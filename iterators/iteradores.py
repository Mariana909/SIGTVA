"""
PATRÓN: ITERATOR
PROCESO: Despacho de remesa — recorrido de guías sin exponer la lista

Roles del patrón
  Agregado (interfaz) ...... AgregadoEnvios  -> declara crearIterador()
  AgregadoConcreto ......... Remesa (en prototypes) -> crea IteradorGuia
  Iterador (interfaz) ...... IteradorEnvios  -> declara haySiguiente() y siguiente()
  IteradorConcreto ......... IteradorGuia    -> recorre Remesa.guias con un índice
  Elemento ................. Guia (en prototypes)
  Cliente .................. AuxiliarDespacho (en services)

Por qué Iterator: el despacho necesita visitar cada guía en orden para
escanearla, sin que el cliente dependa de que las guías vivan en una lista.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prototypes.prototipos_envio import Guia, Remesa


class AgregadoEnvios(ABC):
    """Agregado (interfaz): entrega un iterador para recorrer sus envíos."""

    @abstractmethod
    def crearIterador(self) -> IteradorEnvios:
        """Crea el iterador de este agregado (una instancia nueva por recorrido)."""


class IteradorEnvios(ABC):
    """Iterador (interfaz): recorre los elementos uno a uno sin exponer la colección."""

    @abstractmethod
    def haySiguiente(self) -> bool:
        """True si queda al menos un elemento por entregar."""

    @abstractmethod
    def siguiente(self) -> Guia:
        """Entrega el siguiente elemento; lanza StopIteration si se agotó."""


class IteradorGuia(IteradorEnvios):
    """IteradorConcreto: recorre Remesa.guias conservando el agregado que recorre."""

    def __init__(self, agregado: Remesa):
        # El iterador conoce su agregado concreto (rol «agregado» del diagrama).
        self._agregado = agregado
        self._indice = 0

    def haySiguiente(self) -> bool:
        return self._indice < len(self._agregado.guias)

    def siguiente(self) -> Guia:
        if not self.haySiguiente():
            raise StopIteration("No quedan guías en la remesa.")
        guia = self._agregado.guias[self._indice]
        self._indice += 1
        return guia
