# Plan de Pruebas — TaskFlow

## 1. Objetivo
Validar la calidad de la aplicación TaskFlow (API REST + Frontend) antes de un despliegue a producción, identificando defectos funcionales, de seguridad y de rendimiento.

---

## 2. Alcance

### En alcance
- API REST: todos los endpoints documentados en Swagger (`/docs`)
- Frontend: flujos principales de gestión de tareas
- Seguridad básica: inyección, autorización, exposición de datos
- Rendimiento: tiempos de respuesta bajo carga normal

### Fuera de alcance
- Autenticación/autorización (la app no la implementa en esta versión)
- Compatibilidad con navegadores distintos a Chromium
- Tests de accesibilidad (WCAG)
- Infraestructura Docker / Docker Compose

---

## 3. Estrategia de prueba

| Tipo | Herramienta | Cobertura objetivo |
|------|-------------|-------------------|
| API funcional | pytest + requests | Todos los endpoints CRUD |
| API negativos | pytest + requests | Validaciones, edge cases |
| UI / E2E | Playwright | Flujos críticos del usuario |
| Rendimiento | Locust | Endpoints de mayor tráfico |
| Seguridad | Manual + pytest | OWASP top-10 básico |

---

## 4. Matriz de riesgos

| Área | Probabilidad de fallo | Impacto | Prioridad de prueba |
|------|-----------------------|---------|---------------------|
| Integridad de datos en Tasks | Alta | Crítico | P1 |
| Validaciones de entrada en API | Alta | Alto | P1 |
| Seguridad (inyección SQL) | Media | Crítico | P1 |
| Paginación y filtros | Alta | Alto | P1 |
| Operaciones masivas (bulk) | Media | Alto | P2 |
| Exportación CSV | Media | Medio | P2 |
| Gestión de proyectos (cascada al eliminar) | Media | Alto | P2 |
| Estadísticas (cálculo de vencidas) | Alta | Medio | P2 |
| Comentarios (coherencia task_id) | Media | Medio | P3 |
| Transiciones de estado de tareas | Baja | Medio | P3 |
| Frontend (UX/feedback) | Alta | Bajo | P4 |

---

## 5. Casos de prueba

### Módulo: Health

| ID | Título | Precondiciones | Pasos | Datos de prueba | Resultado esperado | Prioridad |
|----|--------|---------------|-------|-----------------|-------------------|-----------|
| TC-001 | Health check retorna 200 y estado healthy | App levantada | GET /api/health | — | 200 OK, `{"status": "healthy"}` con campo `version` | P1 |
| TC-002 | Health check incluye versión de la app | App levantada | GET /api/health | — | Campo `version` presente en respuesta | P2 |

---

### Módulo: Users

| ID | Título | Precondiciones | Pasos | Datos de prueba | Resultado esperado | Prioridad |
|----|--------|---------------|-------|-----------------|-------------------|-----------|
| TC-010 | Crear usuario con datos válidos | API activa | POST /api/users con body completo | `{username:"tester01", email:"test@example.com", full_name:"Test User", role:"member"}` | 201 Created, respuesta con `id` generado y campos coincidentes | P1 |
| TC-011 | Crear usuario con email inválido | API activa | POST /api/users con email sin formato | `{email:"noesunemail"}` | 422 Unprocessable Entity | P1 |
| TC-012 | Crear usuario con username duplicado | Usuario existente con mismo username | POST /api/users con username ya usado | Mismo username del paso anterior | 409 Conflict | P1 |
| TC-013 | Crear usuario con email duplicado | Usuario existente con mismo email | POST /api/users con email ya usado | Mismo email del paso anterior | 409 Conflict | P1 |
| TC-014 | Listar usuarios activos | Al menos 1 usuario activo | GET /api/users | — | 200 OK, lista de usuarios con `total` | P1 |
| TC-015 | Obtener usuario por ID válido | Usuario existente | GET /api/users/{id} | ID de usuario existente | 200 OK, datos del usuario | P1 |
| TC-016 | Obtener usuario con ID inexistente | API activa | GET /api/users/{id} | UUID aleatorio que no existe | 404 Not Found | P1 |
| TC-017 | Desactivar usuario (soft delete) | Usuario activo | DELETE /api/users/{id} | ID de usuario activo | 200 OK, `{"message": "User deactivated"}` | P2 |
| TC-018 | Usuario desactivado no aparece en listado por defecto | Usuario previamente desactivado | GET /api/users | — | El usuario desactivado NO aparece en la lista | P2 |
| TC-019 | Crear usuario con username corto (< 3 chars) | API activa | POST /api/users | `{username:"ab"}` | 422 Unprocessable Entity | P2 |

---

### Módulo: Projects

| ID | Título | Precondiciones | Pasos | Datos de prueba | Resultado esperado | Prioridad |
|----|--------|---------------|-------|-----------------|-------------------|-----------|
| TC-020 | Crear proyecto con datos válidos | Usuario existente como owner | POST /api/projects | `{name:"Proyecto Test", owner_id:"<id_valido>"}` | 201 Created, respuesta con `id` y `status: "active"` | P1 |
| TC-021 | Crear proyecto con owner_id inexistente | API activa | POST /api/projects | `{name:"Proyecto Test", owner_id:"uuid-inexistente"}` | 400 o 422 — no debe aceptar owner inválido | P1 |
| TC-022 | Listar proyectos no muestra eliminados por defecto | Existe proyecto eliminado | GET /api/projects | — | Proyectos con `status: "deleted"` NO deben aparecer | P1 |
| TC-023 | Filtrar proyectos por estado | Proyectos en diferentes estados | GET /api/projects?status=active | `status=active` | Solo proyectos activos | P2 |
| TC-024 | Obtener proyecto por ID | Proyecto existente | GET /api/projects/{id} | ID válido | 200 OK, datos del proyecto | P1 |
| TC-025 | Actualizar nombre de proyecto | Proyecto existente | PUT /api/projects/{id} | `{name:"Nuevo Nombre"}` | 200 OK, nombre actualizado | P2 |
| TC-026 | Eliminar proyecto (soft delete) | Proyecto activo | DELETE /api/projects/{id} | ID válido | 200 OK, proyecto con `status: "deleted"` | P2 |
| TC-027 | Tareas no quedan huérfanas al eliminar proyecto | Proyecto con tareas asociadas | DELETE /api/projects/{id}, luego GET /api/tasks?project_id={id} | — | Las tareas del proyecto eliminado no deben ser accesibles o deben marcarse como canceladas | P2 |
| TC-028 | Obtener proyecto inexistente | API activa | GET /api/projects/{id} | UUID que no existe | 404 Not Found | P1 |

---

### Módulo: Tasks

| ID | Título | Precondiciones | Pasos | Datos de prueba | Resultado esperado | Prioridad |
|----|--------|---------------|-------|-----------------|-------------------|-----------|
| TC-030 | Crear tarea con datos completos | Proyecto y usuario existentes | POST /api/tasks | Body completo con todos los campos | 201 Created, `status: "todo"` por defecto | P1 |
| TC-031 | Crear tarea solo con campos obligatorios | Proyecto y usuario existentes | POST /api/tasks | Solo `title`, `project_id`, `reporter_id` | 201 Created | P1 |
| TC-032 | Crear tarea con proyecto inexistente | API activa | POST /api/tasks | `project_id` UUID que no existe | 404 Not Found | P1 |
| TC-033 | Crear tarea en proyecto eliminado/archivado | Proyecto con status≠active | POST /api/tasks | `project_id` de proyecto eliminado | 400 o 422 — no debe permitirse | P1 |
| TC-034 | Crear tarea con prioridad inválida | Proyecto existente | POST /api/tasks | `priority: "ultra-high"` | 422 Unprocessable Entity | P1 |
| TC-035 | Crear tarea con reporter_id inexistente | Proyecto existente | POST /api/tasks | `reporter_id: "uuid-inexistente"` | 400 o 422 | P2 |
| TC-036 | Listar tareas con filtro por proyecto | Tareas en diferentes proyectos | GET /api/tasks?project_id={id} | ID de proyecto | Solo tareas de ese proyecto | P1 |
| TC-037 | Paginación: total refleja filtros aplicados | Más de 20 tareas en un proyecto | GET /api/tasks?project_id={id}&page=1&page_size=5 | — | `total` debe ser la cantidad de tareas del proyecto, no el total global | P1 |
| TC-038 | Búsqueda de tareas por texto | Tareas con títulos variados | GET /api/tasks?search=autenticacion | — | Solo tareas cuyo título/descripción coincide | P2 |
| TC-039 | Búsqueda con payload de inyección SQL | API activa | GET /api/tasks?search=' OR '1'='1 | `search=' OR '1'='1` | La consulta no debe romper la DB ni retornar todos los registros | P1 |
| TC-040 | Actualizar estado de tarea (happy path) | Tarea en estado `todo` | PUT /api/tasks/{id} con `status: "in_progress"` | `{status:"in_progress"}` | 200 OK, `status` actualizado | P1 |
| TC-041 | Transición de estado inválida (done → todo) | Tarea en estado `done` | PUT /api/tasks/{id} con `status: "todo"` | `{status:"todo"}` | 400 — transición no permitida | P2 |
| TC-042 | Eliminar tarea existente | Tarea existente | DELETE /api/tasks/{id} | ID válido | 200 o 204, tarea ya no accesible | P1 |
| TC-043 | Eliminar tarea inexistente | API activa | DELETE /api/tasks/{id} | UUID que no existe | 404 Not Found | P1 |
| TC-044 | Obtener tarea eliminada retorna 404 | Tarea previamente eliminada | GET /api/tasks/{id} | ID de tarea eliminada | 404 Not Found | P1 |

---

### Módulo: Comments

| ID | Título | Precondiciones | Pasos | Datos de prueba | Resultado esperado | Prioridad |
|----|--------|---------------|-------|-----------------|-------------------|-----------|
| TC-050 | Crear comentario en tarea existente | Tarea y usuario existentes | POST /api/tasks/{task_id}/comments | `{task_id: "<id>", author_id:"<user_id>", content:"comentario"}` | 201 Created, campos coherentes | P1 |
| TC-051 | task_id del body difiere del task_id de la URL | Dos tareas existentes | POST /api/tasks/{task_id_A}/comments con `task_id: task_id_B` | Body con task_id diferente a la URL | El comentario debe quedar asociado al task_id de la URL, no del body | P1 |
| TC-052 | Crear comentario en tarea inexistente | API activa | POST /api/tasks/{id}/comments | ID de tarea que no existe | 404 Not Found | P1 |
| TC-053 | Listar comentarios de una tarea | Tarea con comentarios | GET /api/tasks/{task_id}/comments | — | 200 OK, lista de comentarios con `total` | P2 |
| TC-054 | Comentario vacío es rechazado | Tarea existente | POST /api/tasks/{id}/comments | `{content: ""}` | 422 Unprocessable Entity | P2 |

---

### Módulo: Statistics

| ID | Título | Precondiciones | Pasos | Datos de prueba | Resultado esperado | Prioridad |
|----|--------|---------------|-------|-----------------|-------------------|-----------|
| TC-060 | Estadísticas globales retornan totales correctos | Tareas en múltiples estados | GET /api/stats | — | `total_tasks` coincide con suma de todos los estados | P1 |
| TC-061 | Estadísticas por proyecto son correctas | Proyecto con tareas conocidas | GET /api/stats?project_id={id} | ID de proyecto | Totales reflejan solo las tareas de ese proyecto | P1 |
| TC-062 | Cálculo de tareas vencidas es correcto | Tareas con due_date pasada no completadas | GET /api/stats | — | `overdue` cuenta solo tareas con fecha pasada y status ≠ done/cancelled | P2 |
| TC-063 | Estadísticas con project_id inexistente | API activa | GET /api/stats?project_id={id} | UUID que no existe | 200 OK con todos los valores en 0 | P3 |

---

### Módulo: Bulk Update

| ID | Título | Precondiciones | Pasos | Datos de prueba | Resultado esperado | Prioridad |
|----|--------|---------------|-------|-----------------|-------------------|-----------|
| TC-070 | Actualización masiva exitosa | Al menos 3 tareas existentes | POST /api/tasks/bulk-update | `{task_ids:[...], updates:{status:"done"}}` | 200 OK, `updated` = cantidad de IDs enviados | P2 |
| TC-071 | Bulk update con IDs mixtos (válidos e inválidos) | Algunas tareas existentes | POST /api/tasks/bulk-update | Lista con IDs reales y UUIDs inexistentes | 400 o 207 Multi-Status — debe indicar cuáles fallaron | P1 |
| TC-072 | Bulk update sin task_ids | API activa | POST /api/tasks/bulk-update | `{task_ids:[], updates:{status:"done"}}` | 400 Bad Request | P2 |
| TC-073 | Bulk update con campo no permitido | Tareas existentes | POST /api/tasks/bulk-update | `{task_ids:[...], updates:{title:"hack"}}` | Solo actualiza campos permitidos (status, priority, assignee_id) | P2 |

---

### Módulo: Export

| ID | Título | Precondiciones | Pasos | Datos de prueba | Resultado esperado | Prioridad |
|----|--------|---------------|-------|-----------------|-------------------|-----------|
| TC-080 | Exportar todas las tareas en JSON | Tareas existentes | GET /api/export/tasks | — | 200 OK, JSON con array `tasks` y `total` correcto | P2 |
| TC-081 | Exportar tareas filtradas por proyecto en JSON | Proyecto con tareas | GET /api/export/tasks?project_id={id} | ID de proyecto | Solo tareas de ese proyecto | P2 |
| TC-082 | Exportar en CSV — estructura correcta | Tareas existentes | GET /api/export/tasks?format=csv | `format=csv` | Respuesta CSV con encabezado y filas por tarea | P2 |
| TC-083 | Exportar CSV — campos con comas escapados correctamente | Tarea con coma en título/descripción | GET /api/export/tasks?format=csv | Tarea creada con `title:"Tarea, con coma"` | El CSV debe escapar la coma (campo entre comillas) | P1 |
| TC-084 | Exportar con formato inválido | API activa | GET /api/export/tasks?format=xml | `format=xml` | 400 Bad Request o fallback a JSON | P3 |

---

## 6. Criterios de aceptación
- Los tests marcados P1 deben tener 0 fallos para aprobar un release.
- Los tests P2 deben tener máximo 2 fallos no críticos documentados.
- Todos los bugs P1 encontrados durante la ejecución deben reportarse antes de cualquier despliegue.
