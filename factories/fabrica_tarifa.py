"""
PATRÓN: FACTORY METHOD
PROCESO: Venta de tiquete — creación de la tarifa

Roles del patrón
  Producto (interfaz) ..... Tarifa
  Productos concretos ..... TarifaOrdinaria, TarifaEstudiante, TarifaAdultoMayor
  Creador (abstracto) ..... FabricaTarifa   -> declara el factory method crearTarifa()
  Creadores concretos ..... FabricaTarifaOrdinaria, FabricaTarifaEstudiante,
                            FabricaTarifaAdultoMayor

El Builder de tiquete (ver /builders) recibe la Tarifa ya creada por su fábrica.
"""
from abc import ABC, abstractmethod


# ═══════════════════════ PRODUCTO ═══════════════════════
class Tarifa(ABC):
    @abstractmethod
    def calcular(self) -> float:
        """Valor final a pagar después de aplicar la tarifa al valor base."""

    @abstractmethod
    def descripcion(self) -> str:
        """Nombre legible de la tarifa (se muestra en la factura)."""


def _validarBase(valorBase: float) -> float:
    if valorBase <= 0:
        raise ValueError("El valor base del viaje debe ser mayor que cero.")
    return valorBase


class TarifaOrdinaria(Tarifa):
    DESCUENTO = 0.0

    def __init__(self, valorBase: float):
        self.valorBase = _validarBase(valorBase)

    def calcular(self) -> float:
        return round(self.valorBase * (1 - self.DESCUENTO), 2)

    def descripcion(self) -> str:
        return "Tarifa ordinaria"


class TarifaEstudiante(Tarifa):
    DESCUENTO = 0.15

    def __init__(self, valorBase: float):
        self.valorBase = _validarBase(valorBase)

    def calcular(self) -> float:
        return round(self.valorBase * (1 - self.DESCUENTO), 2)

    def descripcion(self) -> str:
        return "Tarifa estudiante (15% de descuento)"


class TarifaAdultoMayor(Tarifa):
    DESCUENTO = 0.20

    def __init__(self, valorBase: float):
        self.valorBase = _validarBase(valorBase)

    def calcular(self) -> float:
        return round(self.valorBase * (1 - self.DESCUENTO), 2)

    def descripcion(self) -> str:
        return "Tarifa adulto mayor (20% de descuento)"


# ═══════════════════════ CREADOR ABSTRACTO ═══════════════════════
class FabricaTarifa(ABC):
    @abstractmethod
    def crearTarifa(self, valorBase: float) -> Tarifa:
        """FACTORY METHOD: cada subclase decide qué Tarifa concreta instanciar."""

    def liquidar(self, valorBase: float) -> float:
        """Lógica común del creador: usa el producto sin saber cuál es."""
        return self.crearTarifa(valorBase).calcular()


# ═══════════════════════ CREADORES CONCRETOS ═══════════════════════
class FabricaTarifaOrdinaria(FabricaTarifa):
    def crearTarifa(self, valorBase: float) -> Tarifa:
        return TarifaOrdinaria(valorBase)


class FabricaTarifaEstudiante(FabricaTarifa):
    def crearTarifa(self, valorBase: float) -> Tarifa:
        return TarifaEstudiante(valorBase)


class FabricaTarifaAdultoMayor(FabricaTarifa):
    def crearTarifa(self, valorBase: float) -> Tarifa:
        return TarifaAdultoMayor(valorBase)
