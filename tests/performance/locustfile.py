"""
Tests de rendimiento con Locust — TaskFlow API
Ejecutar: locust -f locustfile.py --host=http://localhost:8080

Escenarios:
- Load test:   50 usuarios concurrentes por 2 minutos
- Stress test: incrementar hasta encontrar el punto de quiebre
- Spike test:  pico repentino de 100 usuarios
"""
import random
import json
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner


# ─── Setup: crear datos base ─────────────────────────────────────────────────

SHARED_PROJECT_ID = None
SHARED_USER_ID = None


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Crea un proyecto y usuario compartidos para los tests de carga."""
    global SHARED_PROJECT_ID, SHARED_USER_ID

    if isinstance(environment.runner, MasterRunner):
        return  # Solo en modo single o worker

    import requests
    base = environment.host + "/api"

    # Crear usuario
    r = requests.post(f"{base}/users", json={
        "username": "perf_user_001",
        "email": "perf@loadtest.com",
        "full_name": "Perf Test User",
        "role": "member",
    })
    if r.status_code in [201, 409]:
        if r.status_code == 201:
            SHARED_USER_ID = r.json()["id"]
        else:
            # Ya existe — obtener el ID listando
            users = requests.get(f"{base}/users").json()["users"]
            u = next((u for u in users if u["username"] == "perf_user_001"), None)
            if u:
                SHARED_USER_ID = u["id"]

    if not SHARED_USER_ID:
        print("⚠️  No se pudo obtener user para load tests")
        return

    # Crear proyecto
    r = requests.post(f"{base}/projects", json={
        "name": "Proyecto Load Test",
        "description": "Proyecto para tests de rendimiento",
        "owner_id": SHARED_USER_ID,
    })
    if r.status_code == 201:
        SHARED_PROJECT_ID = r.json()["id"]
    else:
        projs = requests.get(f"{base}/projects").json()["projects"]
        p = next((p for p in projs if p["name"] == "Proyecto Load Test"), None)
        if p:
            SHARED_PROJECT_ID = p["id"]


# ─── Usuarios virtuales ────────────────────────────────────────────────────────

class ReadOnlyUser(HttpUser):
    """
    Usuario de solo lectura — simula navegación y consultas del dashboard.
    Peso: 70% del tráfico.
    """
    weight = 7
    wait_time = between(1, 3)

    @task(3)
    def list_tasks(self):
        """GET /api/tasks con paginación."""
        page = random.randint(1, 3)
        with self.client.get(
            f"/api/tasks?page={page}&page_size=20",
            name="/api/tasks [list]",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"Status {r.status_code}")

    @task(2)
    def list_tasks_with_filters(self):
        """GET /api/tasks con filtros de estado y prioridad."""
        status = random.choice(["todo", "in_progress", "done"])
        priority = random.choice(["low", "medium", "high", "critical"])
        with self.client.get(
            f"/api/tasks?status={status}&priority={priority}",
            name="/api/tasks [filtered]",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"Status {r.status_code}")

    @task(2)
    def get_stats(self):
        """GET /api/stats — endpoint más pesado."""
        with self.client.get(
            "/api/stats",
            name="/api/stats",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"Status {r.status_code}")

    @task(1)
    def list_projects(self):
        with self.client.get(
            "/api/projects",
            name="/api/projects [list]",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"Status {r.status_code}")

    @task(1)
    def health_check(self):
        self.client.get("/api/health", name="/api/health")


class WriteUser(HttpUser):
    """
    Usuario de escritura — crea y elimina tareas.
    Peso: 30% del tráfico.
    """
    weight = 3
    wait_time = between(2, 5)

    def on_start(self):
        self.created_task_ids = []

    @task(2)
    def create_task(self):
        """POST /api/tasks."""
        if not SHARED_PROJECT_ID or not SHARED_USER_ID:
            return

        payload = {
            "title": f"Load test task {random.randint(1000, 9999)}",
            "project_id": SHARED_PROJECT_ID,
            "reporter_id": SHARED_USER_ID,
            "priority": random.choice(["low", "medium", "high"]),
        }
        with self.client.post(
            "/api/tasks",
            json=payload,
            name="/api/tasks [create]",
            catch_response=True,
        ) as r:
            if r.status_code == 201:
                task_id = r.json().get("id")
                if task_id:
                    self.created_task_ids.append(task_id)
                r.success()
            else:
                r.failure(f"Status {r.status_code}: {r.text[:100]}")

    @task(1)
    def delete_own_task(self):
        """DELETE /api/tasks/{id} — limpia los recursos creados."""
        if not self.created_task_ids:
            return
        task_id = self.created_task_ids.pop(0)
        with self.client.delete(
            f"/api/tasks/{task_id}",
            name="/api/tasks/{id} [delete]",
            catch_response=True,
        ) as r:
            if r.status_code in [200, 204, 404]:
                r.success()
            else:
                r.failure(f"Status {r.status_code}")

    def on_stop(self):
        """Limpiar tareas restantes al finalizar."""
        for task_id in self.created_task_ids:
            self.client.delete(f"/api/tasks/{task_id}")
