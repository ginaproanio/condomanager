# 00. Convenciones y Reglas Críticas del Proyecto

> **Propósito**: Este documento es la **Constitución Técnica** de CondoManager-SaaS. Define las reglas inquebrantables de arquitectura y seguridad, así como las convenciones de estilo.
>
> **REGLA SUPREMA (2025)**:  
> La funcionalidad del sistema siempre tiene prioridad sobre cualquier convención de estilo.  
> Si un cambio por "cumplir convención" rompe algo → se revierte inmediatamente.

---

# ANTIPATRONES Y REGLAS DE SEGURIDAD (ZERO TOLERANCE)

**Cualquier PR que viole esta sección será RECHAZADO automáticamente.**

## 1. PROHIBICIONES ARQUITECTÓNICAS

### 1.1 Multi-Tenancy

| ❌ PROHIBIDO | Por qué NO (Riesgo) | ✅ MANDATORIO |
|-------------|-------------------|--------------|
| **Resolver Tenant manualmente**<br>`tenant = get_tenant()` en cada ruta | **Data Leakage**. Si un dev olvida la línea, expone datos globales. | **Middleware Global**. Usar `g.condominium` inyectado por el middleware `resolve_tenant`. |
| **Queries sin filtro**<br>`User.query.all()` | **Broken Access Control (OWASP A01)**. Expone datos de todos los condominios. | **Filtro Explícito**. `User.query.filter_by(condominium_id=g.condominium.id)`. |
| **Hardcoding de subdominios**<br>`if subdomain == 'sandbox':` | **Vulnerabilidad Arquitectónica**. Dificulta rotación de entornos. | **Entornos Dinámicos**. Usar `g.condominium.environment`. |
| **Queries globales sin filtro de entorno**<br>`db.session.query(func.sum(Payment.amount))` | **Métricas Contaminadas**. Mezcla datos de producción con datos de prueba (`sandbox`, `internal`). | **Filtro de Entorno**. En queries globales (MASTER), filtrar por `environment` para métricas reales (ej. `environment NOT IN ('sandbox', 'internal')`). |
| **Flags booleanos**<br>`is_internal`, `is_demo` | **Mantenimiento Frágil**. Se olvidan en rutas nuevas. | **Enums + Middleware**. Usar ENUM `environment` + validación global. |

### 1.2 Seguridad (OWASP Top 10)

| ❌ PROHIBIDO | Por qué NO (Riesgo) | ✅ MANDATORIO |
|-------------|-------------------|--------------|
| **CSRF Desactivado**<br>`JWT_COOKIE_CSRF_PROTECT = False` | **Fraude**. Permite ejecutar acciones en nombre del usuario. | **CSRF Activado**. Siempre `True` en producción. |
| **Transacciones sin atomicidad**<br>Sin `try/except` + `rollback()` | Pérdida de consistencia en BD. | **Atomicidad**. Bloque `try/except` con `db.session.rollback()`. |
| **SQL Injections**<br>Concatenación de strings en queries. | **OWASP A03**. Robo total de base de datos. | **SQLAlchemy ORM**. Usar parámetros bind del ORM siempre. |

### 1.4 Gestión de Entornos

| ❌ PROHIBIDO | Por qué NO (Riesgo) | ✅ MANDATORIO |
|-------------|-------------------|--------------|
| **Usar 'sandbox' para pruebas de clientes** | **Contaminación**. Datos basura mezclados con contabilidad real. | **Entornos Separados**. Tenants `demo` y `internal` aislados. |
| **Acceso público a tenant interno** | **Exposición de Secretos**. Admin panel expuesto a internet. | **Firewall Lógico**. Middleware bloquea IPs no autorizadas (futuro). |

---

## 2. Convención de Idioma — REGLA REALISTA 2025

| Elemento                        | Idioma permitido         | Justificación                                                                 |
|---------------------------------|--------------------------|-------------------------------------------------------------------------------|
| Código nuevo (2025 en adelante) | 100 % inglés             | Hiring internacional, herramientas, claridad global                           |
| Código existente funcional      | Español permitido        | No romper funcionalidades por estética                                        |
| Refactor de archivo existente   | Migrar a inglés + tests  | Cambio controlado, nunca masivo                                               |
| Columnas y tablas de BD         | Español permitido        | Ecuador: cédula, avalúo municipal, código predial, integración SRI           |
| Rutas URL visibles al usuario   | Español (obligatorio)    | UX Latam: `/registro`, `/dashboard`, `/pagos`, `/aprobar`                     |
| Templates HTML (texto visible)  | Español (obligatorio)    | Experiencia de usuario final                                                  |
| Variables, funciones, clases internas | Inglés preferido (nuevo) | Consistencia técnica                                                          |
| Mensajes de commit              | Inglés, imperativo       | `Add user registration`, `Fix payment webhook`                                |
| Logs técnicos y flash messages  | Inglés                   | Debugging y monitoreo                                                         |

**Ejemplos permitidos y correctos en producción 2025**:
```python
# Modelos (campos legales ecuatorianos)
cedula = db.Column(db.String(20), unique=True)
avaluo_municipal = db.Column(db.Numeric)

# Rutas públicas
@app.route('/registro')
def registro():
    return render_template('public/registro.html')

# Código nuevo
def create_payment_intent(amount: float) -> str: