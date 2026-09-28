"""
DEMO — ABSTRACT FACTORY (Registro de envío)

Ejecutar desde la raíz del proyecto:   python demos/demo_abstract_factory.py

Qué demuestra: ServicioRegistroEnvio (cliente) recibe UNA fábrica y arma el
envío usando solo interfaces. Al cambiar la fábrica cambia toda la familia de
productos (flete, peso, guía, aviso, crédito) sin tocar el código del cliente.
"""
from _comun import titulo, seccion

from factories.fabrica_envio import FabricaPaqueteo, FabricaCorporativa, FabricaRemesa
from services.servicio_registro_envio import ServicioRegistroEnvio

FAMILIAS = (("Paqueteo", FabricaPaqueteo), ("Corporativa", FabricaCorporativa), ("Remesa", FabricaRemesa))


def registrar(nombre, clase_fabrica, peso, dims="30x30x30", doc="900123"):
    servicio = ServicioRegistroEnvio(clase_fabrica())
    servicio.fijarModalidad(nombre)
    try:
        e = servicio.construir(peso, dims, "Bogotá", "Cali", doc)
        print(f"   => OK  guía {e.guia.numero} | facturable {e.pesoFacturable} kg | flete ${e.valorFlete:,.0f}")
    except ValueError as err:
        print(f"   => RECHAZADO: {err}")


titulo("DEMO ABSTRACT FACTORY — registro de envíos")

seccion("1. La MISMA petición (20 kg, 30x30x30) con las tres fábricas")
for nombre, clase in FAMILIAS:
    print(f"\n   [{nombre}]")
    registrar(nombre, clase, 20)

seccion("2. Cada familia impone sus reglas: paquete de 40 kg")
for nombre, clase in FAMILIAS:
    print(f"\n   [{nombre}]")
    registrar(nombre, clase, 40)

seccion("3. Peso facturable = máx(real, volumétrico): 5 kg pero caja de 100x50x50 cm")
for nombre, clase in FAMILIAS[:2]:
    print(f"\n   [{nombre}]")
    registrar(nombre, clase, 5, dims="100x50x50")

seccion("4. La Corporativa valida cupo de crédito: 450 kg (flete > $800.000)")
print("\n   [Corporativa]")
registrar("Corporativa", FabricaCorporativa, 450)

seccion("5. La Remesa aplica descuento por volumen: 250 kg")
print("\n   [Remesa]")
registrar("Remesa", FabricaRemesa, 250)

seccion("6. Guías en lote (solo tiene sentido en Remesa): generarLote(3, base=5000)")
for guia in FabricaRemesa().crearGuia().generarLote(3, 5000):
    print(f"   {guia.numero}  {guia.codigoBarras}")
