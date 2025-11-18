# Guía de Deployment
Versión: 2.0.0 (Alineado con Arquitectura de Esquema Compartido)

> Esta guía describe el despliegue de la aplicación en una plataforma como **Railway**, siguiendo una arquitectura de **esquema compartido** y un flujo de trabajo **GitOps**, donde los cambios en el repositorio de GitHub disparan los despliegues.

## 1. Requisitos Previos

- **Plataforma**: Una cuenta en Railway.
- **Repositorio**: El código del proyecto alojado en GitHub y conectado a tu proyecto de Railway.
- **Dominio**: Un dominio personalizado (ej. `condomanager.com`) configurado en Railway.

## 2. Configuración en Railway
 
### 2.1 Servicios
Dentro de tu proyecto de Railway, necesitas dos servicios principales:
1.  **Aplicación Web (Web App)**: Conectada a tu repositorio de GitHub. Railway detectará el `Procfile` y sabrá cómo ejecutar la aplicación.
2.  **Base de Datos (PostgreSQL)**: Un servicio de base de datos de PostgreSQL. Railway proporcionará automáticamente la URL de conexión (`DATABASE_URL`).

### 2.2 Variables de Entorno
En la configuración de tu servicio de aplicación en Railway, define las siguientes variables:
```env
FLASK_ENV=production
SQLALCHEMY_DATABASE_URI=${{PostgreSQL.DATABASE_URL}} # Railway inyecta esta variable
SECRET_KEY=clave_secreta_generada_para_produccion # Usar el generador de secretos de Railway
JWT_SECRET_KEY=clave_jwt_generada_para_produccion # Usar el generador de secretos de Railway
MASTER_EMAIL=maestro@tudominio.com
MASTER_PASSWORD=una_contraseña_muy_fuerte_y_segura
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
