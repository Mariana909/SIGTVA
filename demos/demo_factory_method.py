"""
DEMO — FACTORY METHOD (Venta de tiquete: creación de la tarifa)

Ejecutar desde la raíz del proyecto:   python demos/demo_factory_method.py

Qué demuestra: el código cliente pide una tarifa a un CREADOR abstracto
(FabricaTarifa) sin saber qué clase concreta se instancia; cada subclase del
creador decide qué Tarifa fabricar en su factory method crearTarifa().
"""
from _comun import seccion, titulo
from factories.fabrica_tarifa import (
    FabricaTarifa,
    FabricaTarifaAdultoMayor,
    FabricaTarifaEstudiante,
    FabricaTarifaOrdinaria,
)

VALOR_BASE = 85000.0


def cobrar(creador: FabricaTarifa, valor_base: float) -> None:
    """Código CLIENTE: solo conoce FabricaTarifa y Tarifa, nunca las clases concretas."""
    tarifa = creador.crearTarifa(valor_base)          # <- factory method
    print(f"   {type(creador).__name__:<26} crea {type(tarifa).__name__:<18}"
          f"{tarifa.descripcion():<40} ${tarifa.calcular():>9,.0f}")


titulo("DEMO FACTORY METHOD — creación de tarifas de tiquete")

seccion(f"1. El mismo código cliente con tres creadores (valor base ${VALOR_BASE:,.0f})")
for creador in (FabricaTarifaOrdinaria(), FabricaTarifaEstudiante(), FabricaTarifaAdultoMayor()):
    cobrar(creador, VALOR_BASE)

seccion("2. Lógica común del creador: liquidar() usa el producto sin saber cuál es")
for creador in (FabricaTarifaOrdinaria(), FabricaTarifaEstudiante(), FabricaTarifaAdultoMayor()):
    print(f"   {type(creador).__name__:<26} liquidar({VALOR_BASE:,.0f}) = ${creador.liquidar(VALOR_BASE):,.0f}")

seccion("3. Regla de validación en el producto: el valor base debe ser positivo")
try:
    FabricaTarifaEstudiante().crearTarifa(0)
except ValueError as e:
    print(f"   RECHAZADO -> {e}")

seccion("4. Colaboración: esta Tarifa es la que recibirá el Builder (ver demo_builder.py)")
tarifa = FabricaTarifaEstudiante().crearTarifa(VALOR_BASE)
print(f"   Tarifa lista para inyectar al Builder: {type(tarifa).__name__} -> ${tarifa.calcular():,.0f}")
