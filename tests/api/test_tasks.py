"""TC-030 a TC-044: Tests del módulo de tareas."""
import uuid
import pytest


def test_create_task_full(base_url, api, created_project, created_user):
    """TC-030: Crear tarea con todos los campos retorna 201 con status=todo."""
    payload = {
        "title": "Tarea completa de prueba",
        "description": "Descripción detallada de la tarea",
        "project_id": created_project["id"],
        "reporter_id": created_user["id"],
        "assignee_id": created_user["id"],
        "priority": "high",
        "due_date": "2027-12-31",
        "tags": ["testing", "api"],
    }
    r = api.post(f"{base_url}/tasks", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert "id" in body
    assert body["status"] == "todo"
    assert body["title"] == payload["title"]
    assert body["priority"] == payload["priority"]
    assert isinstance(body["tags"], list)
    # Teardown
    api.delete(f"{base_url}/tasks/{body['id']}")


def test_create_task_minimal(base_url, api, created_project, created_user):
    """TC-031: Crear tarea con campos obligatorios mínimos retorna 201."""
    payload = {
        "title": "Tarea mínima",
        "project_id": created_project["id"],
        "reporter_id": created_user["id"],
    }
    r = api.post(f"{base_url}/tasks", json=payload)
    assert r.status_code == 201
    task_id = r.json()["id"]
    api.delete(f"{base_url}/tasks/{task_id}")


def test_create_task_nonexistent_project(base_url, api, created_user):
    """TC-032: project_id inexistente retorna 404."""
    payload = {
        "title": "Tarea en proyecto fantasma",
        "project_id": str(uuid.uuid4()),
        "reporter_id": created_user["id"],
    }
    r = api.post(f"{base_url}/tasks", json=payload)
    assert r.status_code == 404


def test_create_task_in_deleted_project(base_url, api, created_user):
    """TC-033: BUG-005 — No debe permitirse crear tareas en proyectos eliminados.
    FALLA ESPERADA: La API permite crear tareas en proyectos archivados/eliminados.
    """
    # Crear y eliminar un proyecto
    r_proj = api.post(f"{base_url}/projects", json={
        "name": f"Proyecto a eliminar {uuid.uuid4().hex[:6]}",
        "owner_id": created_user["id"],
    })
    project_id = r_proj.json()["id"]
    api.delete(f"{base_url}/projects/{project_id}")

    # Intentar crear tarea en ese proyecto
    payload = {
        "title": "Tarea en proyecto eliminado",
        "project_id": project_id,
        "reporter_id": created_user["id"],
    }
    r = api.post(f"{base_url}/tasks", json=payload)
    assert r.status_code in [400, 422], (
        f"BUG-005: Se permite crear tareas en proyectos eliminados. "
        f"Retornó {r.status_code}"
    )


def test_create_task_invalid_priority(base_url, api, created_project, created_user):
    """TC-034: Prioridad inválida retorna 422."""
    payload = {
        "title": "Tarea prioridad inválida",
        "project_id": created_project["id"],
        "reporter_id": created_user["id"],
        "priority": "ultra-critical",
    }
    r = api.post(f"{base_url}/tasks", json=payload)
    assert r.status_code == 422


def test_create_task_invalid_reporter(base_url, api, created_project):
    """TC-035: BUG-007 — reporter_id inexistente debe retornar error.
    FALLA ESPERADA: La API no valida que reporter_id exista.
    """
    payload = {
        "title": "Tarea con reporter inexistente",
        "project_id": created_project["id"],
        "reporter_id": str(uuid.uuid4()),
    }
    r = api.post(f"{base_url}/tasks", json=payload)
    assert r.status_code in [400, 404, 422], (
        f"BUG-007: reporter_id inexistente aceptado. Retornó {r.status_code}"
    )


def test_list_tasks_filter_by_project(base_url, api, created_task, created_project):
    """TC-036: Listar tareas filtradas por project_id retorna solo las de ese proyecto."""
    r = api.get(f"{base_url}/tasks", params={"project_id": created_project["id"]})
    assert r.status_code == 200
    body = r.json()
    assert "tasks" in body
    for t in body["tasks"]:
        assert t["project_id"] == created_project["id"], (
            f"Tarea {t['id']} pertenece al proyecto {t['project_id']}, "
            f"no al filtrado {created_project['id']}"
        )


def test_pagination_total_reflects_filter(base_url, api, created_project, created_user):
    """TC-037: BUG-007 — El total de paginación debe reflejar los filtros aplicados.
    FALLA ESPERADA: El total es el conteo global, no el filtrado.
    """
    # Crear 3 tareas en el proyecto
    task_ids = []
    for i in range(3):
        r = api.post(f"{base_url}/tasks", json={
            "title": f"Tarea paginacion {i}",
            "project_id": created_project["id"],
            "reporter_id": created_user["id"],
        })
        if r.status_code == 201:
            task_ids.append(r.json()["id"])

    r = api.get(f"{base_url}/tasks", params={
        "project_id": created_project["id"],
        "page": 1,
        "page_size": 100,
    })
    body = r.json()
    actual_count = len(body["tasks"])
    assert body["total"] == actual_count, (
        f"BUG-009: total={body['total']} no coincide con tareas retornadas={actual_count}"
    )

    for tid in task_ids:
        api.delete(f"{base_url}/tasks/{tid}")


def test_search_tasks(base_url, api, created_task):
    """TC-038: Búsqueda por texto retorna tareas que coinciden."""
    # Usar parte del título de la tarea creada
    search_term = created_task["title"][:10]
    r = api.get(f"{base_url}/tasks", params={"search": search_term})
    assert r.status_code == 200
    task_ids = [t["id"] for t in r.json()["tasks"]]
    assert created_task["id"] in task_ids, (
        f"La tarea con título '{created_task['title']}' no apareció al buscar '{search_term}'"
    )


def test_search_sql_injection(base_url, api):
    """TC-039: BUG-008 — Inyección SQL en parámetro search no debe romper la DB ni retornar todos los registros.
    FALLA ESPERADA: El parámetro search no está parametrizado.
    """
    injection = "' OR '1'='1"
    r = api.get(f"{base_url}/tasks", params={"search": injection})
    assert r.status_code == 200

    # Obtener total real de tareas
    r_all = api.get(f"{base_url}/tasks", params={"page_size": 1})
    total_tasks = r_all.json()["total"]

    injected_count = len(r.json()["tasks"])
    # Si la inyección fue exitosa, retornará todas las tareas
    assert injected_count < total_tasks or total_tasks == 0, (
        f"BUG-008: Posible SQL injection — búsqueda con '{injection}' "
        f"retornó {injected_count} tareas (total en DB: {total_tasks})"
    )


def test_update_task_status(base_url, api, created_task):
    """TC-040: Actualizar estado a in_progress retorna el estado nuevo."""
    r = api.put(f"{base_url}/tasks/{created_task['id']}", json={"status": "in_progress"})
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"


def test_invalid_state_transition(base_url, api, created_task):
    """TC-041: BUG-010 — Transición done → todo debe ser rechazada.
    FALLA ESPERADA: La API permite transiciones inválidas.
    """
    # Primero llevar a done
    api.put(f"{base_url}/tasks/{created_task['id']}", json={"status": "in_progress"})
    api.put(f"{base_url}/tasks/{created_task['id']}", json={"status": "done"})

    # Intentar revertir a todo
    r = api.put(f"{base_url}/tasks/{created_task['id']}", json={"status": "todo"})
    assert r.status_code == 400, (
        f"BUG-010: Transición done→todo aceptada. Retornó {r.status_code}"
    )


def test_delete_task_success(base_url, api, created_project, created_user):
    """TC-042: Eliminar tarea existente — tarea no accesible después."""
    r = api.post(f"{base_url}/tasks", json={
        "title": "Tarea a eliminar",
        "project_id": created_project["id"],
        "reporter_id": created_user["id"],
    })
    assert r.status_code == 201
    task_id = r.json()["id"]

    r_del = api.delete(f"{base_url}/tasks/{task_id}")
    assert r_del.status_code in [200, 204]

    r_get = api.get(f"{base_url}/tasks/{task_id}")
    assert r_get.status_code == 404, "La tarea eliminada aún es accesible"


def test_delete_task_nonexistent(base_url, api):
    """TC-043: Eliminar tarea inexistente retorna 404."""
    r = api.delete(f"{base_url}/tasks/{uuid.uuid4()}")
    assert r.status_code == 404


def test_get_deleted_task_returns_404(base_url, api, created_project, created_user):
    """TC-044: GET de tarea eliminada retorna 404."""
    r = api.post(f"{base_url}/tasks", json={
        "title": "Tarea get post-delete",
        "project_id": created_project["id"],
        "reporter_id": created_user["id"],
    })
    task_id = r.json()["id"]
    api.delete(f"{base_url}/tasks/{task_id}")

    r_get = api.get(f"{base_url}/tasks/{task_id}")
    assert r_get.status_code == 404
