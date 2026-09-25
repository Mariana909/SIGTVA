from abc import ABC, abstractmethod
from typing import Optional
from factories.fabrica_envio import FabricaEnvio

# --- PARTES DEL PRODUCTO ---
class Guia:
    def __init__(self, numero: str, codigoBarras: str):
        self.numero = numero
        self.codigoBarras = codigoBarras

class Ruta:
    def __init__(self, origen: str, destino: str):
        self.origen = origen
        self.destino = destino

class Bodega:
    def __init__(self, ubicacion: str):
        self.ubicacion = ubicacion

class PlanillaCarga:
    def __init__(self, conductor: str, firma: bool = True):
        self.conductor = conductor
        self.firma = firma

class Cliente:
    def __init__(self, documento: str):
        self.documento = documento


# --- PRODUCTO COMPLEJO ---
class Envio:
    def __init__(self):
        self.pesoFacturable: float = 0.0
        self.valorDeclarado: float = 0.0
        self.tipoServicio: str = ""
        self.estado: str = "Registrado"
        self.guia: Optional[Guia] = None
        self.bodega: Optional[Bodega] = None
        self.planilla: Optional[PlanillaCarga] = None
        self.ruta: Optional[Ruta] = None
        self.cliente: Optional[Cliente] = None

# --- CONSTRUCTOR INTERFAZ ---
class ConstructorEnvio(ABC):
    @abstractmethod
    def inspeccionar( me ) -> None: pass
    @abstractmethod
    def fijarPesoDims(self, peso: float, dims: str) -> None: pass
    @abstractmethod
    def fijarServicio(self, s: str) -> None: pass
    @abstractmethod
    def fijarActores(self, r: str, d: str) -> None: pass
    @abstractmethod
    def fijarPago(self, pago: dict) -> None: pass
    @abstractmethod
    def emitirGuia( me ) -> None: pass
    @abstractmethod
    def fijarBodega(self, b: Bodega) -> None: pass
    @abstractmethod
    def despachar(self, viaje: str) -> None: pass
    @abstractmethod
    def generarPlanilla( me ) -> None: pass
    @abstractmethod
    def construir( me ) -> Envio: pass


# --- CONSTRUCTOR CONCRETO ---
class ConstructorEnvioImpl(ConstructorEnvio):
    def __init__(self, fabrica_modalidad: FabricaEnvio):
        self.fabrica = fabrica_modalidad
        self.reset()

    def reset(self):
        self._envio = Envio()

    def inspeccionar(self) -> None:
        self._envio.estado = "Inspeccionado"

    def fijarPesoDims(self, peso: float, dims: str) -> None:
        validador = self.fabrica.crearPeso()
        if validador.validar(peso, dims):
            self._envio.pesoFacturable = peso

    def fijarServicio(self, s: str) -> None:
        self._envio.tipoServicio = s

    def fijarActores(self, r: str, d: str) -> None:
        self._envio.cliente = Cliente(documento=r)

    def fijarPago(self, pago: dict) -> None:
        calculador = self.fabrica.crearFlete()
        ruta_str = f"{self._envio.ruta.origen if self._envio.ruta else 'Origen'}-{self._envio.ruta.destino if self._envio.ruta else 'Destino'}"
        self._envio.valorDeclarado = calculador.calcular(ruta_str, self._envio.pesoFacturable)

    def emitirGuia(self) -> None:
        generador = self.fabrica.crearGuia()
        guia_data = generador.generar({})
        self._envio.guia = Guia(numero=guia_data["numero"], codigoBarras=guia_data["codigoBarras"])

    def fijarBodega(self, b: Bodega) -> None:
        self._envio.bodega = b

    def despachar(self, viaje: str) -> None:
        self._envio.estado = "Despachado"

    def generarPlanilla(self) -> None:
        self._envio.planilla = PlanillaCarga(conductor="Conductor Asignado", firma=True)

    def construir(self) -> Envio:
        notificador = self.fabrica.crearAviso()
        notificador.avisar({"guia": self._envio.guia.numero if self._envio.guia else "N/A"})
        
        resultado = self._envio
        self.reset()
        return resultado


# --- DIRECTOR ---
class AuxiliarEncomiendas:
    def __init__(self, constructor: ConstructorEnvio):
        self.builder = constructor

    def registrarEnvio(self, peso: float, dims: str, origen: str, destino: str, cliente_doc: str, bodega_ub: str) -> Envio:
        self.builder.inspeccionar()
        self.builder.fijarPesoDims(peso, dims)
        self.builder.fijarServicio("Encomienda Estándar")
        self.builder.fijarActores(cliente_doc, "Destinatario")
        self.builder.fijarBodega(Bodega(bodega_ub))
        self.builder.fijarPago({})
        self.builder.emitirGuia()
        self.builder.generarPlanilla()
        self.builder.despachar("Viaje 101")
        return self.builder.construir()