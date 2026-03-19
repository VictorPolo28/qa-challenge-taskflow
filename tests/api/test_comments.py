"""TC-050 a TC-054: Tests del módulo de comentarios."""
import uuid


def test_create_comment_valid(base_url, api, created_task, created_user):
    """TC-050: Crear comentario en tarea existente retorna 201."""
    payload = {
        "task_id": created_task["id"],
        "author_id": created_user["id"],
        "content": "Este es un comentario de prueba",
    }
    r = api.post(f"{base_url}/tasks/{created_task['id']}/comments", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert "id" in body
    assert body["content"] == payload["content"]


def test_comment_task_id_url_overrides_body(base_url, api, created_user, created_project):
    """TC-051: BUG-010 — El task_id del body no debe sobreescribir el task_id de la URL.
    FALLA ESPERADA: La API usa el task_id del body, no el de la URL.
    """
    # Crear dos tareas
    r1 = api.post(f"{base_url}/tasks", json={
        "title": "Tarea A (URL target)",
        "project_id": created_project["id"],
        "reporter_id": created_user["id"],
    })
    r2 = api.post(f"{base_url}/tasks", json={
        "title": "Tarea B (body injection)",
        "project_id": created_project["id"],
        "reporter_id": created_user["id"],
    })
    task_a = r1.json()["id"]
    task_b = r2.json()["id"]

    # Enviar comentario a Tarea A (URL) pero con task_id de Tarea B en el body
    payload = {
        "task_id": task_b,  # Diferente al de la URL
        "author_id": created_user["id"],
        "content": "Comentario desviado",
    }
    r = api.post(f"{base_url}/tasks/{task_a}/comments", json=payload)
    assert r.status_code == 201

    # Verificar que el comentario quedó en Tarea A, no en Tarea B
    r_comments_a = api.get(f"{base_url}/tasks/{task_a}/comments")
    r_comments_b = api.get(f"{base_url}/tasks/{task_b}/comments")

    comments_a = r_comments_a.json()["total"]
    comments_b = r_comments_b.json()["total"]

    assert comments_a == 1, (
        f"BUG-010: El comentario no quedó en Tarea A. "
        f"Task A tiene {comments_a} comentarios, Task B tiene {comments_b}"
    )

    # Teardown
    api.delete(f"{base_url}/tasks/{task_a}")
    api.delete(f"{base_url}/tasks/{task_b}")


def test_create_comment_nonexistent_task(base_url, api, created_user):
    """TC-052: Comentario en tarea inexistente retorna 404."""
    payload = {
        "task_id": str(uuid.uuid4()),
        "author_id": created_user["id"],
        "content": "Comentario fantasma",
    }
    r = api.post(f"{base_url}/tasks/{uuid.uuid4()}/comments", json=payload)
    assert r.status_code == 404


def test_list_comments(base_url, api, created_task, created_user):
    """TC-053: Listar comentarios de una tarea retorna lista con total."""
    payload = {
        "task_id": created_task["id"],
        "author_id": created_user["id"],
        "content": "Comentario listado",
    }
    api.post(f"{base_url}/tasks/{created_task['id']}/comments", json=payload)

    r = api.get(f"{base_url}/tasks/{created_task['id']}/comments")
    assert r.status_code == 200
    body = r.json()
    assert "comments" in body
    assert "total" in body
    assert body["total"] >= 1


def test_create_comment_empty_content(base_url, api, created_task, created_user):
    """TC-054: Comentario con contenido vacío retorna 422."""
    payload = {
        "task_id": created_task["id"],
        "author_id": created_user["id"],
        "content": "",
    }
    r = api.post(f"{base_url}/tasks/{created_task['id']}/comments", json=payload)
    assert r.status_code == 422
