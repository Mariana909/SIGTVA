"""
Capa de LÓGICA — CONTROL del patrón Prototype.

Proceso: Registro de envío — radicación de remesa múltiple.
ServicioPrototipos siembra las plantillas una vez y radica cada remesa
CLONANDO: la guía base (superficial), una tula por destino (profunda) y la
remesa corporativa (profunda). Cada guía clonada se numera con el
SecuenciadorGuia (Singleton): los patrones componen.
"""
import logging

from prototypes.prototipos_envio import Guia, RegistroPrototipos, Remesa, Tula
from singletons.secuenciadores import SecuenciadorGuia

logger = logging.getLogger("sigtva.prototipos")


class ServicioPrototipos:
    """CONTROL Prototype: pide copias al registro, nunca construye a mano."""

    def __init__(self, registro: RegistroPrototipos = None,
                 secuenciador: SecuenciadorGuia = None):
        self._registro = registro or RegistroPrototipos()
        self._secuenciador = secuenciador or SecuenciadorGuia()

    def sembrar_plantillas(self, remitente: str, servicio: str = "estandar") -> list:
        """Guarda guía base, tula estándar y remesa corporativa. Una sola vez."""
        self._registro.registrar("guia_base", Guia("BASE", remitente, servicio))
        self._registro.registrar("tula_estandar", Tula("BASE", "DESTINO"))
        self._registro.registrar("remesa_corporativa", Remesa("BASE", remitente))
        logger.info("[Prototype] Plantillas sembradas para el remitente %s", remitente)
        return self._registro.claves()

    def radicar_remesa(self, remitente: str, destinos: list) -> dict:
        """Clona una guía por destino, una tula por destino y cierra la remesa."""
        if not remitente:
            raise ValueError("La remesa necesita un remitente.")
        if not destinos:
            raise ValueError("La remesa necesita al menos un destino.")
        self.sembrar_plantillas(remitente)

        remesa = self._registro.clonar("remesa_corporativa")
        remesa.numero = self._secuenciador.siguiente()
        tulas = []
        for destino in destinos:
            guia = self._registro.clonar("guia_base")
            guia.numero = self._secuenciador.siguiente()
            tula = self._registro.clonar("tula_estandar")
            tula.destino = destino
            tula.precinto = f"PR-{guia.numero}"
            tula.guias.append(guia)
            remesa.guias.append(guia)
            tulas.append(tula)
            logger.info("[Prototype] Guía %s -> %s (precinto %s)",
                        guia.numero, destino, tula.precinto)
        logger.info("[Prototype] Remesa %s lista (%d guías)", remesa.numero, len(tulas))
        return {"remesa": remesa, "tulas": tulas, "guias": list(remesa.guias)}
