"""
PATRÓN: SINGLETON
PROCESO: Venta de tiquete (SecuenciadorTiquete) y Registro de envío
         (SecuenciadorGuia, usado por ServicioPrototipos para numerar guías)

Roles del patrón
  Singleton ......... SecuenciadorTiquete / SecuenciadorGuia (consecutivo
                      único nacional, incremento atómico con candado)
  Clientes .......... ProcesoVentaTiquete, ServicioPrototipos y demos

Un contador global con `itertools.count` o una variable de módulo se rompe
con hilos (dos hilos pueden leer el mismo valor antes de incrementar).
El Singleton con candado garantiza: un número, una sola vez.
"""
import logging
import threading

logger = logging.getLogger("sigtva.singleton")


class _SecuenciadorBase:
    """Consecutivo único thread-safe. No instanciar directo: usar las subclases."""

    _instancia = None
    _candado = threading.Lock()
    _prefijo = ""
    _inicio = 1
    _ancho = 0  # 0 = sin relleno; 10 = guía de 10 dígitos

    def __new__(cls):
        if cls._instancia is None:
            with cls._candado:
                if cls._instancia is None:
                    nuevo = super().__new__(cls)
                    nuevo._consecutivo = cls._inicio - 1
                    cls._instancia = nuevo
        return cls._instancia

    @classmethod
    def obtenerInstancia(cls):  # noqa: N802 - nombre UML/diagrama
        return cls()

    def siguiente(self) -> str:
        """Entrega el siguiente número. Atómico: jamás se repite ni se salta."""
        with self._candado:
            self._consecutivo += 1
            numero = str(self._consecutivo)
            if self._ancho:
                numero = numero.zfill(self._ancho)
            resultado = f"{self._prefijo}{numero}"
        logger.info("[Singleton] %s.siguiente() -> %s", type(self).__name__, resultado)
        return resultado

    def reiniciar(self, inicio: int = 1) -> None:
        """Solo para demos y pruebas."""
        with self._candado:
            self._consecutivo = inicio - 1


class SecuenciadorTiquete(_SecuenciadorBase):
    """Consecutivo nacional de tiquetes (formato TQ-000001)."""

    _prefijo = "TQ-"
    _inicio = 1
    _ancho = 6


class SecuenciadorGuia(_SecuenciadorBase):
    """Consecutivo nacional de guías: 10 dígitos (thread-safe para 150-400/día)."""

    _prefijo = ""
    _inicio = 7000000001
    _ancho = 10
