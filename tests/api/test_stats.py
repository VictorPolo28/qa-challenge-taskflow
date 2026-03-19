"""TC-060 a TC-063: Tests del módulo de estadísticas."""
import uuid


def test_stats_global_returns_200(base_url, api):
    """TC-060a: GET /api/stats retorna 200 con estructura correcta."""
    r = api.get(f"{base_url}/stats")
    assert r.status_code == 200
    body = r.json()
    assert "total_tasks" in body
    assert "by_status" in body
    assert "by_priority" in body
    assert "overdue" in body


def test_stats_total_matches_sum_of_statuses(base_url, api):
    """TC-060b: BUG-011 — La suma de tareas por estado debe igualar total_tasks.
    Nota: Si hay tareas en cancelled que no se contabilizan, esta prueba lo detecta.
    """
    r = api.get(f"{base_url}/stats")
    body = r.json()
    total = body["total_tasks"]
    by_status_sum = sum(body["by_status"].values())
    assert total == by_status_sum, (
        f"total_tasks={total} no coincide con suma de estados={by_status_sum}. "
        f"Detalle: {body['by_status']}"
    )


def test_stats_by_project(base_url, api, created_task, created_project):
    """TC-061: Estadísticas por project_id reflejan solo ese proyecto."""
    r = api.get(f"{base_url}/stats", params={"project_id": created_project["id"]})
    assert r.status_code == 200
    body = r.json()
    assert body["total_tasks"] >= 1, "Debe haber al menos la tarea creada por el fixture"


def test_stats_overdue_calculation(base_url, api, created_project, created_user):
    """TC-062: BUG-011 — Tarea con due_date en el pasado y status=todo debe contarse como overdue."""
    # Crear tarea vencida
    r = api.post(f"{base_url}/tasks", json={
        "title": "Tarea vencida para stats",
        "project_id": created_project["id"],
        "reporter_id": created_user["id"],
        "due_date": "2020-01-01",
    })
    assert r.status_code == 201
    task_id = r.json()["id"]

    r_stats = api.get(f"{base_url}/stats", params={"project_id": created_project["id"]})
    overdue = r_stats.json()["overdue"]
    assert overdue >= 1, (
        f"BUG-011: La tarea con due_date=2020-01-01 no fue contada como overdue. "
        f"overdue={overdue}"
    )

    # Teardown
    api.delete(f"{base_url}/tasks/{task_id}")


def test_stats_nonexistent_project(base_url, api):
    """TC-063: Estadísticas con project_id inexistente retorna totales en 0."""
    r = api.get(f"{base_url}/stats", params={"project_id": str(uuid.uuid4())})
    assert r.status_code == 200
    body = r.json()
    assert body["total_tasks"] == 0
