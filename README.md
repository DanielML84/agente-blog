# Agente para el blog de robótica

Servidor MCP local que ofrece herramientas para consultar los artículos
publicados, redactar propuestas con Ollama y guardar artículos como borradores
en el proyecto Django del blog. La redacción no guarda nada por sí sola.

## Requisitos

- Python 3.14 y `uv`.
- Ollama en ejecución con el modelo `qwen3.5:9b` descargado.
- El blog ejecutándose en `http://127.0.0.1:8000/`.
- Un token de Django válido en `.env`, en la variable `BLOG_API_TOKEN`.

El `.env` de este proyecto está excluido de Git. No compartas ni publiques el
token. El agente usa ese token solo al guardar un borrador mediante la API del
blog.

## Preparación

Desde la carpeta del agente:

```powershell
uv sync
```

Si quieres usar otro modelo o una dirección distinta, define `OLLAMA_MODEL`,
`OLLAMA_HOST` o `BLOG_API_URL` en `.env`. Los valores predeterminados son
`qwen3.5:9b`, `http://127.0.0.1:11434` y
`http://127.0.0.1:8000/api/articulos/`.

## Conectar con VS Code

Abre esta carpeta del agente en VS Code. La configuración
`.vscode/mcp.json` registra el servidor MCP local `agente-blog`; inicia o
habilita ese servidor desde las opciones MCP de VS Code.

En el chat puedes pedir, por ejemplo:

> Redacta un artículo sobre cómo se orientan los robots móviles.

El agente puede usar estas herramientas:

- `consultar_articulos_publicados`: lee los artículos publicados.
- `redactar_articulo`: genera una propuesta usando Ollama; no la guarda.
- `guardar_borrador`: envía título y cuerpo a Django como borrador.

Revisa el texto generado antes de pedir explícitamente que lo guarde. La API
crea un borrador no publicado; la publicación sigue siendo manual desde el
administrador del blog.

## Ejecutar y comprobar

Para comprobar la comunicación MCP desde una terminal:

```powershell
uv run main.py
```

Este comando inicia el transporte `stdio` del servidor, que espera mensajes
MCP; para el uso normal, deja que VS Code lo inicie desde `mcp.json`.

Ejecuta los tests con:

```powershell
uv run python -m unittest discover -s tests
```
