/**
 * auth.js - Lógica de autenticación del lado del cliente.
 * Se ejecuta cuando el DOM está completamente cargado.
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('FLOW: DOMContentLoaded en auth.js iniciado. URL actual:', window.location.href);

    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        console.log('FLOW: Formulario de login encontrado. Adjuntando listener de "submit".');
        loginForm.addEventListener('submit', handleLogin);
    } else {
        // Esto es normal en páginas que no son la de login. No es un error.
        console.log('INFO: Formulario "login-form" no encontrado en esta página. Se omite el listener de login.');
    }
});

/**
 * Maneja el envío del formulario de login.
 * Previene el envío por defecto, llama a la API y maneja la respuesta.
 * @param {Event} e - El evento de submit del formulario.
 */
async function handleLogin(e) {
    // 1. Prevenir que la página se recargue
    e.preventDefault();
    console.log('FLOW: handleLogin() - Submit interceptado, previniendo recarga.');

    // 2. Obtener los datos del formulario
    const formData = new FormData(e.target);
    const data = {
        email: formData.get('email'),
        password: formData.get('password')
    };

    // 3. Enviar la petición a la API
    try {
        console.log('FLOW: handleLogin() - Enviando solicitud a /api/auth/login con email:', data.email);
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        console.log('FLOW: handleLogin() - Respuesta recibida de /api/auth/login (status, ok):', response.status, response.ok);

        // 4. Procesar la respuesta
        const responseData = await response.json();

        // Aceptamos 'success' y 'warning' como logins válidos (warning = admin sin condominio asignado)
        if (response.ok && (responseData.status === 'success' || responseData.status === 'warning')) {
            if (responseData.status === 'warning') {
                alert(`⚠️ Aviso: ${responseData.message}`);
            }
            
            // ÉXITO: El backend validó las credenciales
            console.log('FLOW: handleLogin() - Login exitoso. Redirigiendo a:', responseData.redirect_url);
            // El backend ya estableció la cookie JWT, ahora solo redirigimos.
            window.location.href = responseData.redirect_url;
        } else {
            // ERROR CONTROLADO: El backend respondió con un error (ej. 401 Credenciales incorrectas)
            const errorMessage = responseData.error || 'Error desconocido durante el login.';
            console.warn('WARN: handleLogin() - Login fallido:', errorMessage);
            alert(`❌ Error de Login: ${errorMessage}`);
        }
    } catch (error) {
        // ERROR DE RED: El servidor no respondió (caído, CORS, etc.)
        console.error('ERROR: handleLogin() - Error de conexión:', error);
        alert('❌ Error de Conexión: No se pudo comunicar con el servidor.');
    }
}