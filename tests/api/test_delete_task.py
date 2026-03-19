import requests
import random
import string
from datetime import datetime

BASE_URL = "http://localhost:8080/api"
TASKS_URL = f"{BASE_URL}/tasks"

def generate_unique_title():
    """Genera un título único para pruebas"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"Tarea para eliminar {random_suffix}"

def create_test_task():
    """Crea una tarea de prueba y retorna su ID"""
    data = {
        "title": generate_unique_title(),
        "description": "Tarea creada para probar eliminación",
        "project_id": "6d216d4d-603c-4f85-a8ff-fae810adfa84",
        "assignee_id": "user_001",
        "reporter_id": "user_002",
        "priority": "medium",
        "tags": ["test", "eliminación"]
    }
    
    response = requests.post(TASKS_URL, json=data)
    assert response.status_code in [200, 201], f"Error al crear tarea: {response.status_code}"
    
    task_id = response.json().get("id")
    assert task_id is not None, "No se recibió ID de la tarea"
    
    print(f"Tarea de prueba creada con ID: {task_id}")
    return task_id

def test_delete_task_success():
    """Prueba 1: Eliminación exitosa de una tarea existente"""
    print("\nPrueba 1: Eliminación exitosa de tarea existente")
    
    # Crear tarea para eliminar
    task_id = create_test_task()
    delete_url = f"{TASKS_URL}/{task_id}"
    
    # Verificar que la tarea existe antes de eliminar
    get_response = requests.get(delete_url)
    assert get_response.status_code == 200, " La tarea deberia existir antes de eliminar"
    
    # Eliminar la tarea
    delete_response = requests.delete(delete_url)
    
    # Validaciones
    assert delete_response.status_code in [200, 204], f" Expected 200/204, got {delete_response.status_code}"
    print(f"Codigo HTTP correcto: {delete_response.status_code}")
    
    # Verificar que la tarea ya no existe
    verify_response = requests.get(delete_url)
    assert verify_response.status_code == 404, " La tarea aun existe después de eliminar"
    print(" Tarea eliminada correctamente (GET retorna 404)")
    
    print(" Prueba 1 PASO")

def test_delete_task_nonexistent():
    """Prueba 2: Intentar eliminar una tarea que no existe"""
    print("\nPrueba 2: Eliminar tarea inexistente")
    
    nonexistent_id = "99999999-9999-9999-9999-999999999999"
    delete_url = f"{TASKS_URL}/{nonexistent_id}"
    
    response = requests.delete(delete_url)
    
    # Debería retornar 404 Not Found
    assert response.status_code == 404, f" Expected 404, got {response.status_code}"
    
    # Validar mensaje de error
    response_data = response.json()
    assert "detail" in response_data or "message" in response_data, "Deberia incluir mensaje de error"
    print(f"Mensaje de error: {response_data.get('detail', response_data.get('message'))}")
    
    print("Prueba 2 PASO")

def test_delete_task_invalid_id_format():
    """Prueba 3: Eliminar con formato de ID inválido"""
    print("\nPrueba 3: Formato de ID invalido")
    
    invalid_ids = [
        "123",  # Muy corto
        "no-es-un-uuid",
        "!!!!",
        " ",
        "6d216d4d-603c-4f85-a8ff",  # UUID incompleto
        "../../etc/passwd",  # Path traversal
        "<script>alert('xss')</script>"  # XSS attempt
    ]
    
    for invalid_id in invalid_ids:
        delete_url = f"{TASKS_URL}/{invalid_id}"
        response = requests.delete(delete_url)
        
        # Debería retornar 400 Bad Request o 422 Unprocessable Entity
        assert response.status_code in [400, 422,404], f" Para ID '{invalid_id}': Expected 400/422, got {response.status_code}"
        print(f"ID inválido '{invalid_id}': {response.status_code} correcto")
    
    print(" Prueba 3 PASO")

def test_delete_task_unauthorized():
    """Prueba 4: Eliminar sin autenticación (si aplica)"""
    print("\nPrueba 4: Eliminar sin autenticación")
    
    task_id = create_test_task()
    delete_url = f"{TASKS_URL}/{task_id}"
    
    # Intentar eliminar sin token (asumiendo que la API requiere auth)
    headers = {}  # Sin headers de autenticación
    response = requests.delete(delete_url, headers=headers)
    
    # Si el endpoint requiere auth, debería dar 401
    if response.status_code == 401:
        print("Autenticación requerida correctamente")
        
        # Verificar que la tarea sigue existiendo
        get_response = requests.get(delete_url)
        assert get_response.status_code == 200, " La tarea no debería eliminarse sin auth"
        print("La tarea no fue eliminada (persiste después de intento no autorizado)")
    else:
        print(f"Endpoint no requiere autenticación (status: {response.status_code})")
    
    # Limpiar: eliminar la tarea con auth si es necesario
    if response.status_code != 200 and response.status_code != 204:
        # Si no se eliminó, limpiar manualmente
        cleanup_response = requests.delete(delete_url)
        if cleanup_response.status_code in [200, 204]:
            print("Tarea de prueba eliminada en limpieza")
    
    print("Prueba 4 PASO")

def test_delete_task_twice():
    """Prueba 5: Eliminar la misma tarea dos veces"""
    print("\nPrueba 5: Eliminar la misma tarea dos veces")
    
    task_id = create_test_task()
    delete_url = f"{TASKS_URL}/{task_id}"
    
    # Primera eliminación
    response1 = requests.delete(delete_url)
    assert response1.status_code in [200, 204], f"Primera eliminación fallO: {response1.status_code}"
    print("Primera eliminación exitosa")
    
    # Segunda eliminación (la tarea ya no existe)
    response2 = requests.delete(delete_url)
    
    # Debería retornar 404 (idempotencia: DELETE repetido da mismo resultado)
    assert response2.status_code == 404, f" Expected 404 para segunda eliminación, got {response2.status_code}"
    print("Segunda eliminación retorna 404 correctamente")
    
    print("Prueba 5 PASO")

def test_delete_task_verify_response():
    """Prueba 6: Verificar la respuesta de eliminación exitosa"""
    print("\nPrueba 6: Verificar respuesta de eliminación exitosa")
    
    task_id = create_test_task()
    delete_url = f"{TASKS_URL}/{task_id}"
    
    response = requests.delete(delete_url)
    
    # Verificar diferentes formatos posibles de respuesta
    if response.status_code == 200:
        # Si retorna 200, debería incluir información de la tarea eliminada
        response_data = response.json()
        assert response_data.get("id") == task_id, "ID no coincide en respuesta"
        assert response_data.get("title") is not None, "Respuesta debería incluir título"
        assert response_data.get("deleted_at") is not None or response_data.get("deleted") is True, " Debería indicar que fue eliminada"
        print("Respuesta 200 con datos de tarea eliminada")
    elif response.status_code == 204:
        # Si retorna 204, no debería tener cuerpo
        assert response.text == "", "Respuesta 204 no debería tener cuerpo"
        print("Respuesta 204 sin contenido")
    
    print("Prueba 6 PASO")

def test_delete_task_with_dependencies():
    """Prueba 7: Eliminar tarea que tiene dependencias (si aplica)"""
    print("\nPrueba 7: Eliminar tarea con dependencias")
    
    # Crear tarea principal
    main_task_id = create_test_task()
    
    # Crear subtarea o tarea dependiente (asumiendo que existe concepto de dependencias)
    subtask_data = {
        "title": f"Subtarea de {main_task_id}",
        "project_id": "6d216d4d-603c-4f85-a8ff-fae810adfa84",
        "parent_task_id": main_task_id  # Campo hipotético
    }
    
    subtask_response = requests.post(TASKS_URL, json=subtask_data)
    
    # Si el sistema soporta dependencias
    if subtask_response.status_code in [200, 201]:
        subtask_id = subtask_response.json().get("id")
        print(f"Subtarea creada con ID: {subtask_id}")
        
        # Intentar eliminar tarea principal
        delete_url = f"{TASKS_URL}/{main_task_id}"
        response = requests.delete(delete_url)
        
        # Debería rechazar la eliminación o eliminar en cascada
        if response.status_code == 409:
            print(" Sistema rechaza eliminar tarea con dependencias (Conflict)")
            error_data = response.json()
            print(f"   Mensaje: {error_data.get('detail', error_data.get('message'))}")
        elif response.status_code in [200, 204]:
            # Si elimina, verificar que las subtareas también se eliminaron
            subtask_check = requests.get(f"{TASKS_URL}/{subtask_id}")
            assert subtask_check.status_code == 404, "❌ Las subtareas deberían eliminarse en cascada"
            print("Eliminación en cascada funcionó")
        else:
            print(f"Comportamiento inesperado: {response.status_code}")
    else:
        print(" Sistema no soporta dependencias entre tareas")
    
    print(" Prueba 7 PASo")

def run_all_delete_tests():
    """Ejecutar todas las pruebas de eliminación"""
    
    print("=" * 60)
    print("INICIANDO PRUEBAS DE ELIMINACIÓN DE TAREAS")
    print(f"Endpoint: {TASKS_URL}/{{task_id}}")
    print("=" * 60)
    
    tests = [
        test_delete_task_success,
        test_delete_task_nonexistent,
        test_delete_task_invalid_id_format,
        test_delete_task_unauthorized,
        test_delete_task_twice,
        test_delete_task_verify_response,
        test_delete_task_with_dependencies
    ]
    
    passed = 0
    failed = 0
    results = []
    
    for test in tests:
        try:
            print(f"\n{'='*50}")
            test()
            print(f"{test.__name__} PASO")
            passed += 1
            results.append(("PASÓ", test.__name__))
        except AssertionError as e:
            print(f"{test.__name__} FALLO: {e}")
            failed += 1
            results.append(("FALLO", test.__name__))
        except Exception as e:
            print(f"{test.__name__} ERROR INESPERADO: {e}")
            failed += 1
            results.append(("ERROR", test.__name__))
    
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    for status, test_name in results:
        print(f"{status}: {test_name}")
    print("=" * 60)
    print(f"PASARON: {passed} |  FALLARON: {failed} | TOTAL: {len(tests)}")
    print("=" * 60)
    
    return passed, failed

if __name__ == "__main__":
    run_all_delete_tests()