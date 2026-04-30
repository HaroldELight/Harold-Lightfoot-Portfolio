// Main application JavaScript for Email Bot

// Global variables
let currentSessionId = '';

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            if (alert.classList.contains('show')) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        });
    }, 5000);
});

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('main .container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

function showLoading(button, originalText = null) {
    if (!originalText) {
        originalText = button.innerHTML;
    }
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    button.disabled = true;
    return originalText;
}

function hideLoading(button, originalText) {
    button.innerHTML = originalText;
    button.disabled = false;
}

function formatDateTime(dateString) {
    if (!dateString) return 'No date';
    
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatDate(dateString) {
    if (!dateString) return 'No date';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function truncateText(text, maxLength = 100) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

// API helper functions
function makeRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    return fetch(url, finalOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

// Session management
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function getCurrentSessionId() {
    if (!currentSessionId) {
        currentSessionId = generateSessionId();
    }
    return currentSessionId;
}

// Email utilities
function markAsRead(emailId) {
    return makeRequest(`/api/mark_read/${emailId}`, {
        method: 'POST'
    });
}

function starEmail(emailId) {
    return makeRequest(`/api/star/${emailId}`, {
        method: 'POST'
    });
}

function unstarEmail(emailId) {
    return makeRequest(`/api/unstar/${emailId}`, {
        method: 'POST'
    });
}

// Calendar utilities
function formatEventTime(event) {
    if (event.start.dateTime) {
        const start = new Date(event.start.dateTime);
        const end = new Date(event.end.dateTime);
        return `${formatDateTime(start)} - ${formatDateTime(end)}`;
    } else {
        return `All day - ${formatDate(event.start.date)}`;
    }
}

// Search utilities
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Auto-refresh functionality
function setupAutoRefresh(interval = 30000) {
    setInterval(() => {
        const refreshButtons = document.querySelectorAll('[data-auto-refresh]');
        refreshButtons.forEach(button => {
            if (button.offsetParent !== null) { // Only if visible
                button.click();
            }
        });
    }, interval);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + K for quick search
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[name="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals
    if (event.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        });
    }
});

// Export functions for global use
window.EmailBot = {
    showAlert,
    showLoading,
    hideLoading,
    formatDateTime,
    formatDate,
    truncateText,
    makeRequest,
    getCurrentSessionId,
    markAsRead,
    starEmail,
    unstarEmail,
    formatEventTime,
    debounce,
    setupAutoRefresh
};
