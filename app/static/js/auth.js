// app/static/js/auth.js - Sistema de Autenticación JWT
class AuthManager {
    constructor() {
        console.log('DEBUG: AuthManager constructor iniciado');
        this.tokenKey = 'condomanager_jwt_token';
        this.userKey = 'condomanager_user_data';
        this.init();
    }

    init() {
        console.log('DEBUG: AuthManager.init() iniciado');
        // Interceptar enlaces para verificar autenticación
        this.setupAuthInterception();
        // Verificar estado de autenticación en carga de página
        this.checkAuthStatus();
    }

    // 🔐 GUARDAR TOKEN Y USUARIO
    setAuth(token, user) {
        console.log('DEBUG: setAuth() - Guardando token y usuario', user);
        localStorage.setItem(this.tokenKey, token);
        localStorage.setItem(this.userKey, JSON.stringify(user));
        this.updateUI(user);
    }

    // 🔓 OBTENER TOKEN
    getToken() {
        const token = localStorage.getItem(this.tokenKey);
        console.log('DEBUG: getToken() - Token:', token ? 'exists' : 'null');
        return token;
    }

    // 👤 OBTENER USUARIO
    getUser() {
        const userData = localStorage.getItem(this.userKey);
        const user = userData ? JSON.parse(userData) : null;
        console.log('DEBUG: getUser() - Usuario:', user);
        return user;
    }

    // 🚪 CERRAR SESIÓN
    logout() {
        console.log('DEBUG: logout() - Cerrando sesión');
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.userKey);
        this.updateUI(null);
        // Solo redirigir a login si no estamos ya en la página de login o registro
        if (window.location.pathname !== '/login' && window.location.pathname !== '/registro') {
            window.location.href = '/login';
        }
    }

    // ✅ VERIFICAR SI ESTÁ AUTENTICADO
    isAuthenticated() {
        const isAuthenticated = this.getToken() !== null;
        console.log('DEBUG: isAuthenticated() - Autenticado:', isAuthenticated);
        return isAuthenticated;
    }

    // 🛡️ HEADERS PARA API CON TOKEN
    getAuthHeaders() {
        const token = this.getToken();
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
        };
        console.log('DEBUG: getAuthHeaders() - Cabeceras:', headers);
        return headers;
    }

    // 📞 LLAMADA API AUTENTICADA
    async authFetch(url, options = {}) {
        console.log('DEBUG: authFetch() - URL:', url);
        const headers = this.getAuthHeaders();
        
        const config = {
            ...options,
            headers: {
                ...headers,
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);
            console.log('DEBUG: authFetch() - Respuesta:', response.status, response.ok);
            
            // Si token expiró, redirigir a login
            if (response.status === 401) {
                console.log('DEBUG: authFetch() - Token expirado (401)');
                this.logout();
                throw new Error('Sesión expirada');
            }
            
            return response;
        } catch (error) {
            console.error('Error en authFetch:', error);
            throw error;
        }
    }

    // 🎨 ACTUALIZAR INTERFAZ SEGÚN AUTENTICACIÓN
    updateUI(user) {
        console.log('DEBUG: updateUI() - Usuario para actualizar UI:', user);
        const loginBtn = document.getElementById('login-btn');
        const logoutBtn = document.getElementById('logout-btn');
        const userInfo = document.getElementById('user-info');
        const userName = document.getElementById('user-name');
        const registerBtn = document.getElementById('register-btn');
        const adminLinks = document.querySelectorAll('.admin-only');
        const authRequired = document.querySelectorAll('.auth-required');

        if (user) {
            console.log('DEBUG: updateUI() - Usuario logueado, rol:', user.role);
            // Usuario logueado
            if (loginBtn) loginBtn.style.display = 'none';
            if (registerBtn) registerBtn.style.display = 'none';
            if (logoutBtn) logoutBtn.style.display = 'block';
            if (userInfo) {
                if (userName) userName.textContent = user.name;
                userInfo.style.display = 'block';
            }

            // Mostrar elementos que requieren autenticación
            authRequired.forEach(element => {
                element.style.display = 'block';
            });

            // Mostrar/ocultar enlaces de admin
            adminLinks.forEach(link => {
                link.style.display = (user.role === 'ADMIN' || user.role === 'MASTER') ? 'block' : 'none';
            });
        } else {
            console.log('DEBUG: updateUI() - Usuario no logueado');
            // Usuario no logueado
            if (loginBtn) loginBtn.style.display = 'block';
            if (registerBtn) registerBtn.style.display = 'block';
            if (logoutBtn) logoutBtn.style.display = 'none';
            if (userInfo) userInfo.style.display = 'none';
            
            // Ocultar elementos que requieren autenticación
            authRequired.forEach(element => {
                element.style.display = 'none';
            });
            
            adminLinks.forEach(link => {
                link.style.display = 'none';
            });
        }
    }

    // 🔍 VERIFICAR ESTADO DE AUTENTICACIÓN
    async checkAuthStatus() {
        console.log('DEBUG: checkAuthStatus() iniciado');
        const token = this.getToken();
        console.log('DEBUG: checkAuthStatus() - Token obtenido:', token ? 'exists' : 'null');
        
        if (!token) {
            console.log('DEBUG: checkAuthStatus() - No hay token, actualizando UI a no logueado');
            this.updateUI(null);
            return;
        }

        try {
            // Verificar si el token es válido
            const response = await this.authFetch('/api/auth/me');
            console.log('DEBUG: checkAuthStatus() - Respuesta /api/auth/me:', response.status, response.ok);
            if (response.ok) {
                const data = await response.json();
                console.log('DEBUG: checkAuthStatus() - Datos de usuario desde /api/auth/me:', data);
                this.updateUI(data.user);
            } else {
                console.log('DEBUG: checkAuthStatus() - Respuesta /api/auth/me no OK, cerrando sesión');
                this.logout();
            }
        } catch (error) {
            console.error('Error verificando autenticación en /api/auth/me:', error);
            this.logout();
        }
    }

    // 🎯 INTERCEPTAR ENLACES PARA VERIFICAR AUTENTICACIÓN
    setupAuthInterception() {
        console.log('DEBUG: setupAuthInterception() iniciado');
        document.addEventListener('click', (e) => {
            const target = e.target.closest('a');
            
            if (target && target.classList.contains('auth-required')) {
                e.preventDefault();
                
                if (!this.isAuthenticated()) {
                    alert('Debes iniciar sesión para acceder a esta página');
                    window.location.href = '/login';
                    return;
                }
                
                window.location.href = target.href;
            }
        });
    }
}

// 📝 FUNCIONES DE REGISTRO Y LOGIN
class AuthForms {
    constructor(authManager) {
        console.log('DEBUG: AuthForms constructor iniciado');
        this.auth = authManager;
        this.setupForms();
    }

    setupForms() {
        console.log('DEBUG: AuthForms.setupForms() iniciado');
        // Formulario de registro
        const registerForm = document.getElementById('register-form');
        console.log('DEBUG: registerForm encontrado:', !!registerForm);
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        // Formulario de login JWT
        const loginForm = document.getElementById('login-form');
        console.log('DEBUG: loginForm encontrado:', !!loginForm);
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Botón de logout
        const logoutBtn = document.getElementById('logout-btn');
        console.log('DEBUG: logoutBtn encontrado:', !!logoutBtn);
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.auth.logout();
            });
        }
    }

    // 📝 MANEJAR REGISTRO
    async handleRegister(e) {
        console.log('DEBUG: handleRegister() iniciado');
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            password: formData.get('password')
        };

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                console.log('DEBUG: handleRegister() - Registro exitoso, resultado:', result);
                this.auth.setAuth(result.access_token, result.user);
                alert('✅ Registro exitoso!');
                window.location.href = '/dashboard';
            } else {
                console.log('DEBUG: handleRegister() - Error en registro, resultado:', result);
                alert(`❌ Error: ${result.error}`);
            }
        } catch (error) {
            alert('❌ Error de conexión');
            console.error('Error en registro:', error);
        }
    }

    // 🔐 MANEJAR LOGIN JWT
    async handleLogin(e) {
        console.log('DEBUG: handleLogin() iniciado');
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            email: formData.get('email'),
            password: formData.get('password')
        };

        try {
            const response = await fetch('/api/auth/login', { // CAMBIAR A /api/auth/login
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            console.log('DEBUG: handleLogin() - Raw response object:', response); // AÑADIDO
            console.log('DEBUG: handleLogin() - Solicitud de login enviada, respuesta recibida:', response.status, response.ok);

            // Después de un login exitoso, el backend redirige directamente, no necesitamos procesar JSON aquí.
            // Sin embargo, si la respuesta NO es una redirección, significa que hubo un error del servidor que devuelve JSON.
            if (!response.ok) {
                const errorResult = await response.json();
                console.log('DEBUG: handleLogin() - Login fallido (no OK), error:', errorResult);
                alert(`❌ Error: ${errorResult.error || 'Error desconocido del servidor'}`);
            } else if (response.redirected) {
                console.log('DEBUG: handleLogin() - Redirección del backend detectada:', response.url);
                // El navegador ya seguirá la redirección, no hacemos nada aquí.
            } else {
                console.warn('DEBUG: handleLogin() - Respuesta inesperada del servidor, no redirigida y no OK:', response);
                alert('Error inesperado durante el login.');
            }

        } catch (error) {
            console.error('❌ Error de conexión (catch):', error);
            console.error('Detalle del error (catch):', error);
            alert('❌ Error de conexión (frontend)');
        }
    }
}

// 🚀 INICIALIZAR CUANDO EL DOM ESTÉ LISTO
document.addEventListener('DOMContentLoaded', function() {
    console.log('DEBUG: DOMContentLoaded en auth.js iniciado');
    window.authManager = new AuthManager();
    window.authForms = new AuthForms(window.authManager);
    
    console.log('✅ Sistema de autenticación cargado');
});