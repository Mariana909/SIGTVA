"""
Utilidad de visualización (no es parte de ningún patrón).

Los patrones escriben sus pasos con logging. CapturaTraza recoge esos mensajes
durante una operación para mostrarlos en pantalla (factura) sin acoplar los
patrones a Flask.
"""
import logging
import threading


class _Recolector(logging.Handler):
    def __init__(self, mensajes: list):
        super().__init__(level=logging.INFO)
        self._mensajes = mensajes
        self._hilo = threading.get_ident()  # ignora mensajes de otras peticiones simultáneas

    def emit(self, record: logging.LogRecord) -> None:
        if record.thread == self._hilo:
            self._mensajes.append(record.getMessage())


class CapturaTraza:
    """Uso: with CapturaTraza("sigtva.tiquete") as traza: ...  ->  traza.mensajes"""

    def __init__(self, *nombres_logger: str):
        self._loggers = [logging.getLogger(n) for n in nombres_logger]
        self._niveles = []
        self.mensajes: list = []

    def __enter__(self):
        self._handler = _Recolector(self.mensajes)
        for lg in self._loggers:
            self._niveles.append(lg.level)
            lg.setLevel(logging.INFO)
            lg.addHandler(self._handler)
        return self

    def __exit__(self, *exc):
        for lg, nivel in zip(self._loggers, self._niveles):
            lg.removeHandler(self._handler)
            lg.setLevel(nivel)
        return False
