// Function to handle file downloads - defined in global scope
function downloadResults(csvData, filterExisting = false, format = 'csv') {
    // Split CSV into rows and process
    const rows = csvData.split('\n');
    const header = rows[0];
    const dataRows = rows.slice(1).filter(row => row.trim()); // Remove empty rows
    
    let content = '';
    let mimeType = '';
    let fileName = '';
    
    if (format === 'csv') {
        let filteredData = [header];
        // Process each data row for CSV
        for (const row of dataRows) {
            const columns = row.split(',');
            // Check if we should include this row (all rows or only existing)
            if (!filterExisting || columns[2].trim() === 'true') {
                filteredData.push(row);
            }
        }
        content = filteredData.join('\n');
        mimeType = 'text/csv';
        fileName = 'validation_results.csv';
    } else if (format === 'txt') {
        // For TXT, only include email addresses
        const emailAddresses = dataRows.map(row => row.split(',')[0]) // First column is email
            .filter(email => {
                if (!filterExisting) return true;
                const row = dataRows.find(r => r.startsWith(email + ','));
                return row && row.split(',')[2].trim() === 'true'; // Check 'Exists' column
            });
        content = emailAddresses.join('\n');
        mimeType = 'text/plain';
        fileName = 'email_addresses.txt';
    }
    
    // Create and trigger download
    const blob = new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

document.addEventListener('DOMContentLoaded', function() {

    const singleEmailForm = document.getElementById('singleEmailForm');
    const bulkEmailForm = document.getElementById('bulkEmailForm');
    const resultsSection = document.getElementById('resultsSection');
    const validationResults = document.getElementById('validationResults');
    const downloadButtonContainer = document.getElementById('downloadButtonContainer');

    function displayResults(results, showDownload = false, csvData = null) {
        resultsSection.style.display = 'block';
        
        let resultsHtml = `
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Email</th>
                            <th>Valid Format</th>
                            <th>Exists</th>
                            <th>Message</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        for (const [email, result] of Object.entries(results)) {
            resultsHtml += `
                <tr>
                    <td>${email}</td>
                    <td>${result.valid ? '<span class="text-success">Yes</span>' : '<span class="text-danger">No</span>'}</td>
                    <td>${result.exists ? '<span class="text-success">Yes</span>' : '<span class="text-danger">No</span>'}</td>
                    <td>${result.message}</td>
                </tr>
            `;
        }
        
        resultsHtml += `
                    </tbody>
                </table>
            </div>
        `;
        
        validationResults.innerHTML = resultsHtml;
        
        // Update download button
        if (showDownload && csvData) {
            // Store CSV data in a global variable
            window.currentCsvData = csvData;
            downloadButtonContainer.innerHTML = `
                <div class="d-flex align-items-center gap-3">
                    <div class="form-check">
                        <input type="checkbox" class="form-check-input" id="filterExisting">
                        <label class="form-check-label" for="filterExisting">Export only existing emails</label>
                    </div>
                    <div class="btn-group">
                        <button class="btn btn-primary" onclick="downloadResults(window.currentCsvData, document.getElementById('filterExisting').checked, 'csv')">
                            <i class="fas fa-file-csv"></i> Download CSV
                        </button>
                        <button class="btn btn-secondary" onclick="downloadResults(window.currentCsvData, document.getElementById('filterExisting').checked, 'txt')">
                            <i class="fas fa-file-alt"></i> Download TXT
                        </button>
                    </div>
                </div>
            `;
        } else {
            downloadButtonContainer.innerHTML = '';
        }
    }

    singleEmailForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const emails = document.getElementById('email').value.split('\n').filter(email => email.trim());
        
        if (emails.length === 0) {
            validationResults.innerHTML = '<div class="alert alert-warning">Please enter at least one email address</div>';
            resultsSection.style.display = 'block';
            return;
        }
        
        validationResults.innerHTML = '<div class="alert alert-info">Validating...</div>';
        resultsSection.style.display = 'block';
        
        try {
            const formData = new FormData();
            formData.append('emails', JSON.stringify(emails));
            
            const response = await fetch('/validate', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            validationResults.innerHTML = `
                <p>Total emails processed: ${data.total}</p>
            `;
            displayResults(data.results, true, data.csv_data);
        } catch (error) {
            validationResults.innerHTML = `
                <div class="alert alert-danger">
                    Error occurred during validation: ${error.message}
                </div>
            `;
        }
    });

    bulkEmailForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const file = document.getElementById('file').files[0];
        const progressBar = document.getElementById('validationProgress');
        const progressBarInner = progressBar.querySelector('.progress-bar');
        
        validationResults.innerHTML = '<div class="alert alert-info">Processing...</div>';
        resultsSection.style.display = 'block';
        progressBar.classList.remove('d-none');
        progressBarInner.style.width = '0%';
        progressBarInner.textContent = '0%';
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/validate_bulk', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Validation failed');
            }
            
            const data = await response.json();
            validationResults.innerHTML += `
                <p>Total emails processed: ${data.total}</p>
                <p>Filtered results: ${data.filtered}</p>
            `;
            
            displayResults(data.results, true, data.csv_data);
        } catch (error) {
            validationResults.innerHTML = `
                <div class="alert alert-danger">
                    Error occurred during validation: ${error.message}
                </div>
            `;
        }
    });
});
