    document.addEventListener('DOMContentLoaded', function () {
        // Initialize Bootstrap Tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        // Initialize Bootstrap Toast messages
        var toastElements = document.querySelectorAll('.toast');
        toastElements.forEach(function (toastElement) {
            var toast = new bootstrap.Toast(toastElement);
            toast.show();
        });
    });
