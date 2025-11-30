Plan de Consolidación y Sincronización
Objetivo: Asegurar que el 100% de la documentación y el código reflejen la arquitectura "Path-Based" de forma coherente y sin contradicciones, eliminando toda la "contaminación" de arquitecturas pasadas.

Fase 1: Cimientos Arquitectónicos (Documentación Core)
Estado: ✅ COMPLETADO

Esta fase consistió en reescribir la "Constitución" del proyecto. Ya hemos auditado y corregido los documentos que definen la arquitectura, las reglas y los permisos.

00_CONVENCIONES.md: ✅ Alineado. Reglas de g.condominium y environment establecidas.
01_INDICE.md: ✅ Alineado. Estructura del proyecto actualizada.
02_ARQUITECTURA.md: ✅ Alineado. Estrategia "Path-Based" como única fuente de verdad.
README.md: ✅ Alineado. Eliminadas las referencias a subdominios y esquemas separados.
03_DATABASE.md: ✅ Alineado. Unificado para reflejar el esquema compartido.
04_API.md: ✅ Alineado. Endpoints actualizados al formato /<tenant_slug>/....
05_INSTALACION.md: ✅ Alineado. Eliminadas instrucciones de bases de datos separadas.
06_DEPLOYMENT.md: ✅ Alineado. Centrado 100% en Railway y el proceso de tenant administrativo.
07_REGLAS_NEGOCIO.md: ✅ Alineado. Lógica de módulos actualizada.
08_ROLES_Y_PERMISOS.md: ✅ Alineado. Rutas y filosofía de roles corregidas. Aislamiento del sandbox formalizado.
Fase 2: Sincronización del Código (Frontend - Templates)
Estado: 🚧 EN PROGRESO

Esta es la fase actual. Estamos aplicando las reglas de la Fase 1 al código que el usuario ve y con el que interactúa. El objetivo es encontrar y eliminar enlaces rotos, variables obsoletas y lógica de UI inconsistente.

app/templates/base.html: ✅ COMPLETADO.

Acción: Corregida la navegación principal (navbar) para usar url_for_tenant. Centralizada la lógica de mensajes flash.
Resultado: Esqueleto de la UI robusto y consistente.
app/templates/auth/login.html: ✅ COMPLETADO.

Acción: Eliminada la lógica de mensajes "contaminada" y verificada la implementación de seguridad CSRF.
Resultado: Puerta de entrada a la plataforma limpia y segura.
app/templates/auth/registro.html: 🔲 PENDIENTE.

Análisis Siguiente: Verificar que, al igual que login.html, no contenga lógica de mensajes duplicada y que sus enlaces (¿Ya tienes cuenta?) sean correctos.
app/templates/home.html: 🔲 PENDIENTE.

Análisis: Auditar los "Call to Action" (Regístrese Ahora, Solicite una Demo) para asegurar que apunten a las rutas correctas.
Auditoría de Paneles Principales: 🔲 PENDIENTE.

app/templates/admin/: Revisar todos los templates de este directorio en busca de url_for que deban ser url_for_tenant.
app/templates/master/: Verificar que la navegación interna del panel del MASTER es correcta.
app/templates/user/: Asegurar que el dashboard del usuario final no tenga enlaces rotos.
Fase 3: Auditoría Final y Limpieza
Estado: 🔲 PENDIENTE

Una vez que la documentación y el frontend estén sincronizados, realizaremos una última pasada para asegurar la coherencia total y eliminar archivos que ya no tienen sentido.

Verificación de seed_initial_data.py: ✅ COMPLETADO.

Acción: Se auditó y se confirmó que el script ya implementa correctamente la arquitectura de roles, tenants y módulos, incluyendo la creación del sandbox con el environment correcto. No requiere cambios.
Verificación de Procfile: 🔲 PENDIENTE.

Análisis: Confirmar que el comando flask db upgrade && gunicorn run:app es el adecuado para el ciclo de vida del despliegue en Railway.
Eliminación de Archivos Obsoletos: 🔲 PENDIENTE.

Análisis: Buscar y proponer la eliminación de archivos que ya no son relevantes (ej. app/tenant.py si aún existe, scripts .bat, etc.).
Este plan nos da una estructura clara. Propongo que continuemos ejecutando la Fase 2, empezando por el punto 3: app/templates/auth/registro.html.