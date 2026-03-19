from playwright.sync_api import sync_playwright
from datetime import datetime
import time

def test_automatic_tasks():
    
    with sync_playwright() as p:
        # 2. Lanzar navegador 
        browser = p.chromium.launch(headless=False, slow_mo=500)  # slow_mo hace pausas de 500ms para ver mejor
        page = browser.new_page()
        
        # 3. Ir a la aplicación
        page.goto("http://localhost:8080/")
        
        # 4. Pausa para ver dónde estamos (opcional)
        page.wait_for_timeout(2000)
        
       #Crear tarea
def test_create_task():
    print("Iniciando prueba de creación de tarea...")
    
    with sync_playwright() as p:
        # Lanzar navegador
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("Navegando a la página principal...")
        page.goto("http://localhost:8080/")
        
        # Esperar a que cargue
        page.wait_for_load_state("networkidle")
        
        # Buscar y hacer clic en botón "Nueva Tarea"
        print("Buscando botón para crear tarea")
        
        # Intentar diferentes selectores comunes
        if page.locator("text=+ Nueva Tarea").count() > 0:
            page.click("text=+ Nueva Tarea")
        elif page.locator("#btn-new-task").count() > 0:
            page.click("#btn-new-task")
        elif page.locator("button:has-text('+ Nueva Tarea')").count() > 0:
            page.click("button:has-text('+ Nueva Tarea')")
        else:
            print("No se encontró boton de crear, intentando con el primer enlace...")
            page.click("a:has-text('+ Nueva Tarea')")
        
        # Esperar que aparezca el formulario
        page.wait_for_timeout(1000)
        
        # Llenar el formulario
        print("Llenando formulario de tarea")
        
        # Título de la tarea
        page.fill("#task-title", "Mi tarea automatizada")
     
        
        # Descripción 
        if page.locator("#task-description").count() > 0:
            page.fill("#task-description", "Esta tarea fue creada por Playwright")
            page.wait_for_timeout(3000)
        else:
            print("Error al ingrasar la descripcion")    
            
        # Seleccionar proyecto 
        if page.locator("#task-project").count() > 0:
            page.select_option("#task-project", "6d216d4d-603c-4f85-a8ff-fae810adfa84")
            page.wait_for_timeout(3000)
        else:
             print("Error al seleccionar el proyecto") 
        # Prioridad
        if page.locator("#task-priority").count() > 0:
            page.select_option("#task-priority", "high")
            page.wait_for_timeout(3000)
        else:
             print("Error al seleccionar la prioridad")     

        #asignar    
        if page.locator("#task-assignee").count() > 0:
            page.select_option("#task-assignee", "Laura Martínez")
            page.wait_for_timeout(3000)

        #fecha
        today = datetime.now().strftime("%Y-%m-%d")

        if page.locator("#task-due-date").count() > 0:
            page.fill("#task-due-date", today)
            page.wait_for_timeout(3000)
        else:
             print("Error al seleccionar la fecha")     

        #tags
        if page.locator("#task-tags").count() > 0:
            page.fill("#task-tags", "front-pruebas-bugs")
            page.wait_for_timeout(3000)
        else:
             print("Error al ingresar  las etiquetas")     

        # Guardar
        print(" Guardando tarea.")
        page.click("button:has-text('Guardar')")
        page.wait_for_timeout(3000)
      
     
        # Esperar confirmación
        page.wait_for_timeout(2000)
        
        # Tomar screenshot como evidencia
        page.screenshot(path="test-results/tarea-creada.png")
        print("Tarea creada exitosamente!")
        print("Screenshot guardado en test-results/tarea-creada.png")
        
      
      

def test_delete_task():
    print("Iniciando prueba de busqueda de tarea...")
    
    with sync_playwright() as p:
        # Lanzar navegador
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("Navegando a la página principal...")
        page.goto("http://localhost:8080/")
        
        # Esperar a que cargue
        page.wait_for_load_state("networkidle")

        #buscar   
        if page.locator("#filter-search").count() > 0:
            page.fill("#filter-search", "Mi tarea automatizada")
            print("Buscando la tarea...")
            page.wait_for_timeout(3000)
            page.locator(".btn.btn-sm.btn-danger").first.click()
            print("Eliminando la tarea...")
            page.wait_for_timeout(3000)
        else:
             print("Error al buscar y/o eliminar la tarea") 

def test_add_task_coments():
    print("Iniciando prueba de agregar comentario a la tarea...")
    
    with sync_playwright() as p:
        # Lanzar navegador
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("Navegando a la página principal...")
        page.goto("http://localhost:8080/")
        
        # Esperar a que cargue
        page.wait_for_load_state("networkidle")
         #buscar   
        if page.locator("#filter-search").count() > 0:
            page.fill("#filter-search", "Mi tarea automatizada")
            print("Buscando la tarea...")
            page.wait_for_timeout(3000)
            page.locator(".task-meta").first.click()
            print("entrando a gregar comentario a la tarea...")
            page.wait_for_timeout(3000)
        else:
             print("Error al buscar y/o selecionar la tarea la tarea") 

        print("Agregando comentario") 

        if page.locator("#new-comment").count() > 0:
            page.fill("#new-comment", "Estes es un nuevo comentario")
            page.locator(".btn.btn-primary.btn-sm").first.click()
            page.wait_for_timeout(3000)
        else:
             print("Error al agregar comentario")     



def test_edit_task():
    print("Iniciando prueba de filtro de tarea...")
    
    with sync_playwright() as p:
        # Lanzar navegador
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("Navegando a la página principal...")
        page.goto("http://localhost:8080/")
        
        # Esperar a que cargue
        page.wait_for_load_state("networkidle")
         #buscar   
        if page.locator("#filter-search").count() > 0:
            page.fill("#filter-search", "Mi tarea automatizada")
            print("Buscando la tarea...")
            page.wait_for_timeout(3000)
            page.locator(".btn.btn-sm.btn-secondary").first.click()
            print("entrando a editar la tarea...")
            page.wait_for_timeout(3000)
        else:
             print("Error al buscar y/o editar la tarea") 

        print("Llenando formulario de tarea")

        
        
        # Título de la tarea
        page.fill("#task-title", "Mi tarea automatizada editada")
     
        
        # Descripción 
        if page.locator("#task-description").count() > 0:
            page.fill("#task-description", "Esta tarea fue creada por Playwright  y luego editada")
            page.wait_for_timeout(3000)
        else:
            print("Error al ingrasar la descripcion")    
            
        # Seleccionar proyecto 
        if page.locator("#task-project").count() > 0:
            page.select_option("#task-project", "6d216d4d-603c-4f85-a8ff-fae810adfa84")
            page.wait_for_timeout(3000)
        else:
             print("Error al seleccionar el proyecto") 
        # Prioridad
        if page.locator("#task-priority").count() > 0:
            page.select_option("#task-priority", "low")
            page.wait_for_timeout(3000)
        else:
             print("Error al seleccionar la prioridad")     

        #asignar    
        if page.locator("#task-assignee").count() > 0:
            page.select_option("#task-assignee", "Laura Martínez")
            page.wait_for_timeout(3000)

        #fecha
        today = datetime.now().strftime("%Y-%m-%d")

        if page.locator("#task-due-date").count() > 0:
            page.fill("#task-due-date", today)
            page.wait_for_timeout(3000)
        else:
             print("Error al seleccionar la fecha")     

        #tags
        if page.locator("#task-tags").count() > 0:
            page.fill("#task-tags", "front-pruebas-bugs")
            page.wait_for_timeout(3000)
        else:
             print("Error al ingresar  las etiquetas")     

        # Guardar
        print(" Guardando tarea.")
        page.click("button:has-text('Guardar')")
        page.wait_for_timeout(3000)
      
     
        # Esperar confirmación
        page.wait_for_timeout(2000)
        
        # Tomar screenshot como evidencia
        page.screenshot(path="test-results/tarea-creada.png")
        print("Tarea creada exitosamente!")
        print("Screenshot guardado en test-results/tarea-creada.png")     

def test_filter_task():       
    print("Iniciando prueba de filtro de tarea...")
    
    with sync_playwright() as p:
        # Lanzar navegador
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("Navegando a la página principal...")
        page.goto("http://localhost:8080/")
        
        # Esperar a que cargue
        page.wait_for_load_state("networkidle")    

        if page.locator("#filter-project").count() > 0:
            page.select_option("#filter-project", "Test de pruebas")
            page.wait_for_timeout(3000)
        else:
            print("Error al selecionar proyecto")   

        if page.locator("#filter-status").count() > 0:
            page.select_option("#filter-status", "Por Hacer")
            page.wait_for_timeout(3000)
        else:
            print("Error al selecionar estado")  

        if page.locator("#filter-priority").count() > 0:
            page.select_option("#filter-priority", "Media")
            page.wait_for_timeout(3000)
        else:
            print("Error al selecionar prioridad")        
          



if __name__ == "__main__":
    test_create_task()
    test_edit_task()
    test_add_task_coments()
    test_delete_task()
    test_filter_task()
    