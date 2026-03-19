"""TC-020 a TC-028: Tests del módulo de proyectos."""
import uuid


def test_create_project_valid(base_url, api, created_user):
    """TC-020: Crear proyecto con datos válidos retorna 201."""
    payload = {
        "name": f"Proyecto {uuid.uuid4().hex[:8]}",
        "description": "Descripción de prueba",
        "owner_id": created_user["id"],
    }
    r = api.post(f"{base_url}/projects", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert "id" in body
    assert body["status"] == "active"
    # Teardown
    api.delete(f"{base_url}/projects/{body['id']}")


def test_create_project_invalid_owner(base_url, api):
    """TC-021: BUG-003 — owner_id inexistente debe retornar 404 o 422.
    FALLA ESPERADA: La API acepta owner_ids que no existen (bug conocido).
    """
    payload = {
        "name": "Proyecto Huerfano",
        "owner_id": str(uuid.uuid4()),
    }
    r = api.post(f"{base_url}/projects", json=payload)
    assert r.status_code in [400, 404, 422], (
        "BUG-003: La API acepta owner_id inexistente. "
        f"Retornó {r.status_code}"
    )


def test_list_projects_excludes_deleted(base_url, api, created_project):
    """TC-022: BUG-002 — El listado por defecto no debe incluir proyectos eliminados.
    FALLA ESPERADA: La API retorna proyectos con status=deleted en el listado general.
    """
    # Eliminar el proyecto
    api.delete(f"{base_url}/projects/{created_project['id']}")

    r = api.get(f"{base_url}/projects")
    assert r.status_code == 200
    projects = r.json()["projects"]
    deleted_ids = [p["id"] for p in projects if p.get("status") == "deleted"]
    assert created_project["id"] not in deleted_ids, (
        "BUG-002: Proyecto eliminado aparece en listado por defecto"
    )


def test_filter_projects_by_status(base_url, api, created_project):
    """TC-023: Filtrar proyectos por status=active retorna solo activos."""
    r = api.get(f"{base_url}/projects", params={"status": "active"})
    assert r.status_code == 200
    projects = r.json()["projects"]
    for p in projects:
        assert p["status"] == "active", f"Proyecto con status={p['status']} no debería aparecer con filtro active"


def test_get_project_by_id(base_url, api, created_project):
    """TC-024: Obtener proyecto existente retorna datos correctos."""
    r = api.get(f"{base_url}/projects/{created_project['id']}")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == created_project["id"]
    assert body["name"] == created_project["name"]


def test_update_project_name(base_url, api, created_project):
    """TC-025: Actualizar nombre de proyecto retorna nombre nuevo."""
    new_name = f"Nombre Actualizado {uuid.uuid4().hex[:6]}"
    r = api.put(f"{base_url}/projects/{created_project['id']}", json={"name": new_name})
    assert r.status_code == 200
    assert r.json()["name"] == new_name


def test_delete_project(base_url, api, created_user):
    """TC-026: Eliminar proyecto lo marca como deleted."""
    payload = {
        "name": f"Para Eliminar {uuid.uuid4().hex[:8]}",
        "owner_id": created_user["id"],
    }
    r = api.post(f"{base_url}/projects", json=payload)
    assert r.status_code == 201
    project_id = r.json()["id"]

    r_del = api.delete(f"{base_url}/projects/{project_id}")
    assert r_del.status_code == 200

    r_get = api.get(f"{base_url}/projects/{project_id}")
    if r_get.status_code == 200:
        assert r_get.json()["status"] == "deleted"


def test_delete_project_tasks_orphaned(base_url, api, created_project, created_user):
    """TC-027: BUG-004 — Al eliminar proyecto, las tareas asociadas deben cancelarse.
    FALLA ESPERADA: Las tareas quedan huérfanas con status activo (bug conocido).
    """
    # Crear tarea en el proyecto
    task_payload = {
        "title": "Tarea en proyecto a eliminar",
        "project_id": created_project["id"],
        "reporter_id": created_user["id"],
    }
    r_task = api.post(f"{base_url}/tasks", json=task_payload)
    assert r_task.status_code == 201
    task_id = r_task.json()["id"]

    # Eliminar el proyecto
    api.delete(f"{base_url}/projects/{created_project['id']}")

    # Verificar que la tarea fue cancelada o eliminada
    r_get = api.get(f"{base_url}/tasks/{task_id}")
    if r_get.status_code == 200:
        assert r_get.json()["status"] == "cancelled", (
            "BUG-004: La tarea no fue cancelada al eliminar su proyecto. "
            f"Status actual: {r_get.json()['status']}"
        )
    # Si retorna 404 también está bien (eliminación en cascada)


def test_get_project_nonexistent(base_url, api):
    """TC-028: Proyecto inexistente retorna 404."""
    r = api.get(f"{base_url}/projects/{uuid.uuid4()}")
    assert r.status_code == 404
