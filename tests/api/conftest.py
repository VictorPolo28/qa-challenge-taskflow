"""
Fixtures compartidas para los tests de API de TaskFlow.
"""
import uuid
import pytest
import requests

BASE_URL = "http://localhost:8080/api"


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def api(base_url):
    """Session de requests reutilizable."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    # Verificar que la API está disponible antes de correr los tests
    try:
        r = session.get(f"{base_url}/health", timeout=5)
        assert r.status_code == 200, "API no disponible. Ejecutar: make start"
    except requests.exceptions.ConnectionError:
        pytest.exit("No se puede conectar a la API en localhost:8080. Ejecutar: make start")
    return session


@pytest.fixture
def created_user(base_url, api):
    """Crea un usuario de prueba y lo elimina al finalizar el test."""
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "username": f"test_{suffix}",
        "email": f"test_{suffix}@qa.test",
        "full_name": f"Test User {suffix}",
        "role": "member",
    }
    r = api.post(f"{base_url}/users", json=payload)
    assert r.status_code == 201, f"No se pudo crear usuario de prueba: {r.text}"
    user = r.json()
    yield user
    # Teardown: soft-delete
    api.delete(f"{base_url}/users/{user['id']}")


@pytest.fixture
def created_project(base_url, api, created_user):
    """Crea un proyecto de prueba y lo elimina al finalizar el test."""
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "name": f"Proyecto Test {suffix}",
        "description": "Proyecto creado por fixture de prueba",
        "owner_id": created_user["id"],
    }
    r = api.post(f"{base_url}/projects", json=payload)
    assert r.status_code == 201, f"No se pudo crear proyecto de prueba: {r.text}"
    project = r.json()
    yield project
    # Teardown
    api.delete(f"{base_url}/projects/{project['id']}")


@pytest.fixture
def created_task(base_url, api, created_project, created_user):
    """Crea una tarea de prueba y la elimina al finalizar el test."""
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "title": f"Tarea Test {suffix}",
        "description": "Tarea creada por fixture de prueba",
        "project_id": created_project["id"],
        "reporter_id": created_user["id"],
        "priority": "medium",
        "tags": ["test"],
    }
    r = api.post(f"{base_url}/tasks", json=payload)
    assert r.status_code == 201, f"No se pudo crear tarea de prueba: {r.text}"
    task = r.json()
    yield task
    # Teardown
    api.delete(f"{base_url}/tasks/{task['id']}")