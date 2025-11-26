# 🎯 PLAN DE REFACTOR - PARA INSTRUIR A LA IA

## **SEMANA 1: CIMIENTOS MULTI-TENANT SÓLIDOS**

### **Día 1-2: Middleware Global de Tenant**

**Objetivo:** Ninguna ruta debe resolver tenant manualmente

**Tareas para la IA:**

1. Crear middleware `@app.before_request` que auto-detecte tenant

2. En desarrollo: usar parámetro `?tenant=xxx` o subdominio

3. Establecer `g.condominium` automáticamente

4. Actualizar TODAS las rutas para usar `g.condominium`

### **Día 3-4: Query Base Segura**

**Objetivo:** Ninguna query pueda olvidar el filtro de tenant

**Tareas para la IA:**

1. Crear `TenantQuery` que auto-filtre por `condominium_id`

2. Hacer que todos los modelos hereden de esta query base

3. Eliminar `filter_by(condominium_id=...)` manuales existentes

### **Día 5: Validación**

**Objetivo:** Verificar que no hay data leaks

**Tareas para la IA:**

1. Crear tests que verifiquen aislamiento entre tenants

2. Probar que usuario de tenant A no ve datos de tenant B

---

## **SEMANA 2: SEGURIDAD BÁSICA**

### **Día 1-2: CSRF + Rate Limiting**

**Tareas para la IA:**

1. Activar `JWT_COOKIE_CSRF_PROTECT = True`

2. Agregar `@limiter.limit()` a login, pagos, registros

3. Configurar límites por IP y por usuario

### **Día 3-4: Validación Backend**

**Tareas para la IA:**

1. Revisar TODOS los endpoints y agregar decoradores:

   - `@login_required`

   - `@admin_required` 

   - `@module_required`

2. Eliminar validaciones solo en frontend

### **Día 5: Entornos**

**Tareas para la IA:**

1. Agregar columna `environment` a Condominium

2. Crear tenants: `sandbox` (internal), `demo-1`, `demo-2`

3. Middleware que bloquee operaciones reales en demo

---

## **SEMANA 3: ARQUITECTURA LIMPIA**

### **Día 1-3: Servicios**

**Tareas para la IA:**

1. Mover lógica de negocio de routes/ a services/

2. Crear:

   - `PaymentService`

   - `DocumentService` 

   - `UserService`

   - `NotificationService`

### **Día 4-5: Manejo de Errores**

**Tareas para la IA:**

1. Crear error handlers globales

2. Logs estructurados con tenant context

3. Respuestas de error consistentes

---

## **SEMANA 4: TESTING Y VALIDACIÓN**

### **Día 1-3: Tests de Seguridad**

**Tareas para la IA:**

1. Tests de aislamiento multi-tenant

2. Tests de permisos y roles

3. Tests de módulos freemium

### **Día 4-5: Deployment Prep**

**Tareas para la IA:**

1. Health checks

2. Variables de entorno validadas

3. Backup/restore procedures



