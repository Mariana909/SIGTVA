"""
PATRÓN: SINGLETON
PROCESO: Venta de tiquete — validación de soportes de tarifa especial

Roles del patrón
  Singleton ......... ValidadorTarifaEspecial (única caché de soportes ya
                      verificados; no reconsulta en cada venta)
  Clientes .......... ProcesoVentaTiquete y demos

Reglas (del diseño): Plena no exige soporte; Adulto Mayor exige 60 años o
más; Estudiante exige carné vigente; Infante exige menos de 12 años. Si el
soporte es inválido se cobra tarifa plena y queda auditoría.
"""
import logging
import threading

logger = logging.getLogger("sigtva.singleton")


class ValidadorTarifaEspecial:
    """Caché compartida de validaciones. El primer uso consulta, los demás reutilizan."""

    _instancia = None
    _candado = threading.Lock()

    def __new__(cls):
        if cls._instancia is None:
            with cls._candado:
                if cls._instancia is None:
                    cls._instancia = super().__new__(cls)
                    cls._instancia._cache = {}
                    cls._instancia._consultas = 0
        return cls._instancia

    @classmethod
    def obtenerInstancia(cls) -> "ValidadorTarifaEspecial":
        return cls()

    def validar(self, tipo_tarifa: str, soporte: str) -> bool:
        """True si el soporte respalda el descuento. Usa caché (atómico)."""
        with self._candado:
            if (tipo_tarifa, soporte) in self._cache:
                logger.info("[Singleton] Soporte '%s' reutilizado de caché", soporte)
                return self._cache[(tipo_tarifa, soporte)]
            self._consultas += 1
            valido = self._regla(tipo_tarifa, soporte)
            self._cache[(tipo_tarifa, soporte)] = valido
            logger.info("[Singleton] Soporte '%s' validado: %s (consultas reales: %d)",
                        soporte, valido, self._consultas)
            return valido

    def _regla(self, tipo_tarifa: str, soporte: str) -> bool:
        if tipo_tarifa == "ordinaria":
            return True
        if tipo_tarifa == "estudiante":
            return soporte.startswith("CARNE-")
        if tipo_tarifa == "adulto_mayor":
            return soporte.startswith("EDAD:") and int(soporte.split(":")[1]) >= 60
        if tipo_tarifa == "infante":
            return soporte.startswith("EDAD:") and int(soporte.split(":")[1]) < 12
        return False

    def limpiar(self) -> None:
        """Solo para demos y pruebas."""
        with self._candado:
            self._cache.clear()
            self._consultas = 0
