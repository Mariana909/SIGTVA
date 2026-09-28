"""
DEMO — PROTOTYPE (Registro de envío: radicación de remesa por clonación)

Ejecutar desde la raíz del proyecto:   python demos/demo_prototype.py

Qué demuestra: el CONTROL (ServicioPrototipos) nunca construye guías a mano;
pide copias al RegistroPrototipos. Guia se clona superficial (solo valores);
Tula y Remesa se clonan profundo (cada clon trae su propia lista).
"""
from _comun import seccion, titulo
from prototypes.prototipos_envio import RegistroPrototipos
from services.servicio_prototipos import ServicioPrototipos

servicio = ServicioPrototipos()

titulo("DEMO PROTOTYPE — remesa múltiple por clonación")

seccion("1. Radicar remesa: 1 remitente, 3 destinos, 0 digitaciones repetidas")
lote = servicio.radicar_remesa("CC-123", ["Bogotá", "Medellín", "Cali"])
remesa = lote["remesa"]
print(f"   Remesa {remesa.numero} de {remesa.cliente} con {len(remesa.guias)} guías:")
for guia, tula in zip(remesa.guias, lote["tulas"], strict=True):
    print(f"   guía {guia.numero} -> {tula.destino} (precinto {tula.precinto})")

seccion("2. La plantilla no se contamina: ajustar un clon no toca el original")
guia = remesa.guias[0]
guia.numero = "MANUAL"
base = [g.numero for g in remesa.guias[1:]]
print(f"   Clon modificado: {guia.numero} | hermanas intactas: {base}")
print(f"   Plantillas registradas: {RegistroPrototipos().claves()}")

seccion("3. Copia profunda: la tula clonada trae SU lista (no la de la plantilla)")
tula = lote["tulas"][0]
print(f"   Tula {tula.precinto} con {len(tula.guias)} guía(s) propia(s)")

seccion("4. El registro también es Singleton: todos piden al mismo")
print(f"   RegistroPrototipos() is RegistroPrototipos(): "
      f"{RegistroPrototipos() is RegistroPrototipos()}")
