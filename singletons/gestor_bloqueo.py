"""
PATRÓN: SINGLETON
PROCESO: Venta de tiquete — bloqueo transaccional de silla

Roles del patrón
  Singleton ......... GestorBloqueoSillas (constructor privado, instancia
                      estática, obtenerInstancia(); todo acceso sincronizado)
  Clientes .......... ProcesoVentaTiquete (ver /services) y las 200 taquillas

Por qué Singleton y no una variable global: el mapa de bloqueos con su
expiración automática debe ser ÚNICO en todo el proceso; dos gestores
venderían la misma silla. La concurrencia se resuelve con un candado: cada
operación que lee y modifica el mapa es atómica.
"""
import logging
import threading
import time

logger = logging.getLogger("sigtva.singleton")

# Segundos que dura un bloqueo de silla (plazo renovable de la taquilla).
DURACION_BLOQUEO = 180.0


class GestorBloqueoSillas:
    """Único mapa de sillas bloqueadas (viaje, silla) -> (canal, expira_en)."""

    _instancia = None
    _candado = threading.Lock()

    def __new__(cls):
        if cls._instancia is None:
            with cls._candado:
                if cls._instancia is None:  # doble comprobación: seguro con hilos
                    cls._instancia = super().__new__(cls)
                    cls._instancia._bloqueos = {}
        return cls._instancia

    @classmethod
    def obtenerInstancia(cls) -> "GestorBloqueoSillas":
        """Punto global de acceso (equivalente UML a getInstancia())."""
        return cls()

    def bloquear(self, id_viaje: int, numero_silla: int, canal: str,
                 duracion: float = DURACION_BLOQUEO) -> bool:
        """Reserva la silla si está libre o su bloqueo expiró. Atómico."""
        ahora = time.monotonic()
        with self._candado:
            self._expirar(ahora)
            clave = (id_viaje, numero_silla)
            if clave in self._bloqueos:
                logger.info("[Singleton] Silla %s del viaje %s OCUPADA (la tiene %s)",
                            numero_silla, id_viaje, self._bloqueos[clave][0])
                return False
            self._bloqueos[clave] = (canal, ahora + duracion)
            logger.info("[Singleton] Silla %s del viaje %s bloqueada por %s",
                        numero_silla, id_viaje, canal)
            return True

    def liberar(self, id_viaje: int, numero_silla: int) -> None:
        with self._candado:
            self._bloqueos.pop((id_viaje, numero_silla), None)

    def bloqueadas(self) -> int:
        with self._candado:
            self._expirar(time.monotonic())
            return len(self._bloqueos)

    def limpiar(self) -> None:
        """Solo para demos y pruebas: vacía el mapa."""
        with self._candado:
            self._bloqueos.clear()

    def _expirar(self, ahora: float) -> None:
        """Saca los bloqueos vencidos. Se llama SIEMPRE con el candado tomado."""
        vencidas = [k for k, (_, expira) in self._bloqueos.items() if expira <= ahora]
        for k in vencidas:
            del self._bloqueos[k]
