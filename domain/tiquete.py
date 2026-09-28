"""
Objetos de dominio del proceso «Venta de tiquete».

Son las partes y el producto que el patrón Builder ensambla paso a paso.
"""
from dataclasses import dataclass

from factories.fabrica_tarifa import Tarifa


@dataclass
class Viaje:
    origen: str
    destino: str


@dataclass
class Silla:
    numero: int
    estado: str = "Disponible"


@dataclass
class Pasajero:
    documento: str
    nombre: str


@dataclass
class Pago:
    metodo: str
    valor: float


@dataclass
class Factura:
    cufe: str
    total: float


@dataclass
class Tiquete:
    """Producto complejo: agrega sus partes, incluida la factura electrónica."""
    numero: str = ""
    fechaVenta: str = ""
    estado: str = "En construcción"
    valorFinal: float = 0.0
    viaje: Viaje | None = None
    silla: Silla | None = None
    pasajero: Pasajero | None = None
    pago: Pago | None = None
    factura: Factura | None = None
    tarifa: Tarifa | None = None
