# Documentación API

> **Implementación Inicial**: API implementada y validada con "Punta Blanca",
> diseñada para soportar múltiples condominios mediante headers específicos.

## 1. Autenticación
Header requerido para identificar el condominio:
```http
X-Condominio-ID: {identificador_condominio}
```

## 2. Endpoints Principales

### 2.1 Unidades
```http
GET /unidades/
POST /unidades/
GET /unidades/{id}
PUT /unidades/{id}
DELETE /unidades/{id}
```

### 2.2 Usuarios
```http
GET /usuarios/
POST /usuarios/
GET /usuarios/{id}
PUT /usuarios/{id}
DELETE /usuarios/{id}
```

### 2.3 Pagos
```http
GET /pagos/
POST /pagos/
GET /pagos/{id}
```

## Endpoints de Búsqueda

### GET /api/search
Búsqueda en tiempo real con las siguientes restricciones:
- Requiere mínimo 3 caracteres
- Retorna máximo 20 resultados
- Implementa debounce de 500ms (frontend)
- Resultados cacheados por 5 minutos

#### Parámetros
- q: término de búsqueda (string, min: 3 caracteres)
- type: tipo de búsqueda (opcional)

#### Respuesta
```json
{
    "results": [...],
    "count": 20,
    "cached": true|false
}
```

## 3. Respuestas
### 3.1 Formato Estándar
```json
{
    "status": "success|error",
    "data": {},
    "message": "Descripción",
    "condominio": "identificador_condominio"
}
```

## 4. Ejemplos

### Actual (Punta Blanca)
```http
GET https://gestion.puntablancaecuador.com/api/v1/unidades
Authorization: Bearer {token}
X-Condominio-ID: puntablanca
```

### Formato Futuro
```http
GET https://gestion.{condominio}.com/api/v1/unidades
Authorization: Bearer {token}
X-Condominio-ID: {identificador_condominio}
```

3. `docs/11_MONITORING.md`:
<augment_code_snippet path="docs/11_MONITORING.md" mode="EDIT">
```markdown
# Monitoreo del Sistema

## 1. Logs por Condominio

### 1.1 Aplicación
```
/home/usuario/condominios/{nombre_condominio}/logs/
├── app.log
├── error.log
├── access.log
└── celery.log
```

### 1.2 Nginx
```
/var/log/nginx/
├── puntablanca_access.log
├── puntablanca_error.log
└── [nuevo_condominio]_*.log
```

## 2. Métricas
### 2.1 Sistema
- CPU por condominio
- Memoria por condominio
- Almacenamiento
- Tráfico de red

### 2.2 Aplicación
- Tiempo de respuesta
- Usuarios activos
- Errores por condominio
- Transacciones por minuto

## 3. Alertas
### 3.1 Configuración por Condominio
```yaml
alertas:
  {nombre_condominio}:
    cpu_threshold: 80
    memory_threshold: 90
    error_rate: 5
    response_time: 2000
```

## 4. Dashboard
- URL: https://monitor.{nombre_condominio}.com
- Acceso: Administradores del condominio
```

4. Actualizar `docs/CHANGELOG.md`:
<augment_code_snippet path="docs/CHANGELOG.md" mode="EDIT">
```markdown
# Changelog

## [1.1.0] - 2024-03-XX

### Añadido
- Soporte multi-condominio
- Separación de bases de datos por condominio
- Templates configurables por condominio
- Sistema de respaldos independiente
- Monitoreo específico por condominio

### Modificado
- Arquitectura para soportar múltiples instancias
- Sistema de logs separado por condominio
- Configuración de Nginx y Supervisor

### Optimizado
- Rendimiento en consultas multi-tenant
- Uso de recursos por condominio
- Sistema de caché compartido

## [1.0.0] - 2024-03-XX
[contenido anterior...]
```

5. `docs/ROADMAP.md`:
<augment_code_snippet path="docs/ROADMAP.md" mode="EDIT">
```markdown
# Roadmap

## Fase 1: MVP Multi-Condominio (Actual)
- [x] Implementación Punta Blanca
- [x] Arquitectura multi-tenant
- [x] Sistema de respaldos por condominio

## Fase 2: Escalabilidad (Q2 2024)
- [ ] Panel de administración multi-condominio
- [ ] API centralizada con routing por condominio
- [ ] Sistema de métricas unificado
- [ ] Automatización de despliegue

## Fase 3: Expansión (Q3 2024)
- [ ] Templates específicos por tipo de condominio
- [ ] Marketplace de módulos
- [ ] Sistema de facturación por condominio
- [ ] Integración con más proveedores de pago
```

Estos cambios:
1. Establecen una estructura clara para múltiples condominios
2. Documentan procesos específicos por condominio
3. Facilitan la escalabilidad futura
4. Mantienen separación de recursos y configuraciones

¿Necesitas que profundice en algún aspecto específico de estos documentos?
