"""
Objetos de dominio del proceso "Registro de envío".

Son las clases que el patrón Abstract Factory produce y ensambla; no tienen
nada que ver con las tablas de SQLAlchemy (esas viven en /models).
"""
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mementos.recuerdos import InstantaneaEnvio

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
class Receptor:
    """Quien retira el envío en destino (destinatario o tercero autorizado)."""
    documento: str
    esTercero: bool = False
    autorizacionFirmada: bool = False
    firma: str = ""
    pagoRecibido: float = 0.0


@dataclass
class ViajeCarga:
    """Viaje de un bus: capacidad de carga y peso ya asignado (RF-03)."""
    idViaje: int
    origen: str
    destino: str
    capacidadCarga: float
    pesoAsignado: float = 0.0


@dataclass
class Envio:
    """Producto final, Originador del patrón Memento y Contexto del patrón State.

    La guía es composición: nace y muere con el envío. Como originador,
    captura su propio estado con crearRecuerdo() y lo restaura con
    restaurar() sin exponer sus campos. Como contexto de State, guarda la
    referencia a su estado actual y le delega cada operación del ciclo de
    vida; cada transición se registra en el Historial y genera la
    Notificación (RF-04).
    """
    pesoFacturable: float = 0.0
    valorDeclarado: float = 0.0
    valorFlete: float = 0.0
    tipoServicio: str = ""
    estado: str = "Registrado"
    guia: Guia | None = None
    ruta: Ruta | None = None
    cliente: Cliente | None = None

    # --- campos del ciclo de vida (State) ---
    terminalActual: str = ""
    fechaDisponible: object = None   # datetime.datetime | None
    documentoDestinatario: str = ""
    fletePendiente: float = 0.0
    cargoBodegaje: float = 0.0
    idViaje: int | None = None
    cambios: list = None            # historial de transiciones (estado_anterior -> estado_nuevo)

    def __post_init__(self) -> None:
        if self.cambios is None:
            self.cambios = []
        if self.ruta is not None and not self.terminalActual:
            self.terminalActual = self.ruta.origen

    # --- Memento ---
    def crearRecuerdo(self) -> "InstantaneaEnvio":
        """Captura estado, peso, valor y tipo de servicio en una instantánea."""
        from mementos.recuerdos import InstantaneaEnvio

        return InstantaneaEnvio(self.estado, self.pesoFacturable,
                                self.valorDeclarado, self.tipoServicio)

    def restaurar(self, r: "InstantaneaEnvio") -> None:
        """Repone los campos capturados en la instantánea."""
        self.estado = r.obtenerEstado()
        self.pesoFacturable = r.obtenerPesoFacturable()
        self.valorDeclarado = r.obtenerValorDeclarado()
        self.tipoServicio = r.obtenerTipoServicio()

    # --- State: delegación y transición ---
    def cambiarEstado(self, nuevo: object, detalle: str = "") -> None:
        """Registra la transición y actualiza el estado actual."""
        anterior = self.estado
        if anterior != nuevo.nombre():
            self.cambios.append(_Cambio(anterior, nuevo.nombre(), detalle))
        self.estado = nuevo.nombre()
        if hasattr(nuevo, "setContexto"):
            nuevo.setContexto(self)

    def _estadoActual(self):
        from states.estados_envio import reconstruirEstado

        estado = self.estado
        if isinstance(estado, str):
            estado = reconstruirEstado(estado, self.cambios, self)
        else:
            if getattr(estado, "contexto", None) is None:
                estado.setContexto(self)
        return estado

    def despachar(self, viaje) -> None:
        self._estadoActual().despachar(viaje)

    def descargar(self, terminal: str) -> None:
        self._estadoActual().descargar(terminal)

    def entregar(self, receptor) -> None:
        self._estadoActual().entregar(receptor)

    def revisarBodegaje(self, fecha) -> float:
        return self._estadoActual().revisarBodegaje(fecha)

    def registrarNovedad(self, motivo: str) -> None:
        self._estadoActual().registrarNovedad(motivo)

    def liberar(self) -> None:
        self._estadoActual().liberar()

    def abrirReclamacion(self, descripcion: str) -> None:
        self._estadoActual().abrirReclamacion(descripcion)

    def resolverReclamacion(self) -> None:
        self._estadoActual().resolverReclamacion()

    def operacionesPermitidas(self) -> list[str]:
        return self._estadoActual().operacionesPermitidas()

    def _estadoActual(self):
        from states.estados_envio import reconstruirEstado

        if isinstance(self.estado, str):
            return reconstruirEstado(self.estado, self.cambios, self)
        return self.estado

    def destino(self) -> str:
        return self.ruta.destino if self.ruta else ""

    def saldoPendiente(self) -> float:
        return self.fletePendiente + self.cargoBodegaje


@dataclass
class _Cambio:
    anterior: str
    nuevo: str
    detalle: str
