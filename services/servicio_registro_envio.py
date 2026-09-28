"""
PATRÓN: ABSTRACT FACTORY — rol CLIENTE
Proceso: Registro de envío

ServicioRegistroEnvio recibe la fábrica de la modalidad y arma el envío
usando ÚNICAMENTE las interfaces de producto. No sabe si trabaja con
Paqueteo, Corporativa o Remesa: cambiar de familia es cambiar la fábrica.
"""
from domain.envio import Envio, Ruta, Cliente, calcularPesoFacturable
from factories.fabrica_envio import FabricaEnvio


class ServicioRegistroEnvio:
    def __init__(self, f: FabricaEnvio):
        self._fabrica = f
        self._modalidad = "Estándar"

    def fijarModalidad(self, m: str) -> None:
        """Nombre de la modalidad que quedará en Envio.tipoServicio."""
        self._modalidad = m

    def construir(self, peso: float, dims: str, origen: str, destino: str,
                  documentoRemitente: str, valorDeclarado: float = 0.0) -> Envio:
        # 1. Peso: la familia decide el tope (usa máx(real, volumétrico)).
        if not self._fabrica.crearPeso().validar(peso, dims):
            pesoFact = calcularPesoFacturable(peso, dims)
            raise ValueError(
                f"El peso facturable ({pesoFact} kg) supera el tope de la modalidad {self._modalidad}."
            )
        pesoFacturable = calcularPesoFacturable(peso, dims)

        # 2. Flete: la familia decide la tarifa.
        flete = self._fabrica.crearFlete().calcular(f"{origen}-{destino}", pesoFacturable)

        # 3. Crédito: la familia decide si exige cupo.
        if not self._fabrica.crearCredito().validarCupo(documentoRemitente, flete):
            raise ValueError(f"El flete (${flete:,.0f}) supera el cupo de crédito del cliente.")

        # 4. Guía: la familia decide el formato.
        guia = self._fabrica.crearGuia().generar({"documento": documentoRemitente})

        # 5. Ensamble del producto y aviso.
        envio = Envio(
            pesoFacturable=pesoFacturable,
            valorDeclarado=valorDeclarado,
            valorFlete=flete,
            tipoServicio=self._modalidad,
            guia=guia,
            ruta=Ruta(origen, destino),
            cliente=Cliente(documentoRemitente),
        )
        self._fabrica.crearAviso().avisar(envio)
        return envio
