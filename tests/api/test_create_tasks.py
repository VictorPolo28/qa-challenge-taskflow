import requests
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8080/api"
TASKS_URL = f"{BASE_URL}/tasks"

def test_create_task_success():
    """SE valida la creacion de tareas"""
    data = {
        "title": "Implementar autenticacion con JWT",
        "description": "Desarrollar middleware de autenticación usando JSON Web Tokens para proteger las rutas de la API. Incluir renovación de tokens y manejo de expiración.",
        "project_id": "6d216d4d-603c-4f85-a8ff-fae810adfa84",
        "assignee_id": "user_001",
        "reporter_id": "user_002",
        "priority": "low",
        "due_date": "2026-009-15",
        "tags": ["backend", "seguridad", "autenticacion"]
    }

    print(f"\nCreando tarea: {data['title']}")
    response = requests.post(TASKS_URL,json=data)

    #Validacion codigo de respuesta
    assert response.status_code == 201, f"Se esperaba 201, se obtuvo{response.status_code}"
    print ("codigo HTTP 201 correcto")

   # Validacion  Content-Type
    assert response.headers["Content-Type"] == "application/json", "Content-Type incorrecto"
    print(" Content-Type correcto")

    response_data = response.json()
    
    # Validacion 3: Campos obligatorios
    required_fields = ["id","title","reporter_id","project_id"]
    
    for field in required_fields:
        assert field in response_data, f" Campo '{field}' no encontrado en respuesta"
    print("Todos los campos requeridos estan presentes")

    # Validacion 4: Tipos de datos
    assert isinstance(response_data["id"], str), "ID debe ser  string"
    assert isinstance(response_data["title"], str), "title debe ser string"
    assert isinstance(response_data["description"], str), "description debe ser string"
    assert isinstance(response_data["project_id"], str), " project_id debe ser string"
    assert isinstance(response_data["assignee_id"], str), " assignee_id debe ser string"
    assert isinstance(response_data["reporter_id"], str), "reporter_id debe ser string"
    assert isinstance(response_data["priority"], str), "priority debe ser string"
    assert isinstance(response_data["tags"], list), "tags debe ser lista"
    assert isinstance(response_data["status"], str), "status debe ser string"
    print("Tipos de datos correctos")

    # Validacion 5: Valores especificos
    assert response_data["title"] == data["title"], f" Title mismatch: {response_data['title']} != {data['title']}"
    assert response_data["description"] == data["description"], " Description mismatch"
    assert response_data["project_id"] == data["project_id"], "project_id mismatch"
    assert response_data["assignee_id"] == data["assignee_id"], "assignee_id mismatch"
    assert response_data["reporter_id"] == data["reporter_id"], "reporter_id mismatch"
    assert response_data["priority"] == data["priority"], "priority mismatch"
    assert response_data["due_date"] == data["due_date"], "due_date mismatch"
    assert set(response_data["tags"]) == set(data["tags"]), "tags mismatch"
    print("Valores coinciden con lo enviado")

    # Validacion 6: Valores por defecto
    assert response_data["status"] in ["pending", "todo", "open", "created"], "Status inicial incorrecto"
    print(" Status inicial correcto")

    # Validacion 7: Fechas en formato ISO
    try:
        datetime.fromisoformat(response_data["created_at"].replace('Z', '+00:00'))
        print("Fechas en formato correcto")
    except ValueError:
        assert False, "Formato de fecha invalido"

    print(f"\nTarea creada exitosamente con ID: {response_data['id']}")
    return response_data["id"]

def test_create_task_minimal():
    """Prueba la creación con campos minimos requeridos"""
    
    minimal_data = {
        "title": "Tarea mínima",
        "project_id": "6d216d4d-603c-4f85-a8ff-fae810adfa84",
         "reporter_id": "user_002"
        # solo título y project_id son obligatorios
    }
    
    response = requests.post(TASKS_URL, json=minimal_data)
    assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
    
    response_data = response.json()
    assert response_data["title"] == minimal_data["title"]
    assert response_data["project_id"] == minimal_data["project_id"]
    print("Tarea con campos minimos creada correctamente")

def test_create_task_invalid_priority():
    """Prueba con prioridad invalida"""
    
    data = {
        "title": "Tarea con prioridad inválida",
        "project_id": "6d216d4d-603c-4f85-a8ff-fae810adfa84",
        "priority": "ultra-high"  # Prioridad no valida
    }
    
    response = requests.post(TASKS_URL, json=data)
    assert response.status_code in [400, 422], f"Expected 400  or 422, got {response.status_code}"
    print("Validacion de prioridad funciona correctamente")

def test_create_task_invalid_date():
    """Prueba con fecha inválida"""
    
    data = {
        "title": "Tarea con fecha inválida",
        "project_id": "6d216d4d-603c-4f85-a8ff-fae810adfa84",
        "due_date": "2024-13-45"  # Fecha inválida
    }
    
    response = requests.post(TASKS_URL, json=data)
    assert response.status_code in [400,422], f"Expected 400, got {response.status_code}"
    print("Validacion de fecha funciona correctamente")

def test_create_task_missing_required():
    """Prueba con campos requeridos faltantes"""
    
    data = {
        "description": "Tarea sin título ni project_id"  # Faltan campos requeridos
    }
    
    response = requests.post(TASKS_URL, json=data)
    assert response.status_code == 422 or response.status_code == 400, f"Expected 400/422, got {response.status_code}"
    
    # Validar mensaje de error
    error_data = response.json()
    assert "detail" in error_data or "message" in error_data, " Debería incluir detalle del error"
    print(" Validacion de campos requeridos funciona")

def test_create_task_duplicate():
    """Prueba creacion de tarea duplicada (si aplica)"""
    
    data = {
        "title": "Tarea única",
        "project_id": "6d216d4d-603c-4f85-a8ff-fae810adfa84",
        "reporter_id": "user_002"
    }
    
    # Primera creacion
    response1 = requests.post(TASKS_URL, json=data)
    assert response1.status_code in [200, 201]
    
    # Segunda creacion con mismos datos
    response2 = requests.post(TASKS_URL, json=data)
    
   
    if response2.status_code == 409:
        print("El sistema rechaza tareas duplicadas correctamente")
    elif response2.status_code == 201:
        print("El sistema permite tareas duplicadas")
    else:
        assert False, f" Comportamiento inesperado: {response2.status_code}"

def test_create_task_unauthorized():
    """Prueba sin autenticacion (si aplica)"""
    
    data = {
        "title": "Tarea sin auth",
        "project_id": "6d216d4d-603c-4f85-a8ff-fae810adfa84"
    }
    
    # Sin enviar token de autenticacion
    response = requests.post(TASKS_URL, json=data)
    
    # Si el endpoint requiere auth, deberia dar 401
    if response.status_code == 401:
        print(" Autenticacion requerida correctamente")
    else:
        print("El endpoint no requiere autenticacion")

def run_all_tests():
    """Ejecutar todas las pruebas"""
    
    print("=" * 60)
    print(" INICIANDO PRUEBAS DE CREACION DE TAREAS")
    print("=" * 60)
    
    tests = [
        test_create_task_success,
        test_create_task_minimal,
        test_create_task_invalid_priority,
        test_create_task_invalid_date,
        test_create_task_missing_required,
        test_create_task_duplicate,
        test_create_task_unauthorized
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\n--- Ejecutando: {test.__name__} ---")
            test()
            print(f"{test.__name__} PASO")
            passed += 1
        except AssertionError as e:
            print(f" {test.__name__} FALLO: {e}")
            failed += 1
        except Exception as e:
            print(f" {test.__name__} ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f" RESULTADOS: {passed} pasaron, {failed} fallaron")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
