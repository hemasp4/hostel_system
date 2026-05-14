// QR Scanner functionality
class QRScanner {
    constructor() {
        this.html5QrcodeScanner = null;
        this.scanning = false;
    }

    init(elementId) {
        this.html5QrcodeScanner = new Html5QrcodeScanner(
            elementId,
            { 
                fps: 10, 
                qrbox: {width: 250, height: 250},
                aspectRatio: 1.0
            },
            false
        );
    }

    start(onSuccess, onError) {
        if (this.scanning) return;
        
        this.scanning = true;
        this.html5QrcodeScanner.render((decodedText, decodedResult) => {
            this.handleScanSuccess(decodedText, onSuccess);
        }, (error) => {
            this.handleScanError(error, onError);
        });
    }

    stop() {
        if (!this.scanning) return;
        
        this.scanning = false;
        this.html5QrcodeScanner.clear();
    }

    handleScanSuccess(decodedText, callback) {
        // Stop scanning temporarily
        this.stop();
        
        // Play success sound
        this.playSound('success');
        
        // Send to backend for validation
        fetch('/qr/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrf_token')
            },
            body: JSON.stringify({ qr_code: decodedText })
        })
        .then(response => response.json())
        .then(data => {
            if (callback) callback(data);
            
            // Show result
            this.showResult(data);
            
            // Restart scanner after 3 seconds
            setTimeout(() => {
                this.start(callback);
            }, 3000);
        })
        .catch(error => {
            console.error('Error:', error);
            this.showError('Failed to process QR code');
            setTimeout(() => {
                this.start(callback);
            }, 3000);
        });
    }

    handleScanError(error, callback) {
        // Ignore scan errors (common when no QR code is visible)
        if (callback) callback(error);
    }

    showResult(data) {
        const resultDiv = document.getElementById('scanResult');
        if (!resultDiv) return;

        if (data.success) {
            resultDiv.className = 'alert alert-success';
            resultDiv.innerHTML = `
                <h5>✓ Scan Successful</h5>
                <p><strong>Student:</strong> ${data.student_name}</p>
                <p><strong>Leave Period:</strong> ${data.leave_dates}</p>
                <p>${data.message}</p>
            `;
        } else {
            resultDiv.className = 'alert alert-danger';
            resultDiv.innerHTML = `
                <h5>✗ Scan Failed</h5>
                <p>${data.message}</p>
            `;
        }
    }

    showError(message) {
        const resultDiv = document.getElementById('scanResult');
        if (!resultDiv) return;

        resultDiv.className = 'alert alert-danger';
        resultDiv.innerHTML = `
            <h5>✗ Error</h5>
            <p>${message}</p>
        `;
    }

    playSound(type) {
        // Create and play audio feedback
        const audio = new Audio();
        if (type === 'success') {
            audio.src = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZURE';
        } else {
            audio.src = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZURE';
        }
        audio.play().catch(e => console.log('Audio play failed:', e));
    }
}

// Initialize scanner when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('reader')) {
        const scanner = new QRScanner();
        scanner.init('reader');
        scanner.start();
    }
});
