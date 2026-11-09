"""
Capa de LÓGICA — CLIENTE del patrón Memento.

Proceso: Corrección de encomienda registrada. AuxiliarEncomiendas guarda
una instantánea antes de corregir y puede revertirla; «obtenerUltimo»
extrae (pop), así que revertir dos veces usa instantáneas distintas.
"""
import logging

from domain.envio import Envio
from mementos.recuerdos import HistorialEnvios

logger = logging.getLogger("sigtva.memento")


class AuxiliarEncomiendas:
    """Cliente Memento: corrige con foto previa y revierte si hace falta."""

    def __init__(self, historial: HistorialEnvios = None):
        self._historial = historial or HistorialEnvios()

    def corregirEnvio(self, envio: Envio, cambios: dict) -> None:
        """Guarda la instantánea y aplica los cambios permitidos."""
        self._historial.guardar(envio.crearRecuerdo())
        for clave in ("pesoFacturable", "valorDeclarado", "tipoServicio", "estado"):
            if clave in cambios:
                setattr(envio, clave, cambios[clave])
        logger.info("[Memento] Envío corregido; instantánea guardada")

    def revertir(self, envio: Envio) -> bool:
        """Restaura la última instantánea; False si no había ninguna."""
        instantanea = self._historial.obtenerUltimo()
        if instantanea is None:
            return False
        envio.restaurar(instantanea)
        logger.info("[Memento] Envío revertido a '%s'", instantanea.obtenerEstado())
        return True
