// app/static/js/auth.js - Sistema de Autenticación JWT
class AuthManager {
    constructor() {
        this.tokenKey = 'condomanager_jwt_token';
        this.userKey = 'condomanager_user_data';
        this.init();
    }

    init() {
        console.log('FLOW: AuthManager.init() iniciado');
        // Interceptar enlaces para verificar autenticación
        this.setupAuthInterception();
        // Verificar estado de autenticación en carga de página
        this.checkAuthStatus();
    }

    // 🔐 GUARDAR TOKEN Y USUARIO
    setAuth(token, user) {
        localStorage.setItem(this.tokenKey, token);
        localStorage.setItem(this.userKey, JSON.stringify(user));
        this.updateUI(user);
    }

    // 🔓 OBTENER TOKEN
    getToken() {
        const token = localStorage.getItem(this.tokenKey);
        return token;
    }

    // 👤 OBTENER USUARIO
    getUser() {
        const userData = localStorage.getItem(this.userKey);
        const user = userData ? JSON.parse(userData) : null;
        return user;
    }

    // 🚪 CERRAR SESIÓN
    logout() {
        console.log('FLOW: logout() - Función llamada.');
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
        return isAuthenticated;
    }

    // 🛡️ HEADERS PARA API CON TOKEN
    getAuthHeaders() {
        const token = this.getToken();
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
        };
        return headers;
    }

    // 📞 LLAMADA API AUTENTICADA
    async authFetch(url, options = {}) {
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
            
            // Si token expiró, redirigir a login
            if (response.status === 401) {
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
        const loginBtn = document.getElementById('login-btn');
        const logoutBtn = document.getElementById('logout-btn');
        const userInfo = document.getElementById('user-info');
        const userName = document.getElementById('user-name');
        const registerBtn = document.getElementById('register-btn');
        const adminLinks = document.querySelectorAll('.admin-only');
        const authRequired = document.querySelectorAll('.auth-required');

        if (user) {
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
        console.log('FLOW: checkAuthStatus() - Función llamada.');
        const token = this.getToken();
        console.log('FLOW: checkAuthStatus() - Token obtenido:', token ? 'existe' : 'null');
        
        if (!token) {
            console.log('FLOW: checkAuthStatus() - No hay token, actualizando UI a no logueado.');
            this.updateUI(null);
            return;
        }

        try {
            // Verificar si el token es válido
            console.log('FLOW: checkAuthStatus() - Llamando a /api/auth/me');
            const response = await this.authFetch('/api/auth/me');
            console.log('FLOW: checkAuthStatus() - Respuesta /api/auth/me (status, ok):', response.status, response.ok);
            if (response.ok) {
                const data = await response.json();
                console.log('FLOW: checkAuthStatus() - /api/auth/me exitoso, datos:', data);
                this.updateUI(data.user);
            } else {
                console.log('FLOW: checkAuthStatus() - /api/auth/me no OK, status:', response.status, ', llamando a logout().');
                this.logout();
            }
        } catch (error) {
            console.error('ERROR: checkAuthStatus() - Error verificando autenticación en /api/auth/me:', error);
            this.logout();
        }
    }

    // 🎯 INTERCEPTAR ENLACES PARA VERIFICAR AUTENTICACIÓN
    setupAuthInterception() {
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
        this.auth = authManager;
        this.setupForms();
    }

    setupForms() {
        // Formulario de registro
        const registerForm = document.getElementById('register-form');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        // Formulario de login JWT
        const loginForm = document.getElementById('login-form');
        console.assert(loginForm, 'ERROR: El formulario de login (id="login-form") no fue encontrado en el DOM.');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Botón de logout
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.auth.logout();
            });
        }
    }

    // 📝 MANEJAR REGISTRO
    async handleRegister(e) {
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
                this.auth.setAuth(result.access_token, result.user);
                alert('✅ Registro exitoso!');
                window.location.href = '/dashboard';
            } else {
                alert(`❌ Error: ${result.error}`);
            }
        } catch (error) {
            alert('❌ Error de conexión');
            console.error('Error en registro:', error);
        }
    }

    // 🔐 MANEJAR LOGIN JWT
    async handleLogin(e) {
        console.log('FLOW: handleLogin() - Función llamada.');
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            email: formData.get('email'),
            password: formData.get('password')
        };

        try {
            console.log('FLOW: handleLogin() - Enviando solicitud a /api/auth/login');
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            console.log('FLOW: handleLogin() - Respuesta de /api/auth/login (status, ok, redirected):', response.status, response.ok, response.redirected);

            if (!response.ok) {
                // Si la respuesta no es 2xx (ej. 401, 403), procesar el error del backend
                const errorResult = await response.json();
                console.log('FLOW: handleLogin() - Login fallido, error:', errorResult);
                alert(`❌ Error: ${errorResult.error || 'Error desconocido del servidor'}`);
            } else if (response.redirected) {
                // Si el backend envió una redirección HTTP (ej. 302), seguirla
                console.log('FLOW: handleLogin() - Redirección del backend detectada a:', response.url);
                window.location.href = response.url;
            } else {
                // Si la respuesta es 200 OK y no es una redirección, procesar el JSON
                const data = await response.json();
                console.log('FLOW: handleLogin() - Login exitoso, datos:', data);
                if (data.status === "success" && data.redirect_url) {
                    // El backend ya estableció la cookie JWT, ahora redirigir al usuario
                    window.location.href = data.redirect_url;
                } else {
                    // Esto no debería ocurrir si el backend envía "success" y "redirect_url"
                    console.warn('ADVERTENCIA: Respuesta exitosa pero inesperada del servidor (no status: success o redirect_url):', data);
                    alert('Error inesperado durante el login (respuesta JSON no conforme).');
                }
            }

        } catch (error) {
            console.error('ERROR: handleLogin() - Error de conexión (catch):', error);
            alert('❌ Error de conexión (frontend)');
        }
    }
}

// 🚀 INICIALIZAR CUANDO EL DOM ESTÉ LISTO
document.addEventListener('DOMContentLoaded', function() {
    console.log('FLOW: DOMContentLoaded en auth.js iniciado. URL actual:', window.location.href);
    window.authManager = new AuthManager();
    window.authForms = new AuthForms(window.authManager);
    
});
                console.warn('ADVERTENCIA: Respuesta inesperada del servidor: no redirigida y no OK.', response);
                alert('Error inesperado durante el login.');
            }

        } catch (error) {
            console.error('ERROR: handleLogin() - Error de conexión (catch):', error);
            alert('❌ Error de conexión (frontend)');
        }
    }
}

// 🚀 INICIALIZAR CUANDO EL DOM ESTÉ LISTO
document.addEventListener('DOMContentLoaded', function() {
    console.log('FLOW: DOMContentLoaded en auth.js iniciado. URL actual:', window.location.href);
    window.authManager = new AuthManager();
    window.authForms = new AuthForms(window.authManager);
    
});