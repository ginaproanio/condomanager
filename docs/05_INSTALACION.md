# Guía de Instalación
Versión: 3.0.0 (Alineado con la arquitectura "Path-Based")

> **Objetivo**: Esta guía describe cómo configurar un entorno de desarrollo en una PC local con el único fin de **modificar el código y subirlo a GitHub**. No es necesario ejecutar la aplicación ni una base de datos localmente, ya que todas las pruebas se realizan en el ambiente de Railway.

> **Importante**: El proyecto está diseñado para ser ejecutado en un entorno tipo Unix (como el que provee Railway). La ejecución en Windows no está soportada y los scripts `.bat` están obsoletos.

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

### 2.4 Configuración del Editor (VS Code)
Se recomienda instalar las siguientes extensiones para una mejor experiencia de desarrollo:
- `Python` (de Microsoft)
- `Pylance` (de Microsoft)
- `Jinja` (de wholroyd)

## 3. Flujo de Trabajo de Desarrollo
1. **Crear una Rama:** Antes de hacer cualquier cambio, crea una nueva rama desde `main`.
   ```bash
   git checkout -b feature/nombre-de-tu-funcionalidad
   ```
2. **Realizar Cambios:** Modifica el código según sea necesario.
3. **Confirmar Cambios:** Haz commits atómicos y descriptivos.
   ```bash
   git add .
   git commit -m "feat: Añade la funcionalidad X al módulo Y"
   ```
4. **Subir Cambios:** Empuja tu rama a GitHub.
   ```bash
   git push origin feature/nombre-de-tu-funcionalidad
   ```
5. **Crear Pull Request:** En GitHub, abre un Pull Request de tu rama hacia `main`.
6. **Despliegue Automático:** Al hacer merge del Pull Request, Railway desplegará automáticamente los cambios en el entorno de pruebas.

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
