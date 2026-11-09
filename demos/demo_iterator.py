"""
DEMO — ITERATOR (Despacho de remesa: recorrido de guías)

Ejecutar desde la raíz del proyecto:   python demos/demo_iterator.py
"""
from _comun import seccion, titulo

from prototypes.prototipos_envio import Guia, Remesa
from services.servicio_despacho import AuxiliarDespacho

titulo("DEMO ITERATOR — recorrido de guías sin exponer la lista")

remesa = Remesa("REM-001", "CC-123")
for numero, remitente, servicio in [("G-001", "CC-123", "estandar"),
                                    ("G-002", "CC-123", "estandar"),
                                    ("G-003", "CC-123", "prioritario")]:
    remesa.guias.append(Guia(numero, remitente, servicio))

seccion("1. Recorrer la remesa con haySiguiente() y siguiente()")
despachadas = AuxiliarDespacho().despachar(remesa)
print(f"   Despachadas en orden: {despachadas}")

seccion("2. La lista sigue intacta: iterar no borra ni reordena")
print(f"   Guías en remesa: {[g.numero for g in remesa.guias]}")

seccion("3. Agotado el recorrido, siguiente() lanza StopIteration")
it = remesa.crearIterador()
while it.haySiguiente():
    it.siguiente()
try:
    it.siguiente()
except StopIteration:
    print("   StopIteration al pedir de más (correcto)")
