import dns.resolver
import smtplib
import re
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

def is_valid_email_format(email: str) -> bool:
    """Check if email follows correct format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def verify_domain(domain: str) -> tuple:
    """Verify domain exists and has MX records."""
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return True, str(mx_records[0].exchange)
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return False, "Domain does not exist or has no MX records"

def check_smtp(email: str, domain: str, mx_server: str) -> bool:
    """Verify email existence using SMTP."""
    try:
        with smtplib.SMTP(timeout=10) as smtp:
            smtp.connect(mx_server)
            smtp.helo('test.com')
            smtp.mail('test@test.com')
            code, _ = smtp.rcpt(email)
            return code == 250
    except Exception as e:
        logging.debug(f"SMTP check failed for {email}: {str(e)}")
        return False

def validate_email_address(email: str) -> Dict:
    """Validate a single email address."""
    result = {
        'email': email,
        'valid': False,
        'exists': False,
        'message': ''
    }

    if not is_valid_email_format(email):
        result['message'] = 'Invalid email format'
        return result

    domain = email.split('@')[1]
    domain_valid, mx_server = verify_domain(domain)
    
    if not domain_valid:
        result['message'] = mx_server
        return result

    result['valid'] = True
    
    # Check SMTP
    exists = check_smtp(email, domain, mx_server)
    result['exists'] = exists
    result['message'] = 'Email exists' if exists else 'Email does not exist'
    
    return result

def bulk_validate_emails(emails: List[str], chunk_size: int = 100, max_retries: int = 3) -> Dict:
    """
    Validate multiple email addresses concurrently using chunking for memory efficiency.
    
    Args:
        emails: List of email addresses to validate
        chunk_size: Number of emails to process in each chunk
        max_retries: Maximum number of retry attempts for failed validations
        
    Returns:
        Dictionary containing validation results for each email
    """
    results = {}
    total_chunks = (len(emails) + chunk_size - 1) // chunk_size
    retry_queue = []
    
    def process_email(email: str, attempt: int = 1) -> Dict:
        try:
            time.sleep(0.1)  # Rate limiting
            return validate_email_address(email)
        except Exception as e:
            if attempt < max_retries:
                retry_queue.append((email, attempt + 1))
                return None
            return {
                'valid': False,
                'exists': False,
                'message': f'Error after {attempt} attempts: {str(e)}'
            }
    
    for chunk_idx in range(total_chunks):
        start_idx = chunk_idx * chunk_size
        end_idx = min(start_idx + chunk_size, len(emails))
        chunk = emails[start_idx:end_idx]
        
        # Process current chunk
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_email = {
                executor.submit(process_email, email): email 
                for email in chunk
            }
            for future in future_to_email:
                email = future_to_email[future]
                try:
                    result = future.result()
                    if result is not None:
                        results[email] = result
                except Exception as e:
                    logging.error(f"Error processing {email}: {str(e)}")
                    results[email] = {
                        'valid': False,
                        'exists': False,
                        'message': f'Unexpected error: {str(e)}'
                    }
        
        # Process retry queue for this chunk
        while retry_queue:
            email, attempt = retry_queue.pop(0)
            result = process_email(email, attempt)
            if result is not None:
                results[email] = result
        
        # Log progress
        progress = min(100, int((end_idx / len(emails)) * 100))
        logging.info(f"Batch processing progress: {progress}%")
        
        # Give the system some breathing room between chunks
        if chunk_idx < total_chunks - 1:
            time.sleep(0.5)
    
    return results
