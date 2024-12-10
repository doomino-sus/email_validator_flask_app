import os
import csv
from io import StringIO
import json
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from email_validator import validate_email_address, bulk_validate_emails

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "email_validator_secret_key")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = '/tmp'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate():
    emails_json = request.form.get('emails')
    if not emails_json:
        return jsonify({'error': 'Email addresses are required'}), 400
    
    try:
        emails = json.loads(emails_json)
        results = {}
        for email in emails:
            results[email] = validate_email_address(email)
        
        # Create CSV data with consistent boolean representation
        si = StringIO()
        writer = csv.writer(si)
        writer.writerow(['Email', 'Valid', 'Exists', 'Message'])
        
        for email, result in results.items():
            writer.writerow([
                email,
                'true' if result['valid'] else 'false',
                'true' if result['exists'] else 'false',
                result.get('message', '')
            ])
        
        response_data = {
            'results': results,
            'total': len(emails),
            'filtered': len(results),
            'csv_data': si.getvalue()
        }
        si.close()
        
        return jsonify(response_data)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid email data format'}), 400

@app.route('/validate_bulk', methods=['POST'])
def validate_bulk():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not (file.filename.endswith('.csv') or file.filename.endswith('.txt')):
        return jsonify({'error': 'Only CSV and TXT files are supported'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        with open(filepath, 'r') as f:
            emails = [line.strip() for line in f.readlines() if line.strip()]
        
        if len(emails) > 1000:
            chunk_size = 100
        else:
            chunk_size = len(emails)
        
        results = bulk_validate_emails(emails, chunk_size=chunk_size)
        
        # Prepare results for JSON response
        filtered_results = {
            email: result for email, result in results.items()
        }
        
        # Create CSV data with consistent boolean representation
        si = StringIO()
        writer = csv.writer(si, lineterminator='\n')  # Ensure consistent line endings
        writer.writerow(['Email', 'Valid', 'Exists', 'Message'])
        
        for email, result in filtered_results.items():
            writer.writerow([
                email,
                'true' if result['valid'] else 'false',
                'true' if result['exists'] else 'false',
                result.get('message', '')
            ])
        
        csv_data = si.getvalue()
        si.close()
        
        response_data = {
            'results': filtered_results,
            'total': len(emails),
            'filtered': len(filtered_results),
            'csv_data': csv_data
        }
        
        return jsonify(response_data)
    
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
