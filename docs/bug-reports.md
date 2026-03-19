 ### BUG-001: No hay boton que  permita crear proyectos  para asignar tareas
- Severidad: Alta
- Componente: API
- Endpoint: POST/api/projects

Precondiciones:
API activa

Pasos:
1. abrir la palicacion  
2. intentar crear un proyecto

Resultado actual:
no existe boton  u opcion para crear el proyecto

Resultado esperado:
sedebe  mostrar un opcion  para crear  un proyecto al ususario

Impacto:
No permite el correcto uso de app  al user

### BUG-002: No hay opcion  de eliminar o editar proyectos 
- Severidad: Alta
- Componente: API
- Endpoint: DELETE//api/projects/{project_id}

Precondiciones:
API activa

Pasos:
1. abrir la palicacion  
2. intentar crear un proyecto y o validar un proyecto existente
3. intentar eliminar el proyecto creado

Resultado actual:
no existe boton  u opcion para crear el proyecto

Resultado esperado:
sedebe  mostrar un opcion  para crear  un proyecto al ususario


Impacto:
No permite eliminar proyectos innecesarios para el user  creados por error en la app

### BUG-003: DELETE /api/projects/{id} retorna 200 para proyectos existentes pero en el front continua visible el projecto
 
- Severidad:Alta  
- Componente:API  
- Endpoint:DELETE /api/projects/{id}  

Precondiciones:
- Proyecto existente con un id valido

Pasos para reproducir:
1. Ir a Swagger `/docs`
2. Ejecutar GET /api/projects/{project_id} y obtener un ID válido
3. Ejecutar DELETE /api/projects/{id} con ese ID

Resultado actual:
- Respuesta: 200 sin embargo el  proyecto continue siendo visible en el front

Resultado esperado:
- Respuesta: 200 OK y que el proyecto deje de ser visble en el listado de proyectos
- Proyecto eliminado correctamente

Evidencia:
Request:
DELETE /api/projects/6d216d4d-603c-4f85-a8ff-fae810adfa84

Response:
200 ok

Impacto:
No es posible eliminar proyectos  

sugerencia:
Validar existencia del proyecto antes de eliminar o corregir lógica del endpoint



### BUG-004: Permite duplicar nombre de proyectos
- Severidad: Alta
- Componente: API
- Endpoint: POST/api/projects

Precondiciones:
API activa

Pasos:
1. crear  un proyecto directamente   usando  el endpoint como los mismos caracteres  de proyecto existente 
2.  selecionar Execute  y validar que se obtuvo   respuesta  200

Resultado actual:
se recibe estado 200

Resultado esperado:
No permitir crear proyectos con extamente  el mismo nombre y caracteres

Impacto:
Crear  confuncion  en la validacion de proyectos para el  usuario ya que no hay  ninguna diferencia entre nombres de proyectos 

### BUG-005: No hay limitacionde caracteres  para la descripcion en las tareas
- Severidad: Alta
- Componente: API
- Endpoint: POST/api/projects

Precondiciones:
API activa

Pasos:
1. selecionar el boton crear tarea
2.  ingresar  en  el campo de descripcion  una  descrion  que  contenga mas de mil  caracteres
3. llenar los campos requeridos  y confirmar la creacion de la tarea   con  todos los caracteres

Resultado actual:
permite ingresar  una descripcion  de mas de mil  caracteres

Resultado esperado:
Tener rescricion de  cantidad   de caracteres caracteres

Impacto:
satura de informacion las tareas crea  confusion  para los usuarios 

### BUG-006: API permite crear tareas sin usuario asignado sin validación

- Severidad: Media
- Componente: API

Resultado actual:
Se permite crear tareas sin campo "assignee_id"

Resultado esperado:
Definir si el campo es obligatorio o manejar estado "sin asignar"

Impacto:
Ambigüedad en responsabilidades de tareas

### BUG-007: Eliminación de tareas sin confirmación en UI

- Severidad: Media  
- Componente: Frontend  
- Pantalla: Lista de tareas  

Pasos:
1. Crear una tarea
2. Click en eliminar

Resultado actual:
La tarea se elimina inmediatamente

Resultado esperado:
Mostrar modal de confirmación antes de eliminar

Impacto:
Riesgo de eliminación accidental de datos

### BUG-008: Orden de  el nivel de prioridad no es coherente 
- Severidad:  baja
- Componente: Campo prioridad
- Endpoint: PUT/api/tasks/{task_id}

Precondiciones:
API activa

Pasos:
1. Dar click  en el boton crear tarea 
2. Selecionar prioridad
3. Se identifica el orden  "Media,Baja,Alta,Critica"


Resultado actual:
Se   obtiene el orden Media,Baja,Alta,Critica

Resultado esperado:
 Se  espera obtener   el orden  correcto "Baja,Mdeia,Alta,Critica"

Impacto:
Bajo pero genera incomodidad  visual  a los usuarios por no seguir el orden regularmente establecido


### BUG-009: Crear tareas sin descripcion asignada
- Severidad: Alta
- Componente: Campo descripcion
- Endpoint: PUT/api/tasks/{task_id}

Precondiciones:
API activa

Pasos:
1. Dar click  en el boton crear tarea 
2. selecionar el titulo y los otros campos  excepto la descripcion
3. click en el boton guardar


Resultado actual:
Se crear  una tarea sin descripcion alguna

Resultado esperado:
 Solicitar al usuario el ingreso de una descripcion hacerca de la tarea 

Impacto:  crear tareas  de las  cuales no se tiene cotexto  hacerca  del motivo de la creacion  o de la solucitud   detallada  de la tarea 

### BUG-010: Crear tareas sin fecha asignada
- Severidad: Media
- Componente: Fecnha limite
- Endpoint: PUT/api/tasks/{task_id}

Precondiciones:
API activa

Pasos:
1. Dar click  en el boton crear tarea 
2. selecionar el titulo y los otros campos  excepto la fecha
3. click en el boton guardar

Resultado actual:
Permite crear las tareas  sin fechas asignadas

Resultado esperado:
 Solicitar al usuario el  asginar una fecha estimada  de manera obligatoria para la resolucion de la tarea 

Impacto: Se crean tareas  sin fechas asignadas no acordes a las prioridades que el cliente pueda asignar a la tarea 

### BUG-011: Crear tareas sin etiquetas
- Severidad: Media
- Componente: Etiqeutas
- Endpoint: PUT/api/tasks/{task_id}

Precondiciones:
API activa

Pasos:
1. Dar click  en el boton crear tarea 
2. selecionar el titulo y los otros campos  excepto la etiqueta
3. click en el boton guardar

Resultado actual:
Permite crear las tareas  sin etiquetas asignadas

Resultado esperado:
 Solicitar al usuario el  asginar una etiqueta sea  relevante para el desarrollo de la tarea  y o la solucion de esta misma

Impacto: Se crean tareas  sin etiquetas para identificar  puntos relevantes para la solucion.


### BUG-012: Edicion de las tareas
- Severidad: Alta
- Componente: Boton de editar
- Endpoint: GET/api/tasks/{task_id}

Precondiciones:
API activa

Pasos:
1. selecionar editar a una tarea previamente creada
2. Validar que la informacion de la tarea se muestra completamente vacia  y requiere toda la informacion  nuevamnete   en caso de querer editar so una seccion de la tarea


Resultado actual:
La tarea solicita toda la informacion nuevamente no unicamente la parte que  se desee editar


Resultado esperado:
 La  tarea mostrar  toda  la informacion  ingresada  previamente  y permitira al usuario cambiar  solo una o muchas partes de la tarea sin necesesidad de tener ingresar toda la informacion  nuevamente

Impacto: Obliga al usuario  a relizar reprocesos  al llenar nuevamente la tarea  con la misma informacion anterior

### BUG-013: El input de  comentarios 
- Severidad: Media
- Componente: Comentarios
- Endpoint: POST/api/tasks/{task_id}/comments

Precondiciones:
Tarea  creada previamente existente

Pasos:
1. selecionar una tarea previamente creada para actualizacion  y o gragar comentarios
2. agregar un comentario extenso  donde se identifique que el inpunt  es muy pequeño y lineal por lo cual no permite  el ingresar un comentario de manera confortable  para el usuario


Resultado actual:
Dificultar al ingresar un comentario extenso  en la  tarea

Resultado esperado:
 El tamño del imput del comentario se mas amplio para que permita al usuario validar  el comentarion ingresado  previo al envio

Impacto:
Dificultad  para el usuario en el ingreso  de comentarios

### BUG-014: Prioridad en otro idioma
- Severidad: Baja
- Componente: Prioridad revision de la task
- Endpoint: GET/api/tasks/{task_id}

Precondiciones:
API activa

Pasos:
1. selecionar una tarea previamente creada para actualizacion  de estado y o gragar comentarios
2. Se validaen la parte superiro  derecha que la prioridad esta escrita en ingles  cuando previmente se selecciono en español lo cual provoca incogruencia en el idioma de la aplicacion


Resultado actual:
"Medium"

Resultado esperado:
 Medio

Impacto: Bajo pero genera  confusion   en la revision de  la prioridad del tarea si el cliente no habla  ingles

### BUG-015: Creación de tareas para un proyecto directamente desde el endpoint
Severidad: Media
Componente: API - Gestión de Tareas
Endpoint: POST /api/tasks

Precondiciones:
API activa y funcionando
Proyecto existente con ID válido en la base de datos

Pasos:

1. Enviar una solicitud POST al endpoint POST /api/tasks con un cuerpo JSON válido que incluya título, descripción, etc.
2. Incluir en el cuerpo de la solicitud el campo proyectoId con el mismo ID del proyecto al que se está intentando agregar la tarea lo cual  no permite.
3. Enviar la petición.

Resultado actual:
La tarea no se crea correctamente, ya que el sisteme no esta solicitando el id del projecto alcual se le asignara la tarea

Resultado esperado:
El sistema debe validar el campo proyectoId enviado en  la solicitud y asociar automáticamente la tarea al proyecto especificado en la URL (/api/proyectos/{id}/tareas), independientemente del valor enviado en el cuerpo.

Impacto:
No Posible asignación de tareas a proyectos desde el endpoint

### BUG-016: Exportación a Excel de lista de tareas de proyecto enviada con errores (archivo sin filtros aplicados)
Severidad: Alta
Componente: Exportación - Módulo de Reportes/Tareas
Endpoint: GET /api/export/tasks

Precondiciones:
API activa y funcionando
Proyecto existente con ID válido
El proyecto contiene múltiples tareas registradas


Pasos:

1. Acceder a la vista de tareas sin aplicar filtros
2. Hacer clic en el botón "Exportar a Excel"
3. Abrir el archivo Excel generado
5. Verificar los datos exportados

Resultado actual:
El archivo Excel generado no contiene ningunaclase de informacion coherente o entendible hacerca de als tareas

Resultado esperado:
El archivo Excel debe contener  las tareas que cumplen con los filtros aplicados 

Impacto:
Usuarios reciben información incorrecta o no deseada
Experiencia de usuario negativa

### BUG-017: Inconsistencia en contadores de tareas - No se muestran tareas en estado "Canceladas"
Severidad: Media
Componente: Frontend - Dashboard/Resumen de Proyectos
Endpoint: N/A (Interfaz de usuario)

Precondiciones:
Proyecto con tareas en diferentes estados
Existen tareas en estado "Canceladas" en el proyecto

Pasos:

1. Observar los contadores en la parte superior de la pantalla
2. Verificar el total de tareas mostrado
3. Sumar manualmente los valores de los contadores individuales
4. Comparar la suma con el total mostrado

Resultado actual:
En la interfaz se muestran los siguientes contadores:

Total: 24 tareas
Por Hacer: 14 tareas
En Progreso: 2 tareas
Completadas: 2 tareas
Vencidas: 19 tareas

La suma de los contadores individuales (14 + 2 + 2  = 18) no coincide con el total mostrado (24). Adicionalmente, no existe un contador para tareas en estado "Canceladas", lo que sugiere que estas tareas no están siendo representadas en la interfaz pero sí podrían estar afectando los cálculos.

Resultado esperado:
Los contadores deben ser consistentes: la suma de todos los estados debe igualar el total de tareas
Debe existir un contador visible para el estado "Canceladas"
Los valores deben reflejar con precisión el estado actual de las tareas en el proyecto

Impacto:
Confusión para los usuarios al interpretar el progreso del proyecto
Datos inconsistentes que afectan la toma de decisiones
Mala experiencia de usuario al no poder visualizar todas las tareas por estado
Posibles errores en reportes y seguimiento de proyectos

### BUG-018: No permite crear usuarios desde el front
Severidad: Alta
Componente: Frontend 
Endpoint: POST /api/users

Precondiciones:
Usuario autenticado 
Formulario de creación de usuarios disponible

Pasos:
1. no existe  el botón "Crear Nuevo Usuario" o "Agregar Usuario"
2. Completar todos los campos requeridos del formulario (username,nombre, email, rol, etc.)
3. Hacer clic en el botón "Guardar" o "Crear Usuario"
4. Observar la respuesta del sistema

Resultado actual:
El usuario no tiene  ninguna opcion desde el front para crear usuarios

Resultado esperado:
El sistema debe procesar la creación del usuario, mostrar un mensaje de confirmación exitosa y redirigir a la lista de usuarios donde aparecerá el nuevo usuario creado. En caso de error, debe mostrar mensajes claros indicando qué campos necesitan corrección.

Impacto:
Imposibilidad de agregar nuevos usuarios al sistema
Bloqueo en la incorporación de nuevos miembros al equipo
Dependencia de creación manual de usuarios por API directa
Posible impacto en la incorporación de nuevos empleados o colaboradores