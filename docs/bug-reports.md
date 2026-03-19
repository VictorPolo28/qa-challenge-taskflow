# Bug Reports — TaskFlow

Bugs encontrados mediante exploración de la API (Swagger), pruebas manuales en el frontend y revisión del comportamiento de los endpoints.

---

### BUG-001: API acepta emails con formato inválido al crear usuarios

- **Severidad:** Alta
- **Componente:** API — Usuarios
- **Endpoint:** `POST /api/users`

**Precondiciones:** API activa.

**Pasos para reproducir:**
1. Ejecutar `POST /api/users` con body: `{"username":"tester99","email":"noesunemail","full_name":"Test","role":"member"}`
2. Observar la respuesta.

**Resultado actual:**
```json
HTTP 201 Created
{"id":"...","email":"noesunemail",...}
```

**Resultado esperado:**
HTTP 422 Unprocessable Entity — el campo `email` debe rechazar valores que no tengan formato `user@domain.tld`.

**Evidencia:**
```
POST /api/users
Body: {"username":"bugtest01","email":"noesunemail","full_name":"Test User","role":"member"}
Response: 201 Created — {"id":"abc...","email":"noesunemail",...}
```

**Impacto:** La base de datos puede acumular usuarios con emails inválidos, lo que rompe cualquier flujo futuro de comunicación por correo y dificulta la integridad de datos.

**Sugerencia de fix:** Agregar validación de formato email con regex o con el validador de Pydantic `EmailStr`.

---

### BUG-002: Listado de proyectos muestra proyectos eliminados por defecto

- **Severidad:** Alta
- **Componente:** API — Proyectos
- **Endpoint:** `GET /api/projects`

**Precondiciones:** Existe al menos un proyecto eliminado (status = "deleted").

**Pasos para reproducir:**
1. Crear un proyecto: `POST /api/projects`
2. Eliminarlo: `DELETE /api/projects/{id}`
3. Listar proyectos: `GET /api/projects`

**Resultado actual:**
El proyecto eliminado aparece en la lista con `"status": "deleted"`.

**Resultado esperado:**
`GET /api/projects` sin filtro de estado debe retornar solo proyectos activos y archivados. Los proyectos con `status: "deleted"` solo deben ser visibles con el filtro `?status=deleted`.

**Evidencia:**
```
GET /api/projects
Response: {"projects":[{"id":"...","status":"deleted",...}], "total":3}
```

**Impacto:** Los usuarios ven proyectos que supuestamente eliminaron, generando confusión y datos sucios en el frontend.

**Sugerencia de fix:** Cambiar la query por defecto a `WHERE status != 'deleted'`.

---

### BUG-003: Crear proyecto con owner_id inexistente es aceptado

- **Severidad:** Alta
- **Componente:** API — Proyectos
- **Endpoint:** `POST /api/projects`

**Precondiciones:** API activa.

**Pasos para reproducir:**
1. Ejecutar `POST /api/projects` con `owner_id` de un usuario que no existe.

**Resultado actual:**
```json
HTTP 201 Created — proyecto creado con owner inexistente
```

**Resultado esperado:**
HTTP 404 o 422 — el `owner_id` debe existir en la tabla de usuarios.

**Evidencia:**
```
POST /api/projects
Body: {"name":"Proyecto Huérfano","owner_id":"00000000-0000-0000-0000-000000000099"}
Response: 201 Created
```

**Impacto:** Se crean proyectos sin dueño válido. Si el sistema eventualmente agrega roles o permisos, los proyectos huérfanos rompen la lógica de autorización.

**Sugerencia de fix:** Antes del INSERT, validar que `owner_id` existe en la tabla `users`.

---

### BUG-004: Eliminar proyecto no desvincula ni cancela las tareas asociadas

- **Severidad:** Alta
- **Componente:** API — Proyectos / Tareas
- **Endpoint:** `DELETE /api/projects/{id}`

**Precondiciones:** Proyecto activo con tareas asociadas.

**Pasos para reproducir:**
1. Crear un proyecto y agregarle tareas.
2. Eliminar el proyecto: `DELETE /api/projects/{id}`
3. Consultar: `GET /api/tasks?project_id={id}`

**Resultado actual:**
Las tareas siguen existiendo y siendo accesibles, referenciando un proyecto con `status: "deleted"`. El `total` de estadísticas globales las sigue contando.

**Resultado esperado:**
Al eliminar un proyecto, sus tareas deben ser canceladas en cascada, o la API debe rechazar la eliminación si hay tareas activas.

**Evidencia:**
```
DELETE /api/projects/6d216d4d-...  → 200 OK
GET /api/tasks?project_id=6d216d4d-...  → 200 OK con tareas activas
```

**Impacto:** Las tareas quedan huérfanas, generando inconsistencia en estadísticas, asignaciones y exportaciones.

**Sugerencia de fix:** Implementar soft-delete en cascada para tareas del proyecto eliminado, o validar que no existen tareas activas antes de permitir la eliminación.

---

### BUG-005: Permite crear tareas en proyectos archivados o eliminados

- **Severidad:** Alta
- **Componente:** API — Tareas
- **Endpoint:** `POST /api/tasks`

**Precondiciones:** Proyecto con `status: "archived"` o `status: "deleted"`.

**Pasos para reproducir:**
1. Archivar un proyecto: `PUT /api/projects/{id}` con `{"status":"archived"}`
2. Crear una tarea en ese proyecto: `POST /api/tasks` con `project_id` del proyecto archivado.

**Resultado actual:**
```json
HTTP 201 Created — tarea creada en proyecto inactivo
```

**Resultado esperado:**
HTTP 400 — no debe permitirse agregar tareas a proyectos que no están activos.

**Evidencia:**
```
PUT /api/projects/{id} → {"status":"archived"}  → 200 OK
POST /api/tasks → {project_id: {id}, ...}  → 201 Created
```

**Impacto:** Datos inconsistentes: tareas creadas en proyectos que el negocio considera cerrados. Afecta reportes y métricas.

**Sugerencia de fix:** En el endpoint `POST /api/tasks`, verificar que `project.status == "active"` antes de crear la tarea.

---

### BUG-006: Inyección SQL posible en el parámetro de búsqueda de tareas

- **Severidad:** Crítica
- **Componente:** API — Tareas
- **Endpoint:** `GET /api/tasks?search=`

**Precondiciones:** API activa.

**Pasos para reproducir:**
1. Ejecutar: `GET /api/tasks?search=' OR '1'='1`
2. Observar si retorna resultados no esperados.
3. Probar payload más agresivo: `GET /api/tasks?search='; DROP TABLE tasks; --`

**Resultado actual:**
El parámetro `search` es interpolado directamente en la query SQL sin parametrizar:
```python
conditions.append(f"(title LIKE '%{search}%' OR description LIKE '%{search}%')")
```
Esto permite inyectar SQL arbitrario en la consulta.

**Resultado esperado:**
El parámetro debe ser parametrizado de forma segura:
```python
conditions.append("(title LIKE ? OR description LIKE ?)")
params.extend([f"%{search}%", f"%{search}%"])
```

**Evidencia:**
```
GET /api/tasks?search=' OR '1'='1
Response: lista completa de tareas (inyección exitosa)
```

**Impacto:** **Riesgo de seguridad crítico.** Un atacante puede leer, modificar o eliminar datos de cualquier tabla de la base de datos. Motivo de descarte automático en producción.

**Sugerencia de fix:** Usar parámetros posicionales (`?`) en todas las queries SQLite. Nunca interpolar strings en SQL.

---

### BUG-007: Paginación reporta un `total` incorrecto cuando se aplican filtros

- **Severidad:** Alta
- **Componente:** API — Tareas
- **Endpoint:** `GET /api/tasks` con filtros

**Precondiciones:** Tareas en múltiples proyectos.

**Pasos para reproducir:**
1. Tener 18 tareas en total: 10 en Proyecto A, 8 en Proyecto B.
2. Ejecutar: `GET /api/tasks?project_id={id_proyecto_A}&page=1&page_size=5`

**Resultado actual:**
```json
{"tasks":[...5 tareas...], "total": 18, "total_pages": 4}
```
`total` es el conteo global, no el conteo filtrado.

**Resultado esperado:**
```json
{"tasks":[...5 tareas...], "total": 10, "total_pages": 2}
```

**Evidencia:**
```sql
-- El bug en el código:
total_row = conn.execute("SELECT COUNT(*) as total FROM tasks").fetchone()
-- Debería ser:
total_row = conn.execute(f"SELECT COUNT(*) as total FROM tasks{where}", params).fetchone()
```

**Impacto:** El frontend muestra un número incorrecto de páginas, llevando al usuario a páginas vacías. Los reportes de cantidad de tareas por proyecto son erróneos.

**Sugerencia de fix:** Aplicar las mismas condiciones de filtro al `COUNT(*)` que a la query principal.

---

### BUG-008: Transiciones de estado inválidas son aceptadas

- **Severidad:** Media
- **Componente:** API — Tareas
- **Endpoint:** `PUT /api/tasks/{id}`

**Precondiciones:** Tarea en estado `done` o `cancelled`.

**Pasos para reproducir:**
1. Actualizar tarea a estado `done`: `PUT /api/tasks/{id}` con `{"status":"done"}`
2. Revertir: `PUT /api/tasks/{id}` con `{"status":"todo"}`

**Resultado actual:**
```json
HTTP 200 OK — tarea revertida a "todo"
```

**Resultado esperado:**
HTTP 400 — una tarea completada no puede volver a `todo`. El flujo válido es:
`todo → in_progress → in_review → done`
`cualquier estado → cancelled` (unidireccional)

**Evidencia:**
```
PUT /api/tasks/{id} → {"status":"done"} → 200 OK
PUT /api/tasks/{id} → {"status":"todo"} → 200 OK (bug: debería ser 400)
```

**Impacto:** Integridad del flujo de trabajo comprometida. Las métricas de productividad y los reportes de tareas completadas se vuelven no confiables.

---

### BUG-009: DELETE /api/tasks retorna 200 en lugar de 204

- **Severidad:** Baja
- **Componente:** API — Tareas
- **Endpoint:** `DELETE /api/tasks/{id}`

**Precondiciones:** Tarea existente.

**Pasos para reproducir:**
1. `DELETE /api/tasks/{id}` con ID válido.

**Resultado actual:**
```json
HTTP 200 OK — {"message": "Task deleted"}
```

**Resultado esperado:**
HTTP 204 No Content — conforme a la semántica REST para operaciones DELETE exitosas.

**Impacto:** Bajo impacto funcional, pero viola el estándar REST. Los clientes que validan el status code pueden comportarse de forma inesperada.

---

### BUG-010: Comentario se crea bajo el task_id del body, no el de la URL

- **Severidad:** Alta
- **Componente:** API — Comentarios
- **Endpoint:** `POST /api/tasks/{task_id}/comments`

**Precondiciones:** Dos tareas existentes (Task A y Task B).

**Pasos para reproducir:**
1. Ejecutar `POST /api/tasks/{task_id_A}/comments` con body:
   ```json
   {"task_id": "{task_id_B}", "author_id": "...", "content": "comentario desviado"}
   ```
2. Listar comentarios de Task A: `GET /api/tasks/{task_id_A}/comments`
3. Listar comentarios de Task B: `GET /api/tasks/{task_id_B}/comments`

**Resultado actual:**
El comentario aparece en Task B, no en Task A (donde fue enviado por URL).

**Resultado esperado:**
El `task_id` de la URL debe ser el autoritativo. El campo `task_id` del body debe ignorarse o validarse que coincida con la URL.

**Evidencia:**
```
POST /api/tasks/TASK-A/comments
Body: {"task_id":"TASK-B","author_id":"...","content":"test"}
→ 201 Created con task_id: TASK-B

GET /api/tasks/TASK-A/comments → {"comments":[], "total":0}
GET /api/tasks/TASK-B/comments → {"comments":[{"content":"test"}], "total":1}
```

**Impacto:** Los comentarios pueden desviarse silenciosamente a tareas incorrectas, comprometiendo la trazabilidad y el historial de comunicación del equipo.

**Sugerencia de fix:** En el INSERT, usar siempre `task_id` de la URL path, ignorando el campo del body.

---

### BUG-011: Cálculo de tareas vencidas (`overdue`) es incorrecto

- **Severidad:** Alta
- **Componente:** API — Estadísticas
- **Endpoint:** `GET /api/stats`

**Precondiciones:** Tareas con `due_date` pasada y status ≠ done/cancelled.

**Pasos para reproducir:**
1. Crear tarea con `due_date: "2020-01-01"` y status `todo`.
2. Consultar `GET /api/stats`.

**Resultado actual:**
El conteo `overdue` puede ser incorrecto. La query SQL en el código tiene un error lógico en la construcción condicional del WHERE cuando se pasa `project_id`, causando que la comparación de fechas falle o retorne resultados inesperados.

**Resultado esperado:**
`overdue` debe contar exactamente las tareas con `due_date < hoy` y `status NOT IN ('done', 'cancelled')`.

**Impacto:** Los dashboards de gestión de proyectos muestran métricas de vencimiento incorrectas, afectando la toma de decisiones.

---

### BUG-012: Bulk update no maneja IDs inexistentes — retorna 200 aunque no actualice nada

- **Severidad:** Alta
- **Componente:** API — Operaciones masivas
- **Endpoint:** `POST /api/tasks/bulk-update`

**Precondiciones:** API activa.

**Pasos para reproducir:**
1. Ejecutar bulk-update con IDs que no existen:
   ```json
   {"task_ids":["uuid-falso-1","uuid-falso-2"],"updates":{"status":"done"}}
   ```

**Resultado actual:**
```json
HTTP 200 OK — {"message": "Updated 0 tasks", "updated": 0}
```

**Resultado esperado:**
HTTP 404 o 207 Multi-Status indicando que los IDs no fueron encontrados. Un `updated: 0` con código 200 es ambiguo y puede generar que el cliente asuma que la operación fue exitosa.

**Evidencia:**
```
POST /api/tasks/bulk-update
Body: {"task_ids":["00000000-0000-0000-0000-000000000001"],"updates":{"status":"done"}}
Response: 200 OK {"message":"Updated 0 tasks","updated":0}
```

**Impacto:** Las actualizaciones masivas silenciosas pueden causar que el operador crea que las tareas fueron actualizadas cuando en realidad no lo fueron.

---

### BUG-013: Exportación CSV no escapa comas ni comillas en el contenido

- **Severidad:** Alta
- **Componente:** API — Exportación
- **Endpoint:** `GET /api/export/tasks?format=csv`

**Precondiciones:** Tarea con coma o comilla en el título o descripción.

**Pasos para reproducir:**
1. Crear tarea: `POST /api/tasks` con `title: "Tarea, con coma y \"comillas\""`.
2. Exportar: `GET /api/export/tasks?format=csv`
3. Abrir el CSV resultante en Excel o Google Sheets.

**Resultado actual:**
Las comas dentro del contenido rompen el formato CSV — los campos quedan desalineados.

```
id,title,...
abc...,Tarea, con coma y "comillas",...
```
Excel interpreta `Tarea` como una columna y ` con coma...` como otra.

**Resultado esperado:**
Los campos que contienen comas o comillas deben ir entre comillas dobles y las comillas internas deben escaparse:
```
abc...,"Tarea, con coma y ""comillas""",...
```

**Impacto:** Los exports de datos están corruptos para cualquier tarea con puntuación en los campos de texto. Reportes descargados por usuarios son inutilizables.

**Sugerencia de fix:** Usar el módulo estándar `csv` de Python en lugar de la interpolación manual de strings.

---

### BUG-014: CORS configurado con `allow_origins=["*"]` y `allow_credentials=True` simultáneamente

- **Severidad:** Alta
- **Componente:** API — Configuración de seguridad
- **Endpoint:** Todos

**Precondiciones:** API activa.

**Pasos para reproducir:**
1. Enviar cualquier request con header `Origin: http://malicious.example.com`.
2. Observar los headers de respuesta.

**Resultado actual:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

**Resultado esperado:**
La combinación `allow_origins=["*"]` con `allow_credentials=True` viola la especificación CORS y es rechazada por los navegadores modernos. En un entorno de producción real, esto debe restringir los orígenes permitidos a la lista explícita de dominios confiables.

**Impacto:** Vulnerabilidad de seguridad que permitiría ataques CSRF desde cualquier origen si se implementara autenticación. Actualmente es un riesgo latente para cuando se agregue auth.

---

### BUG-015: Orden del dropdown de prioridad en el frontend no es consistente

- **Severidad:** Baja
- **Componente:** Frontend — Modal de creación de tarea
- **Pantalla:** Modal "Nueva Tarea"

**Pasos para reproducir:**
1. Hacer clic en "+ Nueva Tarea"
2. Observar las opciones del selector "Prioridad".

**Resultado actual:**
Orden mostrado: `Media, Baja, Alta, Crítica`

**Resultado esperado:**
El orden lógico de menor a mayor sería: `Baja, Media, Alta, Crítica`

**Impacto:** Bajo — genera confusión visual al usuario al no seguir un orden estándar de jerarquía.

---

### BUG-016: Modal de edición de tarea no precarga los datos existentes

- **Severidad:** Alta
- **Componente:** Frontend — Modal de edición
- **Pantalla:** Modal "Editar Tarea"

**Pasos para reproducir:**
1. Hacer clic en el botón "Editar" (ícono lápiz) de una tarea existente.
2. Observar los campos del formulario.

**Resultado actual:**
El formulario aparece completamente vacío — el usuario debe reingresar todos los datos incluso si solo quiere cambiar un campo.

**Resultado esperado:**
El modal debe precargar todos los campos con los valores actuales de la tarea, permitiendo al usuario modificar solo lo que necesita.

**Impacto:** Experiencia de usuario muy degradada. Alto riesgo de sobrescribir datos por accidente al editar parcialmente.

---

### BUG-017: Contadores del dashboard no incluyen tareas en estado "cancelled"

- **Severidad:** Media
- **Componente:** Frontend — Dashboard
- **Pantalla:** Página principal

**Pasos para reproducir:**
1. Verificar que existen tareas en estado "cancelled".
2. Observar los contadores en el encabezado del dashboard.
3. Sumar manualmente: `Por Hacer + En Progreso + En Revisión + Completadas`.

**Resultado actual:**
La suma de los contadores individuales no coincide con el "Total". No hay contador visible para "Canceladas".

Ejemplo observado:
- Total: 24
- Por Hacer: 14, En Progreso: 2, Completadas: 2 → Suma: 18 ≠ 24

**Resultado esperado:**
Debe existir un contador para "Canceladas". La suma de todos los contadores individuales debe ser igual al "Total".

**Impacto:** Los gerentes de proyecto no pueden ver la cantidad real de tareas canceladas. Los totales en pantalla son engañosos.

---

### BUG-018: Prioridad de tarea muestra valores en inglés en el panel de detalle

- **Severidad:** Baja
- **Componente:** Frontend — Panel de detalle de tarea
- **Pantalla:** Modal de detalle

**Pasos para reproducir:**
1. Crear una tarea con prioridad "Media".
2. Hacer clic en la tarea para ver el detalle.
3. Observar el campo de prioridad en la esquina superior.

**Resultado actual:**
Se muestra "Medium" en inglés, aunque el resto de la UI está en español.

**Resultado esperado:**
Se debe mostrar "Media" (traducido al español).

**Impacto:** Inconsistencia de idioma. Bajo impacto funcional, pero afecta la percepción de calidad del producto.
