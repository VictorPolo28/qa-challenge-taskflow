# Tests de API — TaskFlow

Tests automatizados para la API REST de TaskFlow usando **pytest + requests**.

## Cobertura

| Módulo | Archivo | Tests |
|--------|---------|-------|
| Health | `test_health.py` | 3 |
| Users | `test_users.py` | 10 |
| Projects | `test_projects.py` | 9 |
| Tasks | `test_tasks.py` | 15 |
| Comments | `test_comments.py` | 5 |
| Stats | `test_stats.py` | 5 |
| Bulk Update | `test_bulk.py` | 4 |
| Export | `test_export.py` | 5 |

## Requisitos

```bash
pip install pytest requests
```

## Ejecución

```bash
# Desde la raíz del proyecto (con la app corriendo):
make test-api

# O directamente:
cd tests/api
pytest -v

# Con reporte de fallos detallado:
pytest -v --tb=short

# Solo tests que fallan:
pytest -v --lf
```

## Convención de tests que documentan bugs conocidos

Los tests que cubren bugs intencionales de la app están marcados con comentarios `BUG-XXX` en el docstring y usan mensajes de assertion descriptivos. **Cuando la app tiene el bug, el test falla** — eso es lo esperado. Al corregir el bug, el test debe pasar.

Ejemplo:
```
FAILED test_projects.py::test_list_projects_excludes_deleted
  AssertionError: BUG-002: Proyecto eliminado aparece en listado por defecto
```

## Estructura de fixtures

Los tests usan fixtures de pytest definidas en `conftest.py`:
- `api` — sesión de requests compartida (scope: session)
- `created_user` — usuario creado + eliminado automáticamente por test
- `created_project` — proyecto + usuario creados y eliminados automáticamente
- `created_task` — tarea + proyecto + usuario creados y eliminados automáticamente

