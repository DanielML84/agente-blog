import asyncio
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import main


class ArticleGenerationTests(unittest.TestCase):
    @patch("main.OLLAMA_CLIENT.chat")
    def test_generates_article_without_saving_it(self, chat):
        chat.return_value = SimpleNamespace(
            message=SimpleNamespace(
                content=json.dumps(
                    {"titulo": "Robots móviles", "cuerpo": "## Navegación\n"}
                )
            )
        )

        article = main._generar_articulo("orientación de robots móviles")

        self.assertEqual(article["titulo"], "Robots móviles")
        self.assertEqual(article["cuerpo"], "## Navegación")
        chat.assert_called_once()

    @patch("main.OLLAMA_CLIENT.chat")
    def test_rejects_empty_topic_without_calling_ollama(self, chat):
        with self.assertRaises(ValueError):
            main._generar_articulo("  ")

        chat.assert_not_called()

    @patch("main.OLLAMA_CLIENT.chat")
    def test_rejects_invalid_model_response(self, chat):
        chat.return_value = SimpleNamespace(
            message=SimpleNamespace(content="No es JSON")
        )

        with self.assertRaisesRegex(RuntimeError, "JSON válido"):
            main._generar_articulo("sensores robóticos")

    @patch("main.guardar_borrador_en_blog")
    def test_saves_only_when_save_tool_is_called(self, save):
        save.return_value = {
            "id": 7,
            "titulo": "Robots móviles",
            "cuerpo": "Contenido",
            "estado": "borrador",
        }

        result = asyncio.run(
            main.guardar_borrador("Robots móviles", "Contenido")
        )

        self.assertEqual(result["estado"], "borrador")
        save.assert_called_once_with("Robots móviles", "Contenido")


if __name__ == "__main__":
    unittest.main()
