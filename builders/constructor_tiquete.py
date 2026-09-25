from abc import ABC, abstractmethod
from factories.fabrica_venta import FabricaVenta
from typing import Optional

# --- PARTES DEL PRODUCTO ---
class Viaje:
    def __init__(self, origen: str, destino: str):
        self.origen = origen
        self.destino = destino

class Silla:
    def __init__(self, numero: int, estado: str = "Bloqueada"):
        self.numero = numero
        self.estado = estado

class Pasajero:
    def __init__(self, documento: str, nombre: str):
        self.documento = documento
        self.nombre = nombre

class Pago:
    def __init__(self, metodo: str, valor: float):
        self.metodo = metodo
        self.valor = valor

class Factura:
    def __init__(self, cufe: str, total: float):
        self.cufe = cufe
        self.total = total

# --- PRODUCTO COMPLEJO ---
class Tiquete:
    def __init__(self):
        self.numero: str = ""
        self.fechaVenta: str = ""
        self.estado: str = "Emitido"
        self.valorFinal: float = 0.0
        self.viaje: Optional[Viaje] = None
        self.silla: Optional[Silla] = None
        self.pasajero: Optional[Pasajero] = None
        self.pago: Optional[Pago] = None
        self.factura: Optional[Factura] = None

# --- CONSTRUCTOR INTERFAZ ---
class ConstructorTiquete(ABC):
    @abstractmethod
    def fijarViaje(self, v: Viaje) -> None: pass
    
    @abstractmethod
    def bloquearSilla(self, s: Silla) -> None: pass
    
    @abstractmethod
    def fijarPasajero(self, p: Pasajero) -> None: pass
    
    @abstractmethod
    def fijarTarifa(self, t: float) -> None: pass
    
    @abstractmethod
    def fijarPago(self, pago: Pago) -> None: pass
    
    @abstractmethod
    def emitirFactura(self) -> None: pass
    
    @abstractmethod
    def construir(self) -> Tiquete: pass


# --- CONSTRUCTOR CONCRETO ---
class ConstructorTiqueteImpl(ConstructorTiquete):
    def __init__(self, fabrica_canal: FabricaVenta):
        self.fabrica = fabrica_canal
        self.reset()

    def reset(self):
        self._tiquete = Tiquete()

    def fijarViaje(self, v: Viaje) -> None:
        self._tiquete.viaje = v

    def bloquearSilla(self, s: Silla) -> None:
        bloqueador = self.fabrica.crearBloqueo()
        if bloqueador.bloquear(str(s.numero)):
            self._tiquete.silla = s

    def fijarPasajero(self, p: Pasajero) -> None:
        self._tiquete.pasajero = p

    def fijarTarifa(self, t: float) -> None:
        self._tiquete.valorFinal = t

    def fijarPago(self, pago: Pago) -> None:
        validador = self.fabrica.crearPago()
        if validador.validar({"metodo": pago.metodo, "valor": pago.valor}):
            self._tiquete.pago = pago

    def emitirFactura(self) -> None:
        emisor = self.fabrica.crearFactura()
        factura_data = emisor.emitir({"valorFinal": self._tiquete.valorFinal})
        self._tiquete.factura = Factura(cufe=factura_data["cufe"], total=factura_data["total"])

    def construir(self) -> Tiquete:
        import uuid, datetime
        self._tiquete.numero = f"TQ-{uuid.uuid4().hex[:6].upper()}"
        self._tiquete.fechaVenta = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Generar aviso mediante la fábrica
        notificador = self.fabrica.crearAviso()
        notificador.avisar({"numero": self._tiquete.numero})
        
        resultado = self._tiquete
        self.reset()
        return resultado


# --- DIRECTOR ---
class Taquillero:
    def __init__(self, constructor: ConstructorTiquete):
        self.builder = constructor

    def venderTiquete(self, viaje: Viaje, silla: Silla, pasajero: Pasajero, pago: Pago, tarifa: float) -> Tiquete:
        self.builder.fijarViaje(viaje)
        self.builder.bloquearSilla(silla)
        self.builder.fijarPasajero(pasajero)
        self.builder.fijarTarifa(tarifa)
        self.builder.fijarPago(pago)
        self.builder.emitirFactura()
        return self.builder.construir()