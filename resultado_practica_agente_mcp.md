# Resultado de la práctica: agente de artículos con MCP

## Objetivo

Construir un agente que reúna un modelo de lenguaje local, herramientas MCP y la
API de un blog para redactar una noticia y guardarla como borrador. La práctica
demuestra cómo un modelo puede colaborar con funciones de una aplicación sin
acceder directamente a su base de datos.

## Componentes

- **Ollama y `qwen3.5:4b`** generan el artículo localmente. El modelo
  predeterminado se configura en `agente_con_mcp.py`.
- **Django REST Framework** ofrece la API del blog en
  `http://127.0.0.1:8000/api/articulos/`.
- **`herramientas.py`** contiene las funciones Python que consultan esa API y
  crean borradores. La creación usa el token local `BLOG_API_TOKEN` del archivo
  `.env`.
- **`servidor_mcp.py`** registra esas funciones como herramientas MCP y las
  sirve mediante HTTP en `http://127.0.0.1:8001/mcp`.
- **`agente_con_mcp.py`** coordina el flujo: lee artículos, solicita una
  propuesta a Ollama, valida la respuesta y llama a MCP para guardar el
  borrador.
- **`prueba_mcp.py`** comprueba que un cliente MCP puede descubrir las
  herramientas y consultar artículos. No crea borradores.

## Flujo de una ejecución

1. La persona escribe un encargo en la terminal.
2. El agente llama a la herramienta MCP `listar_articulos`.
3. Envía a Ollama el encargo y los títulos publicados para reducir repeticiones.
4. Ollama genera un objeto JSON con título y cuerpo. Pydantic comprueba que el
   título tenga al menos 5 caracteres y el cuerpo al menos 50.
5. El agente llama a `crear_borrador` a través de MCP.
6. La API del blog devuelve los datos del nuevo borrador. El agente comprueba
   que haya un ID y que el estado sea `borrador`.

**Importante:** en esta versión, el guardado es automático después de la
redacción. No hay un paso de aprobación entre generar y guardar. El agente no
publica el artículo, pero cada ejecución correcta puede crear un borrador real
en la base de datos.

## Preparación

Se necesitan Python y `uv`, Ollama con el modelo seleccionado instalado, y el
servidor Django funcionando. Para esta práctica se comprobó que Ollama tenía
`qwen3.5:4b` instalado.

El archivo `.env`, que no se debe compartir ni subir a Git, debe contener el
token de la API:

```dotenv
BLOG_API_TOKEN=tu_token_local
```

No escribas el token en el código, en los encargos ni en este documento. La
función de `herramientas.py` carga el `.env` local para acceder a esa variable.

Instala o sincroniza las dependencias desde la raíz del proyecto:

```powershell
uv sync
```

El modelo predeterminado actual es `qwen3.5:4b`. Si se quiere cambiar mediante
una variable de entorno de PowerShell para la terminal actual:

```powershell
$env:OLLAMA_MODEL = "qwen3.5:9b"
```

El script `agente_con_mcp.py` usa `os.getenv` y no carga `.env` por sí mismo.
Por tanto, cambiar `OLLAMA_MODEL` dentro de `.env` no cambia el modelo en este
script salvo que se añada explícitamente la carga de ese archivo o se exporte
la variable al entorno antes de ejecutarlo.

## Cómo ejecutar el flujo

Mantén el servidor del blog Django activo. Abre dos terminales en la carpeta
del proyecto `agente-blog`.

**Terminal 1: iniciar el servidor MCP**

```powershell
uv run servidor_mcp.py
```

Déjalo abierto. Escucha en `127.0.0.1:8001` y expone la ruta `/mcp`.

**Terminal 2: ejecutar el agente**

```powershell
uv run agente_con_mcp.py
```

Cuando aparezca `Cuéntame tu idea para el artículo:`, escribe un encargo con
información suficiente y explícita. Por ejemplo:

> SIMULACIÓN EDUCATIVA: Los alumnos del CPIFP Alan Turing han construido
> RiegoBot, un robot que mide la humedad de la tierra mediante un sensor y
> activa una bomba de agua cuando detecta que está seca. Funciona con una
> batería recargable y actualmente está en fase de pruebas. Redacta una noticia
> breve utilizando únicamente estos datos y guárdala como borrador en el blog,
> sin publicarla.

El proceso muestra cuántos artículos consultó, qué título generó y el ID del
borrador guardado. Para terminar el servidor MCP, usa `Ctrl+C` en la Terminal
1.

## Comprobación MCP sin guardar un artículo

Con el servidor MCP activo, se puede usar un segundo cliente para comprobar la
conexión:

```powershell
uv run prueba_mcp.py
```

La prueba lista las herramientas disponibles y llama solo a
`listar_articulos`. No llama a `crear_borrador`.

## Resultado obtenido en esta práctica

Se ejecutó `agente_con_mcp.py` con un encargo sobre RiegoBot. El agente indicó
que había consultado 2 artículos, generó un título y Django confirmó:

```text
BORRADOR GUARDADO EN DJANGO: ID 7 (borrador)
```

El ID 7 quedó como borrador, no como artículo publicado.

## Reutilizar el patrón en otro proyecto

Para llevar esta arquitectura a otra aplicación, identifica las equivalencias:

1. **Servicio:** la aplicación que contiene los datos y ofrece una API.
2. **Herramientas:** funciones pequeñas que leen o modifican ese servicio,
   validan sus entradas y gestionan la autenticación sin exponer secretos.
3. **Servidor MCP:** registra las funciones con nombres y descripciones claros
   y define cómo se conecta el cliente.
4. **Modelo:** recibe las instrucciones y los datos necesarios y devuelve una
   respuesta con formato validable.
5. **Agente:** define el orden de las operaciones, valida cada resultado,
   maneja errores y limita acciones con efectos secundarios.
6. **Prueba:** verifica primero las operaciones de lectura. Prueba escrituras
   solo cuando sepas qué dato persistente crearán y cómo revisarlo o retirarlo.

Antes de ejecutar una tarea real, comprueba el modelo instalado, la dirección
del servidor MCP, la disponibilidad de la API y qué operaciones guardan o
publican datos. En este proyecto, `crear_borrador` escribe en el blog, mientras
que `listar_articulos` solo consulta.
