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

    // --- AUTO-INYECCIÓN CSRF (Semana 2, Día 1) ---
    // Busca la cookie csrf_access_token e inyecta el input hidden en todos los forms POST
    // Esto permite que Flask-JWT-Extended funcione con formularios HTML normales
    const csrfToken = getCookie('csrf_access_token');
    if (csrfToken) {
        document.querySelectorAll('form').forEach(form => {
            // Solo inyectar si es POST (o no tiene method, que default es GET pero por si acaso) 
            // y si no tiene ya el campo
            const method = (form.getAttribute('method') || 'GET').toUpperCase();
            if (method === 'POST' && !form.querySelector('input[name="csrf_token"]')) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'csrf_token';
                input.value = csrfToken;
                form.appendChild(input);
                // console.log('🛡️ CSRF token inyectado en formulario:', form.id || 'sin-id');
            }
        });
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
    
    console.log('✅ App.js cargado correctamente');
});
