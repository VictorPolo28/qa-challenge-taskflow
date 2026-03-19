"""TC-010 a TC-019: Tests del módulo de usuarios."""
import uuid


def test_create_user_valid(base_url, api):
    """TC-010: Crear usuario con datos válidos retorna 201 con id."""
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "username": f"user_{suffix}",
        "email": f"user_{suffix}@test.com",
        "full_name": "Usuario de Prueba",
        "role": "member",
    }
    r = api.post(f"{base_url}/users", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert "id" in body
    assert body["username"] == payload["username"]
    assert body["email"] == payload["email"]
    # Teardown
    api.delete(f"{base_url}/users/{body['id']}")


def test_create_user_invalid_email(base_url, api):
    """TC-011: BUG-001 — Email inválido debe ser rechazado con 422.
    FALLA ESPERADA: La API acepta emails sin formato válido (bug conocido).
    """
    payload = {
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": "noesunemail",
        "full_name": "Test",
        "role": "member",
    }
    r = api.post(f"{base_url}/users", json=payload)
    assert r.status_code == 422, (
        "BUG-001: La API acepta emails inválidos. Debería retornar 422."
    )


def test_create_user_duplicate_username(base_url, api, created_user):
    """TC-012: Username duplicado retorna 409."""
    payload = {
        "username": created_user["username"],
        "email": f"otro_{uuid.uuid4().hex[:8]}@test.com",
        "full_name": "Otro Usuario",
        "role": "member",
    }
    r = api.post(f"{base_url}/users", json=payload)
    assert r.status_code == 409, f"Esperado 409, obtenido {r.status_code}"


def test_create_user_duplicate_email(base_url, api, created_user):
    """TC-013: Email duplicado retorna 409."""
    payload = {
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": created_user["email"],
        "full_name": "Otro Usuario",
        "role": "member",
    }
    r = api.post(f"{base_url}/users", json=payload)
    assert r.status_code == 409, f"Esperado 409, obtenido {r.status_code}"


def test_list_users_returns_200(base_url, api):
    """TC-014: Listar usuarios retorna 200 con campos total y users."""
    r = api.get(f"{base_url}/users")
    assert r.status_code == 200
    body = r.json()
    assert "users" in body
    assert "total" in body
    assert isinstance(body["users"], list)


def test_get_user_by_valid_id(base_url, api, created_user):
    """TC-015: Obtener usuario existente por ID retorna datos correctos."""
    r = api.get(f"{base_url}/users/{created_user['id']}")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == created_user["id"]
    assert body["username"] == created_user["username"]


def test_get_user_nonexistent(base_url, api):
    """TC-016: ID inexistente retorna 404."""
    r = api.get(f"{base_url}/users/{uuid.uuid4()}")
    assert r.status_code == 404


def test_deactivate_user(base_url, api):
    """TC-017: Soft-delete de usuario retorna mensaje de desactivación."""
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "username": f"del_{suffix}",
        "email": f"del_{suffix}@test.com",
        "full_name": "Usuario a Eliminar",
        "role": "member",
    }
    r = api.post(f"{base_url}/users", json=payload)
    assert r.status_code == 201
    user_id = r.json()["id"]

    r_del = api.delete(f"{base_url}/users/{user_id}")
    assert r_del.status_code == 200
    assert "deactivated" in r_del.json().get("message", "").lower()


def test_deactivated_user_not_in_default_list(base_url, api):
    """TC-018: Usuario desactivado no aparece en el listado por defecto."""
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "username": f"inactive_{suffix}",
        "email": f"inactive_{suffix}@test.com",
        "full_name": "Inactive User",
        "role": "member",
    }
    r = api.post(f"{base_url}/users", json=payload)
    user_id = r.json()["id"]
    api.delete(f"{base_url}/users/{user_id}")

    r_list = api.get(f"{base_url}/users")
    user_ids = [u["id"] for u in r_list.json()["users"]]
    assert user_id not in user_ids, "Usuario desactivado no debe aparecer en el listado activo"


def test_create_user_username_too_short(base_url, api):
    """TC-019: Username menor a 3 caracteres retorna 422."""
    payload = {
        "username": "ab",
        "email": f"short_{uuid.uuid4().hex[:8]}@test.com",
        "full_name": "Test",
        "role": "member",
    }
    r = api.post(f"{base_url}/users", json=payload)
    assert r.status_code == 422


def test_create_user_invalid_role(base_url, api):
    """Rol inválido debe ser rechazado."""
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "username": f"user_{suffix}",
        "email": f"user_{suffix}@test.com",
        "full_name": "Test",
        "role": "superadmin",
    }
    r = api.post(f"{base_url}/users", json=payload)
    assert r.status_code in [400, 422], "Rol inválido debe rechazarse"
