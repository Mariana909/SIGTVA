"""
Capa de LÓGICA — CLIENTE del patrón Iterator.

Proceso: Despacho de remesa. AuxiliarDespacho recorre las guías con el
iterador sin conocer la lista interna; depende de la interfaz
AgregadoEnvios, no de la clase Remesa.
"""
import logging

from iterators.iteradores import AgregadoEnvios

logger = logging.getLogger("sigtva.iterator")


class AuxiliarDespacho:
    """Cliente Iterator: escanea cada guía de la remesa en orden."""

    def despachar(self, remesa: AgregadoEnvios) -> list[str]:
        """Recorre el agregado y devuelve los números de guía despachados."""
        despachadas = []
        iterador = remesa.crearIterador()
        while iterador.haySiguiente():
            guia = iterador.siguiente()
            despachadas.append(guia.numero)
            logger.info("[Iterator] Guía %s despachada", guia.numero)
        logger.info("[Iterator] Remesa despachada (%d guías)", len(despachadas))
        return despachadas
