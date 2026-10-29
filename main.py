import asyncio
import json
import os
from typing import TypedDict

import ollama
from mcp.server.mcpserver import MCPServer

from herramientas import crear_borrador as guardar_borrador_en_blog
from herramientas import listar_articulos

MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
OLLAMA_CLIENT = ollama.Client(
    host=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
)

server = MCPServer(
    "agente-blog",
    instructions=(
        "Asistente editorial en español para un blog de robótica. "
        "Redacta propuestas claras y rigurosas. Enseña el borrador al usuario "
        "y no lo guardes hasta que confirme explícitamente."
    ),
)


class Borrador(TypedDict):
    titulo: str
    cuerpo: str


def _generar_articulo(tema: str) -> Borrador:
    tema = tema.strip()
    if not tema:
        raise ValueError("Indica un tema para el artículo.")

    respuesta = OLLAMA_CLIENT.chat(
        model=MODEL,
        format="json",
        think=False,
        options={"num_predict": 768},
        messages=[
            {
                "role": "system",
                "content": (
                    "Escribes artículos en español para un blog de robótica. "
                    "Usa un tono didáctico, cercano y riguroso, explica los "
                    "términos técnicos y estructura el cuerpo en Markdown. "
                    "No inventes cifras, estudios ni fuentes. Devuelve solo "
                    "un objeto JSON con las claves titulo y cuerpo."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Redacta un artículo de unas 200 palabras sobre: {tema}. "
                    "Incluye un título y subtítulos Markdown útiles."
                ),
            },
        ],
    )

    try:
        datos = json.loads(respuesta.message.content)
    except json.JSONDecodeError as error:
        raise RuntimeError("Ollama no devolvió un borrador JSON válido.") from error

    if not isinstance(datos, dict):
        raise RuntimeError("Ollama devolvió un borrador con formato incorrecto.")

    titulo = datos.get("titulo")
    cuerpo = datos.get("cuerpo")
    if not isinstance(titulo, str) or not titulo.strip():
        raise RuntimeError("Ollama no devolvió un título válido.")
    if not isinstance(cuerpo, str) or not cuerpo.strip():
        raise RuntimeError("Ollama no devolvió un cuerpo válido.")

    return {"titulo": titulo.strip(), "cuerpo": cuerpo.strip()}


@server.tool(
    description=(
        "Lista los artículos publicados del blog para consultar el contenido "
        "existente y evitar repeticiones."
    )
)
async def consultar_articulos_publicados() -> list[dict]:
    return await asyncio.to_thread(listar_articulos)


@server.tool(
    description=(
        "Genera una propuesta de artículo en español sobre robótica. Solo "
        "devuelve el borrador; no lo publica ni lo guarda en el blog."
    )
)
async def redactar_articulo(tema: str) -> Borrador:
    return await asyncio.to_thread(_generar_articulo, tema)


@server.tool(
    description=(
        "Guarda un artículo como borrador privado en el blog. Antes de llamar "
        "a esta herramienta, muestra el borrador completo y espera a que el "
        "usuario confirme explícitamente que quiere guardarlo."
    )
)
async def guardar_borrador(titulo: str, cuerpo: str) -> dict:
    return await asyncio.to_thread(guardar_borrador_en_blog, titulo, cuerpo)


def main() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
