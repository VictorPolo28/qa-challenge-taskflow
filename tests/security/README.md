# Hallazgos de Seguridad — TaskFlow

Análisis de seguridad básico sobre la API REST de TaskFlow.

---

## SEC-001: Inyección SQL en parámetro de búsqueda

**Severidad:** Crítica
**Endpoint:** `GET /api/tasks?search=`
**OWASP:** A03:2021 – Injection

### Descripción
El parámetro `search` se interpola directamente en la query SQL sin parametrizar:

```python
# Código vulnerable (main.py ~línea 393)
conditions.append(f"(title LIKE '%{search}%' OR description LIKE '%{search}%')")
```

### Prueba de concepto
```bash
# Retorna TODAS las tareas (inyección exitosa):
curl "http://localhost:8080/api/tasks?search=%27%20OR%20%271%27%3D%271"
# Equivale a: search=' OR '1'='1

# Intento de exfiltración de datos:
curl "http://localhost:8080/api/tasks?search=%27%20UNION%20SELECT%20*%20FROM%20users%20--"
```

### Resultado observado
La búsqueda con `' OR '1'='1` retorna todos los registros de la tabla, confirmando la inyección.

### Remediación
Usar parámetros posicionales SQLite:
```python
conditions.append("(title LIKE ? OR description LIKE ?)")
params.extend([f"%{search}%", f"%{search}%"])
```

---

## SEC-002: CORS misconfiguration — wildcard con credentials

**Severidad:** Alta
**Componente:** Configuración CORS (main.py)
**OWASP:** A05:2021 – Security Misconfiguration

### Descripción
La configuración simultánea de `allow_origins=["*"]` y `allow_credentials=True` viola el estándar CORS (RFC 6454). Los navegadores modernos rechazan esta combinación, pero si en el futuro se reemplaza `"*"` por dominios específicos sin revisar, puede habilitar ataques CSRF cross-origin.

```python
# Configuración vulnerable (main.py ~línea 36-42)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Problema: wildcard
    allow_credentials=True,     # Problema: combinado con wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Remediación
Restringir a dominios conocidos:
```python
allow_origins=["https://app.taskflow.com"],
allow_credentials=True,
```

---

## SEC-003: Sin autenticación ni autorización en ningún endpoint

**Severidad:** Crítica
**Componente:** Todos los endpoints
**OWASP:** A01:2021 – Broken Access Control

### Descripción
Cualquier cliente puede crear, leer, modificar y eliminar cualquier recurso sin autenticación. No hay tokens JWT, sesiones, API keys ni ningún mecanismo de identificación de usuario.

### Prueba de concepto
```bash
# Eliminar una tarea sin ninguna credencial:
curl -X DELETE "http://localhost:8080/api/tasks/CUALQUIER-ID"

# Crear usuario con cualquier rol:
curl -X POST "http://localhost:8080/api/users" \
  -H "Content-Type: application/json" \
  -d '{"username":"hacker","email":"h@h.com","full_name":"Hacker","role":"admin"}'
```

### Remediación
Implementar autenticación JWT o OAuth2. Validar que el usuario autenticado tenga permisos sobre el recurso solicitado antes de cada operación.

---

## SEC-004: Sin rate limiting

**Severidad:** Media
**Componente:** Todos los endpoints
**OWASP:** A05:2021 – Security Misconfiguration

### Descripción
La API no implementa ningún mecanismo de limitación de tasa. Es posible enviar miles de peticiones por segundo sin ser bloqueado.

### Prueba de concepto
```bash
# Enumerar todos los usuarios con fuerza bruta:
for i in $(seq 1 1000); do
  curl -s "http://localhost:8080/api/users/$i" &
done
```

### Remediación
Implementar rate limiting a nivel de middleware (e.g., `slowapi` para FastAPI):
- Máximo 100 requests/minuto por IP para endpoints de lectura
- Máximo 20 requests/minuto por IP para endpoints de escritura

---

## SEC-005: Errores internos exponen información de la base de datos

**Severidad:** Media
**Componente:** Manejo de errores
**OWASP:** A05:2021 – Security Misconfiguration

### Descripción
Ciertos errores retornan el mensaje de excepción interno de SQLite con detalles sobre la estructura de la base de datos:

```bash
curl -X POST "http://localhost:8080/api/users" \
  -d '{"username":"x","email":"x@x.com","full_name":"x","role":"INVALID_ROLE"}'
```

La respuesta puede incluir: `CHECK constraint failed: users` revelando el nombre de la tabla y la restricción.

### Remediación
Capturar excepciones genéricas y retornar mensajes de error genéricos al cliente. Loggear el detalle interno del error solo en el servidor.

---

## Resumen

| ID | Descripción | Severidad | OWASP |
|----|-------------|-----------|-------|
| SEC-001 | SQL Injection en search | Crítica | A03 |
| SEC-002 | CORS wildcard + credentials | Alta | A05 |
| SEC-003 | Sin autenticación/autorización | Crítica | A01 |
| SEC-004 | Sin rate limiting | Media | A05 |
| SEC-005 | Stack traces en respuestas de error | Media | A05 |

**Conclusión:** La aplicación en su estado actual **no es apta para producción**. Los hallazgos SEC-001 y SEC-003 son de prioridad máxima y deben resolverse antes de cualquier despliegue.

