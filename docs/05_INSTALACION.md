# Guía de Instalación
Versión: 2.0.0 (Alineado con Arquitectura de Esquema Compartido)

> **Objetivo**: Esta guía describe cómo configurar un entorno de desarrollo en una PC local con el único fin de **modificar el código y subirlo a GitHub**. No es necesario ejecutar la aplicación ni una base de datos localmente, ya que el flujo de trabajo se centra en el despliegue a entornos en la nube (ej. Railway).

## 1. Requisitos del Sistema

### 1.1 Software Base
- Python 3.8+
- Git
- Un editor de código moderno (ej. Visual Studio Code).

## 2. Configuración Local

### 2.1 Clonar Repositorio
```bash
git clone https://github.com/ginaproanio/condomanager.git
cd condomanager
```

### 2.2 Entorno Virtual Python
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2.3 Dependencias Python
```bash
pip install -r requirements.txt
```

### 2.4 Base de Datos
```bash
# Crear base de datos
mysql -u root -p
CREATE DATABASE condominio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Ejecutar migraciones
flask db upgrade
```

### 2.5 Redis
```bash
# Windows: Iniciar servicio Redis
net start Redis

# Linux/Mac
systemctl start redis
```

## 3. Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:

```env
# Base de datos
DB_HOST=localhost
DB_USER=root
DB_PASS=tu_contraseña
DB_NAME=condominio

# Redis
REDIS_URL=redis://localhost:6379

# Seguridad
SECRET_KEY=tu_clave_secreta
JWT_SECRET_KEY=tu_clave_jwt

# APIs Externas
WHATSAPP_API_KEY=tu_clave_whatsapp
PAYPHONE_API_KEY=tu_clave_payphone

# Entorno
FLASK_ENV=development
FLASK_APP=run.py
```

## 4. Pruebas Iniciales

### 4.1 Scripts de Ejecución
El sistema incluye scripts `.bat` para facilitar la ejecución de servicios:

#### 4.1.1 Desarrollo
```batch
# start_dev.bat
@echo off
start "Redis Server" redis-server
start "Celery Worker" celery -A app.celery worker --pool=solo -l info
start "Flask Development" python run.py
```

#### 4.1.2 Producción
```batch
# start_prod.bat
@echo off
start "Redis Server" redis-server
start "Celery Worker" celery -A app.celery worker --pool=solo -l info
start "Gunicorn Server" gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

#### 4.1.3 Monitoreo
```batch
# monitor.bat
@echo off
start "Redis Monitor" redis-cli monitor
start "Celery Monitor" celery -A app.celery flower
```

### 4.2 Verificación de Servicios
```bash
# Iniciar servidor de desarrollo
flask run

# Iniciar worker Celery
celery -A app.celery worker --pool=solo -l info

# Verificar Redis
redis-cli ping
```

### 4.3 Pruebas Automatizadas
```bash
# Ejecutar suite de pruebas
pytest

# Con cobertura
coverage run -m pytest
coverage report
```

## 5. Problemas Comunes

### 5.1 Base de Datos
- Error de conexión: Verificar credenciales en `.env`
- Error de migraciones: Eliminar carpeta `migrations` y reiniciar desde cero

### 5.2 Redis
- Error de conexión: Verificar que el servicio esté corriendo
- Error de permisos: Verificar configuración de firewall

### 5.3 Python
- Conflictos de dependencias: Crear nuevo entorno virtual
- Errores de importación: Verificar PYTHONPATH

## 6. Errores Comunes y Qué No Hacer

### 6.1 Gestión de Dependencias
❌ NO hacer:
- Instalar paquetes globalmente sin entorno virtual
- Mezclar versiones de Python en el mismo proyecto
- Omitir el `requirements.txt` al hacer commit

✅ En su lugar:
- Usar siempre entorno virtual
- Mantener una sola versión de Python (3.8+)
- Actualizar `requirements.txt` con `pip freeze > requirements.txt`

### 6.2 Base de Datos
❌ NO hacer:
- Modificar tablas directamente en producción
- Omitir backups antes de migraciones
- Usar caracteres especiales en nombres de tablas

✅ En su lugar:
- Usar siempre migraciones de Flask
- Realizar backups antes de cada migración
- Seguir convención de nombres (snake_case)

### 6.3 Seguridad
❌ NO hacer:
- Commitear archivos `.env`
- Usar credenciales por defecto
- Desactivar validaciones CSRF

✅ En su lugar:
- Usar `.env.example` como plantilla
- Generar credenciales seguras únicas
- Mantener todas las validaciones de seguridad

### 6.4 Desarrollo
❌ NO hacer:
- Trabajar directamente en `main` o `master`
- Ignorar los logs de error
- Desactivar el modo debug en desarrollo

✅ En su lugar:
- Crear ramas para cada feature/fix
- Revisar y documentar errores
- Usar configuraciones específicas por entorno

### 6.5 Despliegue
❌ NO hacer:
- Desplegar sin probar en staging
- Ignorar las diferencias de entorno
- Omitir la documentación de cambios

✅ En su lugar:
- Probar en entorno similar a producción
- Documentar diferencias entre entornos
- Mantener CHANGELOG actualizado

### 6.6 Scripts de Ejecución
❌ NO hacer:
- Modificar los scripts sin documentar los cambios
- Ejecutar scripts de producción en desarrollo
- Ignorar los mensajes de error en las ventanas de comando

✅ En su lugar:
- Documentar cualquier modificación en los scripts
- Usar los scripts correspondientes al entorno (dev/prod)
- Revisar todas las ventanas de comando para detectar errores
- Mantener una copia de respaldo de los scripts originales

## 7. Siguiente Paso
Una vez completada la instalación, consultar:
- [Manual de Usuario](01_MANUAL_USUARIO.md) para uso del sistema
- [Arquitectura](02_ARQUITECTURA.md) para detalles técnicos
- [API](03_API.md) para documentación de endpoints

## 7. Configuración Multi-Condominio

### 7.1 Preparación del Entorno
❌ NO hacer:
- Mezclar datos entre condominios
- Compartir bases de datos
- Usar configuraciones genéricas

✅ En su lugar:
- Crear entornos aislados por condominio
- Mantener bases de datos separadas
- Personalizar configuraciones por condominio

### 7.2 Proceso de Nuevo Condominio
1. Clonar repositorio base
2. Crear nueva base de datos
3. Configurar variables de entorno específicas
4. Personalizar templates según necesidades
5. Configurar dominio y SSL

### 7.3 Ejemplo: Punta Blanca
- Dominio: puntablancaecuador.com
- Gestión: gestion.puntablancaecuador.com
- Tipo: Lotes/Terrenos
- Base de datos: puntablanca_db
