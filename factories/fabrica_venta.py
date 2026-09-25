from abc import ABC, abstractmethod

# --- INTERFACES DE PRODUCTOS ---
class BloqueoSilla(ABC):
    @abstractmethod
    def bloquear(self, silla: str) -> bool: pass
    
    @abstractmethod
    def liberar(self, silla: str) -> None: pass

class ValidadorPago(ABC):
    @abstractmethod
    def validar(self, datos: dict) -> bool: pass

class EmisorFactura(ABC):
    @abstractmethod
    def emitir(self, tiquete_data: dict) -> dict: pass

class Notificador(ABC):
    @abstractmethod
    def avisar(self, tiquete_data: dict) -> None: pass


# --- IMPLEMENTACIONES TAQUILLA ---
class BloqueoTaquilla(BloqueoSilla):
    def __init__(self):
        self.tiempoSeg = 180

    def bloquear(self, silla: str) -> bool:
        return True  # Bloqueo local por 3 minutos

    def liberar(self, silla: str) -> None: pass

class PagoTaquilla(ValidadorPago):
    def validar(self, datos: dict) -> bool:
        return True  # Pago por datáfono

class FacturaTaquilla(EmisorFactura):
    def emitir(self, tiquete_data: dict) -> dict:
        return {"cufe": "POS-TAQUILLA-LOCAL", "total": tiquete_data.get("valorFinal", 0.0)}

class AvisoTaquilla(Notificador):
    def avisar(self, tiquete_data: dict) -> None: pass


# --- IMPLEMENTACIONES WEB ---
class BloqueoWeb(BloqueoSilla):
    def bloquear(self, silla: str) -> bool:
        return True  # Bloqueo distribuido

    def liberar(self, silla: str) -> None: pass

class PagoWeb(ValidadorPago):
    def validar(self, datos: dict) -> bool:
        return True  # Pasarela de pagos

class FacturaWeb(EmisorFactura):
    def emitir(self, tiquete_data: dict) -> dict:
        return {"cufe": "CUFE-WEB-ELECTRONICA-999", "total": tiquete_data.get("valorFinal", 0.0)}

class AvisoWeb(Notificador):
    def avisar(self, tiquete_data: dict) -> None: pass


# --- IMPLEMENTACIONES ALIADA ---
class BloqueoAliada(BloqueoSilla):
    def bloquear(self, silla: str) -> bool: return True
    def liberar(self, silla: str) -> None: pass

class PagoAliada(ValidadorPago):
    def validar(self, datos: dict) -> bool: return True  # Voucher

class FacturaAliada(EmisorFactura):
    def emitir(self, tiquete_data: dict) -> dict:
        return {"cufe": "VOUCHER-ALIADO-888", "total": tiquete_data.get("valorFinal", 0.0)}

class AvisoAliada(Notificador):
    def avisar(self, tiquete_data: dict) -> None: pass


# --- FABRICA ABSTRACTA ---
class FabricaVenta(ABC):
    @abstractmethod
    def crearBloqueo(self) -> BloqueoSilla: pass
    
    @abstractmethod
    def crearPago(self) -> ValidadorPago: pass
    
    @abstractmethod
    def crearFactura(self) -> EmisorFactura: pass
    
    @abstractmethod
    def crearAviso(self) -> Notificador: pass


# --- FABRICAS CONCRETAS ---
class FabricaTaquilla(FabricaVenta):
    def crearBloqueo(self) -> BloqueoSilla: return BloqueoTaquilla()
    def crearPago(self) -> ValidadorPago: return PagoTaquilla()
    def crearFactura(self) -> EmisorFactura: return FacturaTaquilla()
    def crearAviso(self) -> Notificador: return AvisoTaquilla()

class FabricaWeb(FabricaVenta):
    def crearBloqueo(self) -> BloqueoSilla: return BloqueoWeb()
    def crearPago(self) -> ValidadorPago: return PagoWeb()
    def crearFactura(self) -> EmisorFactura: return FacturaWeb()
    def crearAviso(self) -> Notificador: return AvisoWeb()

class FabricaAliada(FabricaVenta):
    def crearBloqueo(self) -> BloqueoSilla: return BloqueoAliada()
    def crearPago(self) -> ValidadorPago: return PagoAliada()
    def crearFactura(self) -> EmisorFactura: return FacturaAliada()
    def crearAviso(self) -> Notificador: return AvisoAliada()