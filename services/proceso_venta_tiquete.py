"""
Capa de LÓGICA — caso de uso «Vender tiquete».

Aquí trabajan JUNTOS dos patrones:
  1. Factory Method: la fábrica de tarifa crea la Tarifa.
  2. Builder: el Taquillero (Director) arma el Tiquete y recibe esa Tarifa ya creada.
Después se persiste con los DAO.
"""
import logging

from builders.constructor_tiquete import ConstructorTiqueteImpl, Taquillero
from dao.entidades_base_dao import ClienteDAO
from dao.operaciones_dao import ViajeDAO
from dao.transacciones_dao import TiqueteDAO, FacturaDAO
from domain.tiquete import Viaje, Silla, Pasajero
from factories.fabrica_tarifa import (
    FabricaTarifaOrdinaria, FabricaTarifaEstudiante, FabricaTarifaAdultoMayor)
from services.traza import CapturaTraza

logger = logging.getLogger("sigtva.tiquete")


class ProcesoVentaTiquete:
    PRECIO_BASE = 85000.0  # Precio de lista por pasajero (lo fija el servidor, no el formulario).

    # Selección del creador de tarifa según lo elegido en pantalla.
    FABRICAS_TARIFA = {
        "ordinaria": FabricaTarifaOrdinaria,
        "estudiante": FabricaTarifaEstudiante,
        "adulto_mayor": FabricaTarifaAdultoMayor,
    }

    @classmethod
    def opciones_tarifa(cls) -> list:
        """Opciones para el formulario, generadas por el propio Factory Method."""
        opciones = []
        for clave, clase in cls.FABRICAS_TARIFA.items():
            tarifa = clase().crearTarifa(cls.PRECIO_BASE)
            opciones.append({"clave": clave, "descripcion": tarifa.descripcion(), "valor": tarifa.calcular()})
        return opciones

    def vender(self, id_viaje: int, documento: str, nombre: str, numero_silla: int,
               tipo_tarifa: str, metodo_pago: str, id_usuario: str) -> dict:
        viaje_db = ViajeDAO.consultarViaje(id_viaje)
        if viaje_db is None:
            raise ValueError("El viaje seleccionado no existe.")
        clase_creador = self.FABRICAS_TARIFA.get(tipo_tarifa)
        if clase_creador is None:
            raise ValueError("Tipo de tarifa desconocido.")

        with CapturaTraza("sigtva.tiquete") as traza:
            # ── Patrón 1: Factory Method crea la tarifa ──
            creador = clase_creador()
            tarifa = creador.crearTarifa(self.PRECIO_BASE)
            logger.info("[Factory Method] %s.crearTarifa(%s) -> %s",
                        type(creador).__name__, f"{self.PRECIO_BASE:,.0f}", type(tarifa).__name__)

            # ── Patrón 2: Builder arma el tiquete (dirigido por el Taquillero) ──
            taquillero = Taquillero(ConstructorTiqueteImpl())
            tiquete = taquillero.venderTiquete(
                viaje=Viaje(viaje_db.origen, viaje_db.destino),
                silla=Silla(numero_silla),
                pasajero=Pasajero(documento, nombre),
                tarifa=tarifa,
                metodoPago=metodo_pago,
            )

            # ── Persistencia (se conservan el número y el CUFE que generó el Builder) ──
            cliente = ClienteDAO.registrarCliente(documento, "CC", nombre, "", "")
            ok, msg, tiquete_db = TiqueteDAO.registrarTiquete(
                id_viaje=id_viaje, id_cliente=cliente.id_cliente, id_usuario_registra=id_usuario,
                numero_silla=tiquete.silla.numero, precio_total=tiquete.valorFinal,
                canal_venta="Web", numero_tiquete=tiquete.numero)
            if not ok:
                raise ValueError(msg)
            ok, msg, factura_db = FacturaDAO.registrarFactura(
                monto_total=tiquete.factura.total, id_cajero=id_usuario,
                id_tiquete=tiquete_db.id_tiquete, cufe=tiquete.factura.cufe)
            if not ok:
                raise ValueError(msg)

        return {
            "tipo": "tiquete", "tiquete": tiquete, "tiquete_db": tiquete_db, "factura": factura_db,
            "cliente": cliente, "traza": traza.mensajes,
            "patrones": ["Factory Method", "Builder"],
        }
