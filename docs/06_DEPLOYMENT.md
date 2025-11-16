# Guía de Deployment
Versión: v1.0.0-beta

> **Implementación Inicial**: Esta guía usa "Punta Blanca" como ejemplo de implementación,
> estableciendo el estándar para futuros condominios.

## 1. Requisitos Previos

### 1.1 Configuración Multi-Condominio
#### Estructura de Dominios
- Sitio principal: `{nombre_condominio}.com`
- Sistema de gestión: `gestion.{nombre_condominio}.com`

#### Ejemplos Implementados
1. Punta Blanca
   - Principal: puntablancaecuador.com
   - Gestión: gestion.puntablancaecuador.com
   - Tipo: Lotes/Terrenos

2. [Futuro Condominio]
   - Principal: {dominio}.com
   - Gestión: gestion.{dominio}.com
   - Tipo: [Departamentos/Casas/etc]

### 1.2 Cuenta y Recursos
- Cuenta activa en Hostinger
- Plan Business o superior recomendado
- Acceso SSH habilitado

### 1.3 Preparación Local
- Código versionado en Git
- Pruebas locales completadas
- Variables de entorno documentadas
- Base de datos respaldada

## 2. Configuración en Hostinger

### 2.1 Panel de Control
1. Acceder al panel de Hostinger
2. Configurar subdominio según plantilla:
   ```
   gestion.{nombre_condominio}.com
   ```
3. Verificar recursos asignados:
   - PHP Version: 8.1+
   - Python: 3.8+
   - Node.js: 18+

### 2.2 Base de Datos
```sql
-- Reemplazar {nombre_condominio} con el nombre específico
CREATE DATABASE {nombre_condominio} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER '{nombre_condominio}_user'@'localhost' IDENTIFIED BY 'contraseña_segura';
GRANT ALL PRIVILEGES ON {nombre_condominio}.* TO '{nombre_condominio}_user'@'localhost';
FLUSH PRIVILEGES;

-- Ejemplo Punta Blanca:
CREATE DATABASE puntablanca CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'puntablanca_user'@'localhost' IDENTIFIED BY 'contraseña_segura';
```

### 2.3 Python y Entorno Virtual
```bash
# Crear directorio específico para cada condominio
mkdir -p /home/usuario/condominios/{nombre_condominio}
cd /home/usuario/condominios/{nombre_condominio}

# Configurar Python
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2.4 Servicios Requeridos
- Redis (compartido o dedicado según necesidad)
- Supervisor (configuración por condominio)
- Nginx (virtual hosts separados)

## 3. Proceso de Deployment

### 3.1 Estructura de Directorios
```
/home/usuario/condominios/
├── puntablanca/
│   ├── venv/
│   ├── app/
│   ├── logs/
│   └── media/
├── [futuro_condominio]/
│   ├── venv/
│   ├── app/
│   ├── logs/
│   └── media/
```

### 3.2 Configuración de Nginx
```nginx
# Template para cada condominio
server {
    listen 80;
    server_name gestion.{nombre_condominio}.com;

    # Logs específicos por condominio
    access_log /var/log/nginx/{nombre_condominio}_access.log;
    error_log /var/log/nginx/{nombre_condominio}_error.log;

    location / {
        proxy_pass http://127.0.0.1:{puerto};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /home/usuario/condominios/{nombre_condominio}/app/static;
    }

    location /media {
        alias /home/usuario/condominios/{nombre_condominio}/app/media;
    }
}
```

### 3.3 Supervisor
```ini
[program:{nombre_condominio}]
command=/home/usuario/condominios/{nombre_condominio}/venv/bin/gunicorn -w 4 -b 127.0.0.1:{puerto} run:app
directory=/home/usuario/condominios/{nombre_condominio}/app
user=usuario
autostart=true
autorestart=true
stderr_logfile=/home/usuario/condominios/{nombre_condominio}/logs/err.log
stdout_logfile=/home/usuario/condominios/{nombre_condominio}/logs/out.log

[program:{nombre_condominio}_celery]
command=/home/usuario/condominios/{nombre_condominio}/venv/bin/celery -A app.celery worker --loglevel=info
directory=/home/usuario/condominios/{nombre_condominio}/app
user=usuario
autostart=true
autorestart=true
stderr_logfile=/home/usuario/condominios/{nombre_condominio}/logs/celery_err.log
stdout_logfile=/home/usuario/condominios/{nombre_condominio}/logs/celery_out.log
```

### 3.4 Variables de Entorno
```env
# Template para cada condominio
FLASK_ENV=production
FLASK_APP=run.py
DB_HOST=localhost
DB_NAME={nombre_condominio}
DB_USER={nombre_condominio}_user
DB_PASS=contraseña_segura
SECRET_KEY=clave_secreta_produccion
DOMAIN=gestion.{nombre_condominio}.com
MAIN_WEBSITE=https://{nombre_condominio}.com
CONDOMINIO_TIPO=[lotes/departamentos/casas]
```

### 3.5 SSL/HTTPS
1. Activar SSL en panel de Hostinger
2. Verificar redirección HTTPS
3. Actualizar configuración de Nginx

## 4. Monitoreo Básico

### 4.1 Logs
```bash
# Aplicación
tail -f /var/log/condominio/err.log
tail -f /var/log/condominio/out.log

# Celery
tail -f /var/log/condominio/celery_err.log
tail -f /var/log/condominio/celery_out.log

# Nginx
tail -f /var/log/nginx/error.log
```

### 4.2 Recursos
- Monitoreo de CPU/RAM
- Espacio en disco
- Conexiones activas

### 4.3 Alertas
- Configurar alertas de uso de recursos
- Monitoreo de disponibilidad
- Notificaciones por email

## 5. Errores Comunes y Qué No Hacer

### 5.1 Seguridad
❌ NO hacer:
- Exponer puertos innecesarios
- Usar contraseñas débiles
- Mantener accesos por defecto

✅ En su lugar:
- Configurar firewall adecuadamente
- Usar contraseñas fuertes y únicas
- Cambiar usuarios y puertos por defecto

### 5.2 Deployment
❌ NO hacer:
- Deployar directamente en producción sin pruebas
- Omitir respaldos previos
- Ignorar los logs durante el proceso

✅ En su lugar:
- Probar en ambiente de staging
- Realizar respaldos completos
- Monitorear logs durante el deployment

### 5.3 Configuración
❌ NO hacer:
- Copiar configuraciones de desarrollo
- Dejar debug mode activado
- Exponer información sensible en logs

✅ En su lugar:
- Usar configuraciones específicas de producción
- Desactivar modo debug
- Configurar niveles de log apropiados

### 5.4 Mantenimiento
❌ NO hacer:
- Ignorar actualizaciones de seguridad
- Dejar logs crecer sin control
- Omitir monitoreo de recursos

✅ En su lugar:
- Mantener sistema actualizado
- Implementar rotación de logs
- Monitorear recursos regularmente

## 6. Verificación Post-Deployment

### 6.1 Checklist
- [ ] Aplicación accesible vía HTTPS
- [ ] Todos los servicios corriendo
- [ ] Logs generándose correctamente
- [ ] Backups configurados
- [ ] Monitoreo activo
- [ ] SSL válido y actualizado

### 6.2 Pruebas
- Funcionalidad core
- Integración con servicios externos
- Rendimiento básico
- Manejo de errores

## 7. Rollback Plan
1. Mantener respaldo del último deployment funcional
2. Documentar pasos específicos de rollback
3. Probar proceso de rollback periódicamente

## 8. Proceso de Nuevo Condominio
1. Crear subdominio en Hostinger
2. Configurar base de datos usando template
3. Crear estructura de directorios
4. Configurar Nginx usando template
5. Configurar Supervisor usando template
6. Configurar variables de entorno
7. Desplegar aplicación
8. Verificar checklist

## 9. Referencias
- [Manual de Usuario](01_MANUAL_USUARIO.md)
- [Arquitectura](02_ARQUITECTURA.md)
- [Monitoreo](11_MONITORING.md)
