"""
PATRÓN: BUILDER
PROCESO: Venta de tiquete

Roles del patrón
  Director ............. Taquillero            (ordena los pasos)
  Constructor .......... ConstructorTiquete    (interfaz con los pasos)
  ConstructorConcreto .. ConstructorTiqueteImpl (acumula el tiquete)
  Producto y partes .... Tiquete (+ Viaje, Silla, Pasajero, Pago, Factura) -> /domain
  Colaboración ......... Tarifa llega creada por FabricaTarifa (Factory Method)
"""

import datetime
import hashlib
import logging
import uuid
from abc import ABC, abstractmethod

from domain.tiquete import Factura, Pago, Pasajero, Silla, Tiquete, Viaje
from factories.fabrica_tarifa import Tarifa

logger = logging.getLogger("sigtva.tiquete")


# ═══════════════════════ CONSTRUCTOR (INTERFAZ) ═══════════════════════
class ConstructorTiquete(ABC):
    @abstractmethod
    def fijarViaje(self, v: Viaje) -> None: ...

    @abstractmethod
    def bloquearSilla(self, s: Silla) -> None: ...

    @abstractmethod
    def fijarPasajero(self, p: Pasajero) -> None: ...

    @abstractmethod
    def fijarTarifa(self, t: Tarifa) -> None: ...

    @abstractmethod
    def fijarPago(self, pago: Pago) -> None: ...

    @abstractmethod
    def emitirFactura(self) -> None: ...

    @abstractmethod
    def construir(self) -> Tiquete: ...


# ═══════════════════════ CONSTRUCTOR CONCRETO ═══════════════════════
class ConstructorTiqueteImpl(ConstructorTiquete):
    """Acumula el tiquete paso a paso y solo entrega un producto completo."""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self._tiquete = Tiquete(
            numero=f"TQ-{uuid.uuid4().hex[:6].upper()}",
            fechaVenta=datetime.datetime.now(tz=datetime.UTC).strftime(
                "%Y-%m-%d %H:%M"
            ),
        )

    def fijarViaje(self, v: Viaje) -> None:
        self._tiquete.viaje = v
        logger.info("[Builder] 1. fijarViaje: %s -> %s", v.origen, v.destino)

    def bloquearSilla(self, s: Silla) -> None:
        if s.numero <= 0:
            raise ValueError("Número de silla inválido.")
        s.estado = "Bloqueada"
        self._tiquete.silla = s
        logger.info("[Builder] 2. bloquearSilla: silla %s bloqueada", s.numero)

    def fijarPasajero(self, p: Pasajero) -> None:
        if not p.documento or not p.nombre:
            raise ValueError("El pasajero requiere documento y nombre.")
        self._tiquete.pasajero = p
        logger.info("[Builder] 3. fijarPasajero: %s (doc. %s)", p.nombre, p.documento)

    def fijarTarifa(self, t: Tarifa) -> None:
        self._tiquete.tarifa = t
        self._tiquete.valorFinal = t.calcular()
        logger.info(
            "[Builder] 4. fijarTarifa: %s = $%s",
            t.descripcion(),
            f"{self._tiquete.valorFinal:,.0f}",
        )

    def fijarPago(self, pago: Pago) -> None:
        if self._tiquete.tarifa is None:
            raise ValueError("Debe fijar la tarifa antes del pago.")
        if abs(pago.valor - self._tiquete.valorFinal) > 0.01:
            raise ValueError(
                "El valor del pago no coincide con el valor final del tiquete."
            )
        self._tiquete.pago = pago
        logger.info(
            "[Builder] 5. fijarPago: %s por $%s", pago.metodo, f"{pago.valor:,.0f}"
        )

    def emitirFactura(self) -> None:
        if self._tiquete.pago is None:
            raise ValueError("Debe registrar el pago antes de emitir la factura.")
        t = self._tiquete
        huella = f"{t.numero}|{t.fechaVenta}|{t.pago.valor}"
        cufe = hashlib.sha384(
            huella.encode()
        ).hexdigest()  # simula el CUFE de la factura electrónica
        t.factura = Factura(cufe=cufe, total=t.pago.valor)
        logger.info("[Builder] 6. emitirFactura: CUFE %s...", cufe[:16])

    def construir(self) -> Tiquete:
        t = self._tiquete
        faltantes = [
            nombre
            for nombre, parte in (
                ("viaje", t.viaje),
                ("silla", t.silla),
                ("pasajero", t.pasajero),
                ("tarifa", t.tarifa),
                ("pago", t.pago),
                ("factura", t.factura),
            )
            if parte is None
        ]
        if faltantes:
            raise ValueError(f"Tiquete incompleto, faltan: {', '.join(faltantes)}.")
        t.estado = "Emitido"
        t.silla.estado = "Ocupada"
        logger.info("[Builder] 7. construir: tiquete %s completo y entregado", t.numero)
        self.reset()  # el constructor queda listo para el siguiente tiquete
        return t


# ═══════════════════════ DIRECTOR ═══════════════════════
class Taquillero:
    """Conoce el ORDEN de la venta; no sabe cómo se construye cada parte."""

    def __init__(self, constructor: ConstructorTiquete):
        self._constructor = constructor

    def venderTiquete(
        self,
        viaje: Viaje,
        silla: Silla,
        pasajero: Pasajero,
        tarifa: Tarifa,
        metodoPago: str,
    ) -> Tiquete:
        c = self._constructor
        logger.info("[Builder] El Director (Taquillero) inicia la venta")
        c.fijarViaje(viaje)
        c.bloquearSilla(silla)
        c.fijarPasajero(pasajero)
        c.fijarTarifa(tarifa)
        c.fijarPago(Pago(metodo=metodoPago, valor=tarifa.calcular()))
        c.emitirFactura()
        return c.construir()
