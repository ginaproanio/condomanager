// app/static/js/app.js - Funciones generales de la app

// Bandera para asegurar que la inicialización solo ocurra una vez.
window.appJsInitialized = window.appJsInitialized || false;

document.addEventListener('DOMContentLoaded', function() {
    // Manejar parámetros URL para login tradicional
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('legacy') === 'true') {
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.method = 'POST';
            loginForm.action = '/login';
        }
    }

    // Si el script ya se ejecutó, no hacer nada más.
    if (window.appJsInitialized) {
        console.warn('WARN: app.js ya fue inicializado. Omitiendo re-inicialización.');
        return;
    }
    window.appJsInitialized = true;

    // Inicializar tooltips de Bootstrap
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
    
    // Auto-ocultar alerts después de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
    
    console.log('✅ App.js cargado correctamente');
});