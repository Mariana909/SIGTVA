"""
PATRÓN: ABSTRACT FACTORY
PROCESO: Registro de envío (encomiendas)

Roles del patrón en este archivo
  FabricaAbstracta ..... FabricaEnvio
  FabricaConcreta ...... FabricaPaqueteo, FabricaCorporativa, FabricaRemesa
  Productos abstractos . CalculadorFlete, ValidadorPeso, GeneradorGuia,
                         NotificadorEnvio, ValidadorCredito
  Productos concretos .. 5 productos x 3 familias = 15 clases
El cliente (ServicioRegistroEnvio) vive en /services y solo conoce las interfaces.
"""
import logging
import uuid
from abc import ABC, abstractmethod
from typing import List

from domain.envio import Envio, Guia, calcularPesoFacturable

logger = logging.getLogger("sigtva.envio")


# ═══════════════════════ PRODUCTOS ABSTRACTOS ═══════════════════════
class CalculadorFlete(ABC):
    @abstractmethod
    def calcular(self, ruta: str, peso: float) -> float:
        """Valor del flete para el peso facturable dado."""

    @abstractmethod
    def obtenerPrioridad(self) -> int:
        """Prioridad de despacho de la familia (1 = alta, 3 = normal)."""


class ValidadorPeso(ABC):
    @abstractmethod
    def validar(self, peso: float, dims: str) -> bool:
        """True si máx(peso real, peso volumétrico) cabe en el tope de la familia."""


class GeneradorGuia(ABC):
    @abstractmethod
    def generar(self, datos: dict) -> Guia:
        """Una guía individual."""

    @abstractmethod
    def generarLote(self, n: int, base: int) -> List[Guia]:
        """n guías consecutivas a partir del consecutivo base."""


class NotificadorEnvio(ABC):
    @abstractmethod
    def avisar(self, envio: Envio) -> None:
        """Avisa que el envío quedó registrado."""


class ValidadorCredito(ABC):
    @abstractmethod
    def validarCupo(self, cliente: str, monto: float) -> bool:
        """True si el cliente puede pagar ese monto según las reglas de la familia."""


# ── utilidades privadas de guías (evitan repetir código en las 3 familias) ──
def _guia(prefijo: str, consecutivo: str) -> Guia:
    numero = f"{prefijo}-{consecutivo}"
    return Guia(numero=numero, codigoBarras=f"*{numero}*")


def _lote(prefijo: str, n: int, base: int) -> List[Guia]:
    if n <= 0:
        raise ValueError("El lote debe tener al menos una guía.")
    return [_guia(prefijo, f"{base + i:08d}") for i in range(n)]


# ═══════════════════════ FAMILIA PAQUETEO ═══════════════════════
# Envíos sueltos: tope 30 kg, pago de contado o contraentrega.
class FletePaqueteo(CalculadorFlete):
    TARIFA_KG = 2500.0

    def calcular(self, ruta: str, peso: float) -> float:
        return round(peso * self.TARIFA_KG, 2)

    def obtenerPrioridad(self) -> int:
        return 3


class PesoPaqueteo(ValidadorPeso):
    def __init__(self):
        self.maxKg = 30

    def validar(self, peso: float, dims: str) -> bool:
        return 0 < peso and calcularPesoFacturable(peso, dims) <= self.maxKg


class GuiaPaqueteo(GeneradorGuia):
    def generar(self, datos: dict) -> Guia:
        return _guia("PAQ", uuid.uuid4().hex[:8].upper())

    def generarLote(self, n: int, base: int) -> List[Guia]:
        return _lote("PAQ", n, base)


class AvisoPaqueteo(NotificadorEnvio):
    def avisar(self, envio: Envio) -> None:
        logger.info("[Aviso Paqueteo] SMS al remitente: guía %s registrada.", envio.guia.numero)


class CreditoPaqueteo(ValidadorCredito):
    def validarCupo(self, cliente: str, monto: float) -> bool:
        return True  # Contado o contraentrega: no hay crédito que verificar.


# ═══════════════════════ FAMILIA CORPORATIVA ═══════════════════════
# Empresas: tope 500 kg, tarifa negociada, valida cupo de crédito.
class FleteCorporativa(CalculadorFlete):
    TARIFA_NEGOCIADA_KG = 1800.0

    def calcular(self, ruta: str, peso: float) -> float:
        return round(peso * self.TARIFA_NEGOCIADA_KG, 2)

    def obtenerPrioridad(self) -> int:
        return 1


class PesoCorporativa(ValidadorPeso):
    def __init__(self):
        self.maxKg = 500

    def validar(self, peso: float, dims: str) -> bool:
        return 0 < peso and calcularPesoFacturable(peso, dims) <= self.maxKg


class GuiaCorporativa(GeneradorGuia):
    def generar(self, datos: dict) -> Guia:
        return _guia("CORP", uuid.uuid4().hex[:8].upper())

    def generarLote(self, n: int, base: int) -> List[Guia]:
        return _lote("CORP", n, base)


class AvisoCorporativa(NotificadorEnvio):
    def avisar(self, envio: Envio) -> None:
        logger.info("[Aviso Corporativa] Correo al ejecutivo de cuenta: guía %s registrada.", envio.guia.numero)


class CreditoCorporativa(ValidadorCredito):
    CUPO_MAXIMO = 800_000.0  # Cupo simulado; en producción se consultaría por cliente.

    def validarCupo(self, cliente: str, monto: float) -> bool:
        return monto <= self.CUPO_MAXIMO


# ═══════════════════════ FAMILIA REMESA ═══════════════════════
# Envíos múltiples: sin tope por envío, descuento por volumen, guías en lote.
class FleteRemesa(CalculadorFlete):
    TARIFA_KG = 2500.0

    def calcular(self, ruta: str, peso: float) -> float:
        descuento = 0.25 if peso >= 200 else 0.15 if peso >= 50 else 0.0
        return round(peso * self.TARIFA_KG * (1 - descuento), 2)

    def obtenerPrioridad(self) -> int:
        return 2


class PesoRemesa(ValidadorPeso):
    def validar(self, peso: float, dims: str) -> bool:
        calcularPesoFacturable(peso, dims)  # solo valida el formato de dims
        return peso > 0


class GuiaRemesa(GeneradorGuia):
    def generar(self, datos: dict) -> Guia:
        return _guia("REM", uuid.uuid4().hex[:8].upper())

    def generarLote(self, n: int, base: int) -> List[Guia]:
        return _lote("REM", n, base)


class AvisoRemesa(NotificadorEnvio):
    def avisar(self, envio: Envio) -> None:
        logger.info("[Aviso Remesa] Consolidado enviado a la agencia: guía %s registrada.", envio.guia.numero)


class CreditoRemesa(ValidadorCredito):
    def validarCupo(self, cliente: str, monto: float) -> bool:
        return True


# ═══════════════════════ FÁBRICA ABSTRACTA ═══════════════════════
class FabricaEnvio(ABC):
    """Declara la creación de una familia completa de productos compatibles."""

    @abstractmethod
    def crearFlete(self) -> CalculadorFlete: ...

    @abstractmethod
    def crearPeso(self) -> ValidadorPeso: ...

    @abstractmethod
    def crearGuia(self) -> GeneradorGuia: ...

    @abstractmethod
    def crearAviso(self) -> NotificadorEnvio: ...

    @abstractmethod
    def crearCredito(self) -> ValidadorCredito: ...


# ═══════════════════════ FÁBRICAS CONCRETAS ═══════════════════════
class FabricaPaqueteo(FabricaEnvio):
    def crearFlete(self) -> CalculadorFlete: return FletePaqueteo()
    def crearPeso(self) -> ValidadorPeso: return PesoPaqueteo()
    def crearGuia(self) -> GeneradorGuia: return GuiaPaqueteo()
    def crearAviso(self) -> NotificadorEnvio: return AvisoPaqueteo()
    def crearCredito(self) -> ValidadorCredito: return CreditoPaqueteo()


class FabricaCorporativa(FabricaEnvio):
    def crearFlete(self) -> CalculadorFlete: return FleteCorporativa()
    def crearPeso(self) -> ValidadorPeso: return PesoCorporativa()
    def crearGuia(self) -> GeneradorGuia: return GuiaCorporativa()
    def crearAviso(self) -> NotificadorEnvio: return AvisoCorporativa()
    def crearCredito(self) -> ValidadorCredito: return CreditoCorporativa()


class FabricaRemesa(FabricaEnvio):
    def crearFlete(self) -> CalculadorFlete: return FleteRemesa()
    def crearPeso(self) -> ValidadorPeso: return PesoRemesa()
    def crearGuia(self) -> GeneradorGuia: return GuiaRemesa()
    def crearAviso(self) -> NotificadorEnvio: return AvisoRemesa()
    def crearCredito(self) -> ValidadorCredito: return CreditoRemesa()
