"""
DEMO — BUILDER (Venta de tiquete)

Ejecutar desde la raíz del proyecto:   python demos/demo_builder.py

Qué demuestra: el tiquete se construye PASO A PASO. El Director (Taquillero)
conoce el orden; el constructor concreto acumula las partes y solo entrega un
producto COMPLETO. La Tarifa llega ya creada por su fábrica (Factory Method).
"""
from _comun import seccion, titulo
from builders.constructor_tiquete import ConstructorTiqueteImpl, Taquillero
from domain.tiquete import Pago, Pasajero, Silla, Viaje
from factories.fabrica_tarifa import FabricaTarifaEstudiante, FabricaTarifaOrdinaria

titulo("DEMO BUILDER — construcción del tiquete")

constructor = ConstructorTiqueteImpl()

seccion("1. El Director ordena los pasos (Taquillero.venderTiquete)")
tarifa = FabricaTarifaEstudiante().crearTarifa(85000)      # colaboración con Factory Method
t1 = Taquillero(constructor).venderTiquete(
    Viaje("Bogotá", "Cali"), Silla(7), Pasajero("1018234567", "Ana Gómez"), tarifa, "PSE")

seccion("2. Producto final: el tiquete agrega todas sus partes")
print(f"   Tiquete {t1.numero} [{t1.estado}] {t1.fechaVenta}")
print(f"   Viaje    : {t1.viaje.origen} -> {t1.viaje.destino}")
print(f"   Silla    : {t1.silla.numero} ({t1.silla.estado})")
print(f"   Pasajero : {t1.pasajero.nombre} ({t1.pasajero.documento})")
print(f"   Tarifa   : {t1.tarifa.descripcion()}")
print(f"   Pago     : {t1.pago.metodo} ${t1.pago.valor:,.0f}")
print(f"   Factura  : total ${t1.factura.total:,.0f}  CUFE {t1.factura.cufe[:24]}...")

seccion("3. Sin Director, paso a paso: construir() rechaza un tiquete incompleto")
constructor.fijarViaje(Viaje("Bogotá", "Medellín"))
constructor.bloquearSilla(Silla(3))
try:
    constructor.construir()
except ValueError as e:
    print(f"   RECHAZADO -> {e}")

seccion("4. El orden importa: no se puede pagar antes de fijar la tarifa")
try:
    constructor.fijarPago(Pago("Efectivo", 85000))
except ValueError as e:
    print(f"   RECHAZADO -> {e}")

seccion("5. El mismo constructor se reutiliza: otro tiquete, otro número")
constructor.reset()  # descarta el tiquete incompleto del punto 3
t2 = Taquillero(constructor).venderTiquete(
    Viaje("Cali", "Bogotá"), Silla(12), Pasajero("52111222", "Luis Ruiz"),
    FabricaTarifaOrdinaria().crearTarifa(85000), "Efectivo")
print(f"   Primer tiquete: {t1.numero}   Segundo tiquete: {t2.numero}")
