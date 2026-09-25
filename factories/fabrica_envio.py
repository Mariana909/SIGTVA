from abc import ABC, abstractmethod

# --- INTERFACES DE PRODUCTOS ---
class CalculadorFlete(ABC):
    @abstractmethod
    def calcular(self, ruta: str, peso: float) -> float: pass
    
    @abstractmethod
    def obtenerPrioridad(self) -> int: pass

class ValidadorPeso(ABC):
    @abstractmethod
    def validar(self, peso: float, dims: str) -> bool: pass

class GeneradorGuia(ABC):
    @abstractmethod
    def generar(self, datos: dict) -> dict: pass

class NotificadorEnvio(ABC):
    @abstractmethod
    def avisar(self, envio_data: dict) -> None: pass

class ValidadorCredito(ABC):
    @abstractmethod
    def validarCupo(self, cliente: str, monto: float) -> bool: pass


# --- IMPLEMENTACIONES PAQUETEO ---
class FletePaqueteo(CalculadorFlete):
    def calcular(self, ruta: str, peso: float) -> float: return peso * 2500.0
    def obtenerPrioridad(self) -> int: return 1

class PesoPaqueteo(ValidadorPeso):
    def __init__(self): self.maxKg = 30
    def validar(self, peso: float, dims: str) -> bool: return peso <= self.maxKg

class GuiaPaqueteo(GeneradorGuia):
    def generar(self, datos: dict) -> dict:
        import random
        num = "".join([str(random.randint(0,9)) for _ in range(10)])
        return {"numero": num, "codigoBarras": f"PAQ-{num}"}

class AvisoPaqueteo(NotificadorEnvio):
    def avisar(self, envio_data: dict) -> None: pass

class CreditoPaqueteo(ValidadorCredito):
    def validarCupo(self, cliente: str, monto: float) -> bool: return True  # Contado/Contraentrega


# --- IMPLEMENTACIONES CORPORATIVA ---
class FleteCorporativa(CalculadorFlete):
    def calcular(self, ruta: str, peso: float) -> float: return peso * 1800.0  # Tarifa preferencial
    def obtenerPrioridad(self) -> int: return 2

class PesoCorporativa(ValidadorPeso):
    def __init__(self): self.maxKg = 500
    def validar(self, peso: float, dims: str) -> bool: return peso <= self.maxKg

class GuiaCorporativa(GeneradorGuia):
    def generar(self, datos: dict) -> dict:
        import random
        num = "".join([str(random.randint(0,9)) for _ in range(10)])
        return {"numero": num, "codigoBarras": f"CORP-{num}"}

class AvisoCorporativa(NotificadorEnvio):
    def avisar(self, envio_data: dict) -> None: pass

class CreditoCorporativa(ValidadorCredito):
    def validarCupo(self, cliente: str, monto: float) -> bool: return True  # Cupo verificado


# --- IMPLEMENTACIONES REMESA ---
class FleteRemesa(CalculadorFlete):
    def calcular(self, ruta: str, peso: float) -> float: return peso * 1200.0  # Descuento por volumen
    def obtenerPrioridad(self) -> int: return 3

class PesoRemesa(ValidadorPeso):
    def validar(self, peso: float, dims: str) -> bool: return True

class GuiaRemesa(GeneradorGuia):
    def generar(self, datos: dict) -> dict:
        import random
        num = "".join([str(random.randint(0,9)) for _ in range(10)])
        return {"numero": num, "codigoBarras": f"REM-{num}"}

class AvisoRemesa(NotificadorEnvio):
    def avisar(self, envio_data: dict) -> None: pass

class CreditoRemesa(ValidadorCredito):
    def validarCupo(self, cliente: str, monto: float) -> bool: return True


# --- FABRICA ABSTRACTA ---
class FabricaEnvio(ABC):
    @abstractmethod
    def crearFlete(self) -> CalculadorFlete: pass
    @abstractmethod
    def crearPeso(self) -> ValidadorPeso: pass
    @abstractmethod
    def crearGuia(self) -> GeneradorGuia: pass
    @abstractmethod
    def crearAviso(self) -> NotificadorEnvio: pass
    @abstractmethod
    def crearCredito(self) -> ValidadorCredito: pass


# --- FABRICAS CONCRETAS ---
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