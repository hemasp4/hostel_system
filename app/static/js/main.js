// Main JavaScript file for Hostel Management System

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
});

// Auto-hide alerts after 5 seconds
window.setTimeout(function() {
    $(".alert").fadeTo(500, 0).slideUp(500, function(){
        $(this).remove(); 
    });
}, 5000);

// Date validation for leave requests
function validateDates() {
    const startDate = document.getElementById('start_date');
    const endDate = document.getElementById('end_date');
    
    if (startDate && endDate) {
        startDate.addEventListener('change', function() {
            endDate.min = this.value;
            if (endDate.value && endDate.value < this.value) {
                endDate.value = this.value;
            }
        });
    }
}

// Initialize date validation
validateDates();

// AJAX setup for CSRF token
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrf_token'));
        }
    }
});

// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Leave request preview
function previewLeaveRequest() {
    const reason = document.getElementById('reason').value;
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;
    
    if (reason && startDate && endDate) {
        const preview = `
            <div class="alert alert-info">
                <h5>Leave Request Preview</h5>
                <p><strong>Reason:</strong> ${reason}</p>
                <p><strong>Duration:</strong> ${startDate} to ${endDate}</p>
            </div>
        `;
        document.getElementById('preview-container').innerHTML = preview;
    }
}

function printQRHelper(qrCode, leaveId, studentName, extraDetails = '') {
    let iframe = document.getElementById('printFrame');
    if (!iframe) {
        iframe = document.createElement('iframe');
        iframe.id = 'printFrame';
        iframe.style.position = 'fixed';
        iframe.style.right = '0';
        iframe.style.bottom = '0';
        iframe.style.width = '0';
        iframe.style.height = '0';
        iframe.style.border = '0';
        document.body.appendChild(iframe);
    }
    
    const doc = iframe.contentWindow.document;
    doc.open();
    doc.write(`<html><head><title>Leave Pass QR</title><style>
        body { text-align: center; font-family: sans-serif; padding: 20px; }
        h2 { margin-bottom: 10px; }
        p { margin: 5px 0; }
    </style></head><body>
        <h2>Hostel Leave Pass</h2>
        <img id="printImg" src="${qrCode}" style="max-width:280px; margin: 15px 0;">
        <p><strong>Leave ID:</strong> #${leaveId || 'N/A'}</p>
        ${studentName ? `<p><strong>Student:</strong> ${studentName}</p>` : ''}
        ${extraDetails}
        <p style="margin-top: 15px; color: #555;"><small>Show this QR code at the gate for verification</small></p>
    </body></html>`);
    doc.close();
    
    const img = doc.getElementById('printImg');
    const triggerPrint = () => {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
    };
    
    if (img.complete) {
        triggerPrint();
    } else {
        img.onload = triggerPrint;
    }
}


// Dashboard chart initialization helper
function initDashboardCharts(chartData) {
    // This function can be called from individual dashboard pages
    // to initialize their specific charts
    console.log('Charts initialized with data:', chartData);
}

// Live search functionality
function setupLiveSearch(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (input && table) {
        input.addEventListener('keyup', function() {
            const filter = this.value.toUpperCase();
            const rows = table.getElementsByTagName('tr');
            
            for (let i = 1; i < rows.length; i++) {
                const cells = rows[i].getElementsByTagName('td');
                let found = false;
                
                for (let j = 0; j < cells.length; j++) {
                    if (cells[j].textContent.toUpperCase().indexOf(filter) > -1) {
                        found = true;
                        break;
                    }
                }
                
                rows[i].style.display = found ? '' : 'none';
            }
        });
    }
}

// Export table to CSV with professional cleaning and formatting
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;

    let csv = [];
    const rows = table.querySelectorAll('tr');

    for (let i = 0; i < rows.length; i++) {
        let row = [];
        const cells = rows[i].querySelectorAll('th, td');
        
        for (let j = 0; j < cells.length; j++) {
            // Skip "Actions" column
            const headerText = table.rows[0].cells[j].innerText.toUpperCase();
            if (headerText.includes('ACTIONS')) continue;

            let data = cells[j].innerText;

            // 1. Clean data: Remove extra whitespace, newlines, and non-breaking spaces
            data = data.replace(/\r?\n|\r/g, ' ').trim();
            data = data.replace(/\s+/g, ' ');

            // 2. Escape special characters like long dashes (—) and quotes
            data = data.replace(/—/g, '-'); // Replace EM DASH with simple dash
            data = data.replace(/"/g, '""'); // Escape double quotes for CSV

            // 3. Fix numeric strings (like phone numbers) to prevent scientific notation in Excel
            // We prepend a single quote or wrap in ="..." to force text format
            if (/^\d{7,}$/.test(data)) {
                data = `="${data}"`;
            } else {
                data = `"${data}"`;
            }

            row.push(data);
        }
        if (row.length > 0) {
            csv.push(row.join(','));
        }
    }

    const csvContent = "\ufeff" + csv.join('\n'); // Add UTF-8 BOM for Excel
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'export.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}
