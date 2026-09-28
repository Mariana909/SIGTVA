"""
Objetos de dominio del proceso «Registro de envío».

Son las clases que el patrón Abstract Factory produce y ensambla; no tienen
nada que ver con las tablas de SQLAlchemy (esas viven en /models).
"""
import re
from dataclasses import dataclass
from typing import Optional

# cm³ por kg. Equivale a 400 kg/m³, referencia habitual del transporte terrestre de carga.
FACTOR_VOLUMETRICO = 2500


def calcularPesoFacturable(peso: float, dims: str) -> float:
    """Regla del diseño: el peso facturable es máx(peso real, peso volumétrico).

    dims llega como "LargoxAnchoxAlto" en centímetros, por ejemplo "30x30x30".
    """
    try:
        largo, ancho, alto = (float(x) for x in re.split(r"[xX*, ]+", dims.strip()))
    except (ValueError, AttributeError):
        raise ValueError("Dimensiones inválidas. Use el formato LargoxAnchoxAlto en cm (ej. 30x30x30).")
    if min(largo, ancho, alto) <= 0:
        raise ValueError("Las dimensiones deben ser mayores que cero.")
    volumetrico = (largo * ancho * alto) / FACTOR_VOLUMETRICO
    return round(max(peso, volumetrico), 2)


@dataclass
class Guia:
    numero: str
    codigoBarras: str


@dataclass
class Ruta:
    origen: str
    destino: str


@dataclass
class Cliente:
    documento: str


@dataclass
class Envio:
    """Producto final. La guía es composición: nace y muere con el envío."""
    pesoFacturable: float = 0.0
    valorDeclarado: float = 0.0
    valorFlete: float = 0.0
    tipoServicio: str = ""
    estado: str = "Registrado"
    guia: Optional[Guia] = None
    ruta: Optional[Ruta] = None
    cliente: Optional[Cliente] = None
