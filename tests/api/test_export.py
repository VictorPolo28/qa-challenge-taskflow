"""TC-080 a TC-084: Tests del módulo de exportación."""
import uuid


def test_export_json(base_url, api):
    """TC-080: Exportar todas las tareas en JSON retorna estructura correcta."""
    r = api.get(f"{base_url}/export/tasks")
    assert r.status_code == 200
    body = r.json()
    assert "tasks" in body
    assert "total" in body
    assert isinstance(body["tasks"], list)
    assert body["total"] == len(body["tasks"])


def test_export_json_by_project(base_url, api, created_task, created_project):
    """TC-081: Exportar JSON filtrado por proyecto retorna solo tareas de ese proyecto."""
    r = api.get(f"{base_url}/export/tasks", params={"project_id": created_project["id"]})
    assert r.status_code == 200
    tasks = r.json()["tasks"]
    for t in tasks:
        assert t["project_id"] == created_project["id"], (
            f"Tarea {t['id']} no pertenece al proyecto {created_project['id']}"
        )


def test_export_csv_structure(base_url, api):
    """TC-082: Exportar en CSV retorna Content-Type text/csv con encabezado."""
    r = api.get(f"{base_url}/export/tasks", params={"format": "csv"})
    assert r.status_code == 200
    # La respuesta debe tener content-type text/csv
    assert "text/csv" in r.headers.get("content-type", ""), (
        f"Content-Type esperado: text/csv. Obtenido: {r.headers.get('content-type')}"
    )
    lines = r.text.strip().split("\n")
    assert len(lines) >= 1, "CSV debe tener al menos la línea de encabezado"
    # Verificar que el encabezado contiene campos esperados
    header = lines[0]
    assert "id" in header and "title" in header


def test_export_csv_escapes_commas(base_url, api, created_project, created_user):
    """TC-083: BUG-013 — Campos con comas en CSV deben estar entre comillas.
    FALLA ESPERADA: La API no escapa comas en el CSV.
    """
    # Crear tarea con coma en el título
    title_with_comma = "Tarea, con coma en el título"
    r = api.post(f"{base_url}/tasks", json={
        "title": title_with_comma,
        "project_id": created_project["id"],
        "reporter_id": created_user["id"],
    })
    assert r.status_code == 201
    task_id = r.json()["id"]

    r_csv = api.get(f"{base_url}/export/tasks", params={
        "format": "csv",
        "project_id": created_project["id"],
    })
    csv_content = r_csv.text

    # Verificar que la coma del título está entre comillas
    # Un CSV bien formado tiene: ..., "Tarea, con coma en el título", ...
    # Un CSV mal formado tiene: ..., Tarea, con coma en el título, ...
    assert f'"{title_with_comma}"' in csv_content, (
        f"BUG-013: El campo con coma no está entrecomillado en el CSV. "
        f"Fragmento: {csv_content[:300]}"
    )

    api.delete(f"{base_url}/tasks/{task_id}")


def test_export_empty_project_json(base_url, api, created_user):
    """Exportar proyecto sin tareas retorna lista vacía."""
    r_proj = api.post(f"{base_url}/projects", json={
        "name": f"Proyecto vacio {uuid.uuid4().hex[:6]}",
        "owner_id": created_user["id"],
    })
    project_id = r_proj.json()["id"]

    r = api.get(f"{base_url}/export/tasks", params={"project_id": project_id})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0
    assert body["tasks"] == []

    api.delete(f"{base_url}/projects/{project_id}")
