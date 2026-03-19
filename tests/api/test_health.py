"""TC-001, TC-002: Tests del endpoint de health check."""


def test_health_returns_200(base_url, api):
    """TC-001: Health check retorna 200 y estado healthy."""
    r = api.get(f"{base_url}/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"


def test_health_includes_version(base_url, api):
    """TC-002: Health check incluye versión de la app."""
    r = api.get(f"{base_url}/health")
    body = r.json()
    assert "version" in body, "El campo 'version' debe estar presente"
    assert body["version"], "La versión no debe estar vacía"


def test_health_includes_environment(base_url, api):
    """Health check incluye el entorno de ejecución."""
    r = api.get(f"{base_url}/health")
    body = r.json()
    assert "environment" in body
