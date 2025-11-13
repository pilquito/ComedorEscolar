// Main JavaScript file for cafeteria management system

// Global functions and utilities
window.CafeteriaApp = {
    // API base URL
    apiBase: '/api',
    
    // Show loading state for buttons
    setButtonLoading: function(button, loading = true) {
        if (loading) {
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Cargando...';
            button.disabled = true;
        } else {
            button.innerHTML = button.dataset.originalText || button.innerHTML;
            button.disabled = false;
        }
    },
    
    // Show toast notifications
    showToast: function(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toastId = 'toast-' + Date.now();
        const toastHTML = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <i class="fas fa-${this.getToastIcon(type)} me-2 text-${type}"></i>
                    <strong class="me-auto">Comedor Escolar</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        // Show toast
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 5000
        });
        toast.show();
        
        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    },
    
    // Get icon for toast type
    getToastIcon: function(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    },
    
    // Format date for display
    formatDate: function(date) {
        const options = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        };
        return new Date(date).toLocaleDateString('es-ES', options);
    },
    
    // Validate CSV file
    validateCSVFile: function(file) {
        if (!file) {
            return { valid: false, error: 'No se ha seleccionado ningún archivo' };
        }
        
        if (!file.name.toLowerCase().endsWith('.csv')) {
            return { valid: false, error: 'El archivo debe ser de tipo CSV' };
        }
        
        if (file.size > 5 * 1024 * 1024) { // 5MB limit
            return { valid: false, error: 'El archivo es demasiado grande (máximo 5MB)' };
        }
        
        return { valid: true };
    },
    
    // Handle API errors
    handleApiError: function(error, defaultMessage = 'Error de conexión') {
        console.error('API Error:', error);
        let message = defaultMessage;
        
        if (error.response) {
            // Server responded with error
            if (error.response.status === 401) {
                message = 'Sesión expirada. Por favor, inicia sesión nuevamente.';
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else if (error.response.status === 404) {
                message = 'Recurso no encontrado';
            } else if (error.response.status >= 500) {
                message = 'Error del servidor. Inténtalo de nuevo más tarde.';
            }
        }
        
        this.showToast(message, 'danger');
    }
};

// Initialize tooltips when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
    
    // Add confirmation to destructive actions
    const destructiveButtons = document.querySelectorAll('[data-confirm]');
    destructiveButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.dataset.confirm || '¿Estás seguro?';
            if (!confirm(message)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+R or F5 - Refresh page
    if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
        // Allow default refresh behavior
        return;
    }
    
    // Escape - Close modals
    if (e.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        });
    }
    
    // Ctrl+S - Prevent default save behavior
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        CafeteriaApp.showToast('Los cambios se guardan automáticamente', 'info');
    }
});

// Handle offline/online status
window.addEventListener('online', function() {
    CafeteriaApp.showToast('Conexión restaurada', 'success');
});

window.addEventListener('offline', function() {
    CafeteriaApp.showToast('Sin conexión a internet', 'warning');
});

// Export for global use
window.App = CafeteriaApp;
