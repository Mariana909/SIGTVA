"""
PATRÓN: ABSTRACT FACTORY — rol CLIENTE
Proceso: Registro de envío

ServicioRegistroEnvio recibe la fábrica de la modalidad y arma el envío
usando ÚNICAMENTE las interfaces de producto. No sabe si trabaja con
Paqueteo, Corporativa o Remesa: cambiar de familia es cambiar la fábrica.
"""
import logging

from domain.envio import Cliente, Envio, Ruta, calcularPesoFacturable
from factories.fabrica_envio import FabricaEnvio

logger = logging.getLogger("sigtva.envio")


def _creado(metodo: str, producto):
    """Deja constancia de qué producto concreto entregó la fábrica."""
    logger.info("[Abstract Factory] %s -> %s", metodo, type(producto).__name__)
    return producto


class ServicioRegistroEnvio:
    def __init__(self, f: FabricaEnvio):
        self._fabrica = f
        self._modalidad = "Estándar"

    def fijarModalidad(self, m: str) -> None:
        """Nombre de la modalidad que quedará en Envio.tipoServicio."""
        self._modalidad = m

    def construir(self, peso: float, dims: str, origen: str, destino: str,
                  documentoRemitente: str, valorDeclarado: float = 0.0) -> Envio:
        logger.info("[Abstract Factory] Familia seleccionada: %s", type(self._fabrica).__name__)

        # 1. Peso: la familia decide el tope (usa máx(real, volumétrico)).
        validador = _creado("crearPeso()", self._fabrica.crearPeso())
        pesoFacturable = calcularPesoFacturable(peso, dims)
        if not validador.validar(peso, dims):
            logger.info("[Abstract Factory] Peso facturable %s kg RECHAZADO por la familia", pesoFacturable)
            raise ValueError(
                f"El peso facturable ({pesoFacturable} kg) supera el tope de la modalidad {self._modalidad}."
            )
        logger.info("[Abstract Factory] Peso facturable %s kg aceptado (real %s kg)", pesoFacturable, peso)

        # 2. Flete: la familia decide la tarifa.
        calculador = _creado("crearFlete()", self._fabrica.crearFlete())
        flete = calculador.calcular(f"{origen}-{destino}", pesoFacturable)
        logger.info("[Abstract Factory] Flete calculado: $%s (prioridad %s)",
                    f"{flete:,.0f}", calculador.obtenerPrioridad())

        # 3. Crédito: la familia decide si exige cupo.
        credito = _creado("crearCredito()", self._fabrica.crearCredito())
        if not credito.validarCupo(documentoRemitente, flete):
            logger.info("[Abstract Factory] Cupo de crédito insuficiente")
            raise ValueError(f"El flete (${flete:,.0f}) supera el cupo de crédito del cliente.")

        # 4. Guía: la familia decide el formato.
        generador = _creado("crearGuia()", self._fabrica.crearGuia())
        guia = generador.generar({"documento": documentoRemitente})

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
        _creado("crearAviso()", self._fabrica.crearAviso()).avisar(envio)
        return envio
