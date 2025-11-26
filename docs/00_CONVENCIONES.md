# 00. Convenciones y Reglas Críticas del Proyecto

> **Propósito**: Este documento es la **Constitución Técnica** de CondoManager-SaaS. Define las reglas inquebrantables de arquitectura y seguridad, así como las convenciones de estilo.
>
> **Cualquier PR que viole la Sección 1 será rechazado automáticamente.**

---

# 🚨 ANTIPATRONES Y REGLAS DE SEGURIDAD (ZERO TOLERANCE)

**Cualquier PR que viole esta sección será RECHAZADO automáticamente.**

## 1. PROHIBICIONES ARQUITECTÓNICAS

### 1.1 Multi-Tenancy

| ❌ PROHIBIDO | Por qué NO (Riesgo) | ✅ MANDATORIO |
|-------------|-------------------|--------------|
| **Resolver Tenant manualmente**<br>`tenant = get_tenant()` en cada ruta | **Data Leakage**. Si un dev olvida la línea, expone datos globales. | **Middleware Global**. Usar `g.condominium` inyectado por middleware. |
| **Queries sin filtro**<br>`User.query.all()` | **Broken Access Control (OWASP A01)**. Expone datos de todos los condominios. | **Filtro Explícito**. `User.query.filter_by(condominium_id=g.condominium.id)`. |
| **Hardcoding de subdominios**<br>`if subdomain == 'sandbox':` | **Vulnerabilidad Arquitectónica**. Dificulta rotación de entornos. | **Entornos Dinámicos**. Usar `g.condominium.environment`. |
| **Flags booleanos**<br>`is_internal`, `is_demo` | **Mantenimiento Frágil**. Se olvidan en rutas nuevas. | **Enums + Middleware**. Usar ENUM `environment` + validación global. |

### 1.2 Seguridad (OWASP Top 10)

| ❌ PROHIBIDO | Por qué NO (Riesgo) | ✅ MANDATORIO |
|-------------|-------------------|--------------|
| **CSRF Desactivado**<br>`JWT_COOKIE_CSRF_PROTECT = False` | **Fraude**. Permite ejecutar acciones en nombre del usuario. | **CSRF Activado**. Siempre `True` en producción. |
| **IDs Secuenciales Públicos**<br>`/users/1`, `/users/2` | **Data Scraping / IDOR**. Permite enumerar recursos. | **UUIDs o Checks**. Validar pertenencia al tenant siempre. |
| **Tokens en LocalStorage** | **XSS Vulnerability**. JS malicioso puede robar el token. | **HttpOnly Cookies**. Almacenamiento seguro del navegador. |
| **Validación solo Frontend** | **Security Bypass**. Se puede saltar con cURL/Postman. | **Decoradores Backend**. `@module_required`, `@admin_required`. |

### 1.3 Base de Datos

| ❌ PROHIBIDO | Por qué NO (Riesgo) | ✅ MANDATORIO |
|-------------|-------------------|--------------|
| **Migraciones sin Backup** | **Pérdida de Datos**. Fallos irreversibles en deploy. | **Snapshot Previo**. Backup automático antes de `flask db upgrade`. |
| **Transacciones sin Rollback** | **Inconsistencia de Datos**. Estados corruptos si falla un paso. | **Atomicidad**. Bloque `try/except` con `db.session.rollback()`. |
| **SQL Injections**<br>Concatenación de strings en queries. | **OWASP A03**. Robo total de base de datos. | **SQLAlchemy ORM**. Usar parámetros bind del ORM siempre. |

### 1.4 Gestión de Entornos

| ❌ PROHIBIDO | Por qué NO (Riesgo) | ✅ MANDATORIO |
|-------------|-------------------|--------------|
| **Usar 'sandbox' para pruebas de clientes** | **Contaminación**. Datos basura mezclados con contabilidad real. | **Entornos Separados**. Tenants `demo` y `internal` aislados. |
| **Acceso público a tenant interno** | **Exposición de Secretos**. Admin panel expuesto a internet. | **Firewall Lógico**. Middleware bloquea IPs no autorizadas (futuro). |

---

## 2. Convención de Idioma (La Regla de Oro)

La regla más importante de estilo es la separación de idiomas entre código y UI.

### 2.1 Código Fuente: **Inglés**
Todo identificador técnico **DEBE** estar en inglés:
- Variables, Funciones, Clases (`class Condominium`, `def create_user`).
- Modelos y Columnas de BD (`db.Column(db.String)`).
- Mensajes de Commit.

### 2.2 Interfaz de Usuario (UI): **Español**
Todo texto visible para el usuario final **DEBE** estar en español:
- HTML Templates (`<h1>Bienvenido</h1>`).
- Mensajes Flash (`flash("Usuario creado", "success")`).

---

## 3. Flujo de Trabajo (Git)

- **Ramas:** `feature/nombre-feature`, `fix/bug-desc`. `main` es sagrada.
- **Commits:** Mensajes en inglés, imperativo (`Add user model`, no `Added user model`).

## 4. Stack Tecnológico Permitido

- **Backend:** Python 3.11+, Flask, SQLAlchemy.
- **Auth:** Flask-JWT-Extended (Cookies HttpOnly).
- **DB:** PostgreSQL (Producción), SQLite (Solo Dev local).
- **Linter:** Flake8 / Black.
