"""TC-070 a TC-073: Tests de operaciones masivas (bulk update)."""
import uuid


def _create_task(api, base_url, project_id, reporter_id):
    r = api.post(f"{base_url}/tasks", json={
        "title": f"Bulk task {uuid.uuid4().hex[:6]}",
        "project_id": project_id,
        "reporter_id": reporter_id,
    })
    assert r.status_code == 201
    return r.json()["id"]


def test_bulk_update_valid(base_url, api, created_project, created_user):
    """TC-070: Actualización masiva exitosa retorna updated = cantidad de IDs enviados."""
    ids = [_create_task(api, base_url, created_project["id"], created_user["id"]) for _ in range(3)]

    r = api.post(f"{base_url}/tasks/bulk-update", json={
        "task_ids": ids,
        "updates": {"status": "in_progress"},
    })
    assert r.status_code == 200
    body = r.json()
    assert body["updated"] == 3, f"Esperado updated=3, obtenido {body['updated']}"

    # Verificar que las tareas cambiaron de estado
    for tid in ids:
        r_t = api.get(f"{base_url}/tasks/{tid}")
        assert r_t.json()["status"] == "in_progress"
        api.delete(f"{base_url}/tasks/{tid}")


def test_bulk_update_mixed_ids(base_url, api, created_project, created_user):
    """TC-071: BUG-012 — IDs mixtos (válidos + inexistentes) debe retornar error o 207.
    FALLA ESPERADA: La API retorna 200 con updated<len(task_ids) sin indicar los fallidos.
    """
    valid_id = _create_task(api, base_url, created_project["id"], created_user["id"])
    fake_id = str(uuid.uuid4())

    r = api.post(f"{base_url}/tasks/bulk-update", json={
        "task_ids": [valid_id, fake_id],
        "updates": {"priority": "high"},
    })

    # La respuesta debería indicar que un ID no fue encontrado
    assert r.status_code in [400, 404, 207], (
        f"BUG-012: Se esperaba error o 207 para IDs mixtos. "
        f"Retornó {r.status_code} con body: {r.json()}"
    )

    api.delete(f"{base_url}/tasks/{valid_id}")


def test_bulk_update_empty_ids(base_url, api):
    """TC-072: bulk-update sin task_ids retorna 400."""
    r = api.post(f"{base_url}/tasks/bulk-update", json={
        "task_ids": [],
        "updates": {"status": "done"},
    })
    assert r.status_code == 400


def test_bulk_update_disallowed_field(base_url, api, created_project, created_user):
    """TC-073: Campos no permitidos (title) son ignorados en bulk-update."""
    task_id = _create_task(api, base_url, created_project["id"], created_user["id"])
    original_title = api.get(f"{base_url}/tasks/{task_id}").json()["title"]

    r = api.post(f"{base_url}/tasks/bulk-update", json={
        "task_ids": [task_id],
        "updates": {"title": "Título inyectado", "priority": "low"},
    })
    assert r.status_code in [200, 400]

    # Verificar que el title NO cambió
    updated = api.get(f"{base_url}/tasks/{task_id}").json()
    assert updated["title"] == original_title, (
        f"El campo 'title' fue modificado por bulk-update aunque no debería ser permitido"
    )

    api.delete(f"{base_url}/tasks/{task_id}")
