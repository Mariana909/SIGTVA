"""
PATRÓN: MEMENTO
PROCESO: Corrección de encomienda registrada — guardar y revertir

Roles del patrón
  Originador ......... Envio (en domain) -> crea y restaura recuerdos
  Recuerdo ........... Recuerdo (inmutable) + InstantaneaEnvio (concreto)
  Depositario ........ HistorialEnvios   -> guarda 0..* recuerdos,
                                           obtenerUltimo() EXTRAE (pop)
  Cliente ............ AuxiliarEncomiendas (en services)

Por qué Memento: antes de corregir peso, valor o servicio hay que poder
volver al estado anterior sin exponer los campos del envío a nadie.
«obtenerUltimo» hace pop: revertir dos veces usa instantáneas distintas.
"""
from __future__ import annotations


class Recuerdo:
    """Recuerdo (inmutable): solo guarda el estado; nadie lo modifica."""

    def __init__(self, estado: str):
        object.__setattr__(self, "_estado", estado)

    def __setattr__(self, nombre: str, valor: object) -> None:
        raise AttributeError(
            f"Recuerdo es inmutable: no se puede asignar {nombre}")

    def obtenerEstado(self) -> str:
        return self._estado


class InstantaneaEnvio(Recuerdo):
    """Recuerdo concreto del envío: estado, peso, valor y tipo de servicio."""

    def __init__(self, estado: str, pesoFacturable: float,
                 valorDeclarado: float, tipoServicio: str):
        super().__init__(estado)
        object.__setattr__(self, "_pesoFacturable", pesoFacturable)
        object.__setattr__(self, "_valorDeclarado", valorDeclarado)
        object.__setattr__(self, "_tipoServicio", tipoServicio)

    def obtenerPesoFacturable(self) -> float:
        return self._pesoFacturable

    def obtenerValorDeclarado(self) -> float:
        return self._valorDeclarado

    def obtenerTipoServicio(self) -> str:
        return self._tipoServicio


class HistorialEnvios:
    """Depositario: pila de instantáneas. obtenerUltimo() extrae (pop)."""

    def __init__(self):
        self._historial: list[InstantaneaEnvio] = []

    def guardar(self, r: InstantaneaEnvio) -> None:
        self._historial.append(r)

    def obtenerUltimo(self) -> InstantaneaEnvio | None:
        """Extrae (pop) la última instantánea; None si el historial está vacío."""
        if not self._historial:
            return None
        return self._historial.pop()

    def estaVacio(self) -> bool:
        return not self._historial
