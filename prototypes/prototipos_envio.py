"""
PATRÓN: PROTOTYPE
PROCESO: Registro de envío — radicación de remesa múltiple por clonación

Roles del patrón
  Prototipo (interfaz) ... PrototipoGuia  -> declara clonar()
  Prototipos concretos .... Guia (copia SUPERFICIAL: sus campos son valores),
                            Tula y Remesa (copia PROFUNDA: cada clon necesita
                            su propia lista de guías y su precinto)
  Registro ................ RegistroPrototipos (es Singleton: una sola
                            plantilla de cada tipo en todo el sistema)
  Cliente ................. ServicioPrototipos (ver /services)

Por qué Prototype y no reconstruir: la remesa repite el mismo remitente en
todas las guías; redigitarlo N veces invita a inconsistencias que rompen la
consolidación. Se clona la guía base y solo cambia el destino.
"""
import copy
import logging
import threading
from abc import ABC, abstractmethod

logger = logging.getLogger("sigtva.prototipos")


# ═══════════════════════ PROTOTIPO (INTERFAZ) ═══════════════════════
class PrototipoGuia(ABC):
    @abstractmethod
    def clonar(self) -> "PrototipoGuia":
        """PROTOTYPE: devuelve una copia del ejemplar, no una instancia nueva."""


# ═══════════════════════ PROTOTIPOS CONCRETOS ═══════════════════════
class Guia(PrototipoGuia):
    """Guía base: solo guarda valores (número, remitente, servicio).

    Copia SUPERFICIAL: basta copy.copy porque no hay colecciones internas;
    cada clon recibe después su número único y su destino.
    """

    def __init__(self, numero: str, remitente: str, servicio: str):
        self.numero = numero
        self.remitente = remitente
        self.servicio = servicio

    def clonar(self) -> "Guia":
        clon = copy.copy(self)
        logger.info("[Prototype] Guia.clonar: copia superficial de la guía %s", self.numero)
        return clon


class Tula(PrototipoGuia):
    """Tula estándar por destino: agrupa las guías bajo un precinto numerado.

    Copia PROFUNDA: el clon necesita su PROPIA lista de guías y su precinto;
    con copia superficial, sellar una tula contaminaría la plantilla.
    """

    def __init__(self, precinto: str, destino: str):
        self.precinto = precinto
        self.destino = destino
        self.guias: list = []

    def clonar(self) -> "Tula":
        clon = copy.deepcopy(self)
        logger.info("[Prototype] Tula.clonar: copia profunda (lista propia) del precinto %s",
                    self.precinto)
        return clon


class Remesa(PrototipoGuia):
    """Remesa corporativa: lote de guías de un mismo cliente.

    Copia PROFUNDA por la misma razón que Tula: el lote pertenece al clon.
    """

    def __init__(self, numero: str, cliente: str):
        self.numero = numero
        self.cliente = cliente
        self.guias: list = []

    def clonar(self) -> "Remesa":
        clon = copy.deepcopy(self)
        logger.info("[Prototype] Remesa.clonar: copia profunda del lote %s", self.numero)
        return clon


# ═══════════════════════ REGISTRO (ES SINGLETON) ═══════════════════════
class RegistroPrototipos:
    """Guarda una plantilla por clave y entrega copias.

    Es Singleton (ver /singletons): una sola colección de plantillas en todo
    el sistema, creada una vez de forma thread-safe.
    """

    _instancia = None
    _candado = threading.Lock()

    def __new__(cls):
        if cls._instancia is None:
            with cls._candado:
                if cls._instancia is None:
                    cls._instancia = super().__new__(cls)
                    cls._instancia._plantillas = {}
        return cls._instancia

    def registrar(self, clave: str, prototipo: PrototipoGuia) -> None:
        with self._candado:
            self._plantillas[clave] = prototipo
        logger.info("[Prototype] Plantilla registrada: '%s' -> %s",
                    clave, type(prototipo).__name__)

    def clonar(self, clave: str) -> PrototipoGuia:
        with self._candado:
            prototipo = self._plantillas.get(clave)
        if prototipo is None:
            raise ValueError(f"No hay plantilla registrada con la clave '{clave}'.")
        return prototipo.clonar()

    def claves(self) -> list:
        """Claves registradas (para pantallas y demos)."""
        return sorted(self._plantillas)
