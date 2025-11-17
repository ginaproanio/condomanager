// app/static/js/auth.js - Sistema de Autenticación JWT
class AuthManager {
    constructor() {
        this.tokenKey = 'condomanager_jwt_token';
        this.userKey = 'condomanager_user_data';
        this.init();
    }

    init() {
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
        return localStorage.getItem(this.tokenKey);
    }

    // 👤 OBTENER USUARIO
    getUser() {
        const userData = localStorage.getItem(this.userKey);
        return userData ? JSON.parse(userData) : null;
    }

    // 🚪 CERRAR SESIÓN
    logout() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.userKey);
        this.updateUI(null);
        window.location.href = '/login';
    }

    // ✅ VERIFICAR SI ESTÁ AUTENTICADO
    isAuthenticated() {
        return this.getToken() !== null;
    }

    // 🛡️ HEADERS PARA API CON TOKEN
    getAuthHeaders() {
        const token = this.getToken();
        return {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
        };
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
        const token = this.getToken();
        
        if (!token) {
            this.updateUI(null);
            return;
        }

        try {
            // Verificar si el token es válido
            const response = await this.authFetch('/api/auth/me');
            if (response.ok) {
                const data = await response.json();
                this.updateUI(data.user);
            } else {
                this.logout();
            }
        } catch (error) {
            console.error('Error verificando autenticación:', error);
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
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            email: formData.get('email'),
            password: formData.get('password')
        };

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                this.auth.setAuth(result.access_token, result.user);
                alert('✅ Login exitoso!');
                window.location.href = '/dashboard';
            } else {
                alert(`❌ Error: ${result.error}`);
            }
        } catch (error) {
            console.error('❌ Error de conexión:', error); // Cambiado de alert a console.error
            console.error('Detalle del error:', error); // Añadido para más detalle
            // alert('❌ Error de conexión'); // Descomenta si necesitas la alerta de nuevo
            // console.error('Error en login:', error);
        }
    }
}

// 🚀 INICIALIZAR CUANDO EL DOM ESTÉ LISTO
document.addEventListener('DOMContentLoaded', function() {
    window.authManager = new AuthManager();
    window.authForms = new AuthForms(window.authManager);
    
    console.log('✅ Sistema de autenticación cargado');
});