"""Configuración compartida de las demos: rutas de importación y salida por consola."""
import logging
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # evita errores de tildes en consolas de Windows

# Los patrones escriben sus pasos con logging; aquí los mostramos en pantalla.
logging.basicConfig(level=logging.INFO, format="      | %(message)s", stream=sys.stdout)


def titulo(texto: str) -> None:
    print("\n" + "=" * 72)
    print(texto)
    print("=" * 72)


def seccion(texto: str) -> None:
    print(f"\n--- {texto} ---")
