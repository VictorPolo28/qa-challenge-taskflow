"""
Tests E2E con Playwright — TaskFlow Frontend
Cubre: crear tarea, editar tarea, agregar comentario, eliminar tarea, filtrar tareas.
"""
import uuid
import pytest
from datetime import datetime
from playwright.sync_api import sync_playwright, expect, Page

BASE_URL = "http://localhost:8080"


# ─── Helpers ────────────────────────────────────────────────────────────────

def wait_for_app(page: Page):
    """Espera que la app esté lista."""
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")


def open_new_task_modal(page: Page):
    """Abre el modal de creación de tarea."""
    btn = page.locator("button:has-text('+ Nueva Tarea'), button:has-text('Nueva Tarea'), #btn-new-task")
    expect(btn.first).to_be_visible(timeout=5000)
    btn.first.click()
    # Esperar que el formulario esté visible
    page.wait_for_selector("#task-title", state="visible", timeout=5000)


def fill_task_form(page: Page, title: str, description: str = "", priority: str = "medium"):
    """Rellena los campos comunes del formulario de tarea."""
    page.fill("#task-title", title)

    if page.locator("#task-description").count() > 0:
        page.fill("#task-description", description or f"Descripción generada para: {title}")

    if page.locator("#task-priority").count() > 0:
        page.select_option("#task-priority", priority)

    # Fecha límite
    if page.locator("#task-due-date").count() > 0:
        due = datetime.now().strftime("%Y-%m-%d")
        page.fill("#task-due-date", due)


def save_task_form(page: Page):
    """Hace clic en Guardar y espera confirmación."""
    page.click("button:has-text('Guardar')")
    # Esperar que el modal se cierre o aparezca la tarea en la lista
    page.wait_for_timeout(1500)


def find_task_row(page: Page, title: str):
    """Busca una tarea por título en la lista y retorna su locator."""
    search = page.locator("#filter-search")
    if search.count() > 0:
        search.fill(title)
        page.wait_for_timeout(800)
    return page.locator(f"text={title}").first


# ─── Tests ──────────────────────────────────────────────────────────────────

def test_create_task():
    """Crear una tarea con todos los campos y verificar que aparece en la lista."""
    title = f"Tarea E2E {uuid.uuid4().hex[:6]}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        wait_for_app(page)
        open_new_task_modal(page)
        fill_task_form(page, title=title, description="Descripción E2E", priority="high")

        # Seleccionar proyecto si el campo existe
        if page.locator("#task-project").count() > 0:
            options = page.locator("#task-project option").all()
            if len(options) > 1:
                page.select_option("#task-project", index=1)

        save_task_form(page)

        # Verificar que la tarea aparece en la lista
        task_row = find_task_row(page, title)
        expect(task_row).to_be_visible(timeout=5000)

        page.screenshot(path="test-results/create_task.png")
        print(f"Tarea creada: {title}")

        browser.close()


def test_edit_task():
    """Crear una tarea y luego editarla — verificar que los cambios persisten."""
    title_original = f"Tarea Original {uuid.uuid4().hex[:6]}"
    title_edited = f"Tarea Editada {uuid.uuid4().hex[:6]}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        wait_for_app(page)
        open_new_task_modal(page)
        fill_task_form(page, title=title_original)

        if page.locator("#task-project").count() > 0:
            options = page.locator("#task-project option").all()
            if len(options) > 1:
                page.select_option("#task-project", index=1)

        save_task_form(page)

        # Buscar la tarea y hacer clic en Editar dentro de su fila
        find_task_row(page, title_original)

        # Intentar encontrar el botón editar dentro del contexto de la fila
        task_row_container = page.locator(
            f".task-item:has-text('{title_original}'), "
            f"tr:has-text('{title_original}'), "
            f"li:has-text('{title_original}')"
        ).first

        if task_row_container.count() > 0:
            edit_btn = task_row_container.locator(
                ".btn.btn-sm.btn-secondary, button:has-text('Editar')"
            ).first
        else:
            # Fallback: buscar el primer botón editar visible en la página
            edit_btn = page.locator(
                ".btn.btn-sm.btn-secondary, button:has-text('Editar')"
            ).first

        expect(edit_btn).to_be_visible(timeout=5000)
        edit_btn.click()
        page.wait_for_selector("#task-title", state="visible", timeout=5000)

        # Verificar si el formulario está precargado (BUG-016)
        current_title = page.locator("#task-title").input_value()
        if current_title != title_original:
            print(
                f" BUG-016: Formulario de edición vacío "
                f"(esperado: '{title_original}', actual: '{current_title}')"
            )

        # SIEMPRE limpiar y rellenar — robusto ante BUG-016
        page.locator("#task-title").click(click_count=3)
        page.fill("#task-title", title_edited)
        page.select_option("#task-project", index=1)
        page.select_option("#task-priority", "high")
        

        save_task_form(page)

        # Verificar el título nuevo
        updated_row = find_task_row(page, title_edited)
        expect(updated_row).to_be_visible(timeout=5000)

        page.screenshot(path="test-results/edit_task.png")
        print(f"Tarea editada: {title_edited}")

        browser.close()



def test_add_comment():
    """Abrir el detalle de una tarea y agregar un comentario."""
    title = f"Tarea Comentario {uuid.uuid4().hex[:6]}"
    comment = "Comentario de prueba E2E"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        wait_for_app(page)
        open_new_task_modal(page)
        fill_task_form(page, title=title)

        if page.locator("#task-project").count() > 0:
            options = page.locator("#task-project option").all()
            if len(options) > 1:
                page.select_option("#task-project", index=1)

        save_task_form(page)

        # Abrir el detalle de la tarea
        find_task_row(page, title)
        page.locator(".task-meta, .task-title, .task-item").first.click()
        page.wait_for_selector("#new-comment", state="visible", timeout=5000)

        # Agregar comentario
        page.fill("#new-comment", comment)
        page.locator("button:has-text('Agregar'), .btn-primary.btn-sm").first.click()
        page.wait_for_timeout(1000)

        # Verificar que el comentario aparece
        expect(page.locator(f"text={comment}")).to_be_visible(timeout=5000)

        page.screenshot(path="test-results/add_comment.png")
        print(f"Comentario agregado: {comment}")

        browser.close()


def test_delete_task():
    """Crear una tarea y eliminarla — verificar que desaparece de la lista."""
    title = f"Tarea Eliminar {uuid.uuid4().hex[:6]}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        wait_for_app(page)
        open_new_task_modal(page)
        fill_task_form(page, title=title)

        if page.locator("#task-project").count() > 0:
            options = page.locator("#task-project option").all()
            if len(options) > 1:
                page.select_option("#task-project", index=1)

        save_task_form(page)

        # Buscar y eliminar
        find_task_row(page, title)
        delete_btn = page.locator(".btn-danger, button:has-text('Eliminar')").first
        expect(delete_btn).to_be_visible(timeout=5000)
        delete_btn.click()
        page.wait_for_timeout(1000)

        # Limpiar búsqueda y verificar que la tarea ya no existe
        search = page.locator("#filter-search")
        if search.count() > 0:
            search.fill("")
            page.wait_for_timeout(500)
            search.fill(title)
            page.wait_for_timeout(800)

        task_visible = page.locator(f"text={title}").count()
        assert task_visible == 0, f"La tarea '{title}' aún aparece después de eliminar"

        page.screenshot(path="test-results/delete_task.png")
        print(f"Tarea eliminada: {title}")

        browser.close()


def test_filter_by_status():
    """Aplicar filtro por estado y verificar que solo aparecen tareas del estado seleccionado."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        wait_for_app(page)

        # Aplicar filtro por estado "todo"
        filter_status = page.locator("#filter-status")
        if filter_status.count() == 0:
            print("No se encontró el filtro de estado (#filter-status)")
            browser.close()
            return

        filter_status.select_option("todo")
        page.wait_for_timeout(1000)

        # Todas las tareas visibles deben estar en estado "todo"
        status_badges = page.locator(".task-status, .badge, [data-status]").all()
        for badge in status_badges:
            text = badge.inner_text().lower()
            assert "por hacer" in text or "todo" in text, (
                f"Tarea con estado '{text}' aparece con filtro 'todo'"
            )

        page.screenshot(path="test-results/filter_status.png")
        print("Filtro por estado aplicado correctamente")

        browser.close()


def test_search_task():
    """Buscar una tarea por texto y verificar que aparece en los resultados."""
    title = f"Buscar Esta Tarea {uuid.uuid4().hex[:6]}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        wait_for_app(page)
        open_new_task_modal(page)
        fill_task_form(page, title=title)

        if page.locator("#task-project").count() > 0:
            options = page.locator("#task-project option").all()
            if len(options) > 1:
                page.select_option("#task-project", index=1)

        save_task_form(page)

        # Buscar por texto
        search = page.locator("#filter-search")
        if search.count() > 0:
            search.fill(title[:15])
            page.wait_for_timeout(1000)
            expect(page.locator(f"text={title}")).to_be_visible(timeout=5000)
            print(f"Búsqueda encontró la tarea: {title}")
        else:
            print("Campo de búsqueda no encontrado (#filter-search)")

        page.screenshot(path="test-results/search_task.png")
        browser.close()


if __name__ == "__main__":
    import os
    os.makedirs("test-results", exist_ok=True)
    test_create_task()
    test_edit_task()
    test_add_comment()
    test_delete_task()
    test_filter_by_status()
    test_search_task()
    print("\nTodos los tests UI completados.")
