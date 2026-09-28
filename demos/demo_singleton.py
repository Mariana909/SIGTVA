"""
DEMO — SINGLETON (Venta de tiquete: instancia única bajo concurrencia)

Ejecutar desde la raíz del proyecto:   python demos/demo_singleton.py

Qué demuestra: GestorBloqueoSillas, SecuenciadorTiquete y ValidadorTarifaEspecial
son UN ejemplar cada uno; con hilos de por medio, el bloqueo no se duplica, el
consecutivo no se repite y la caché evita reconsultas.
"""
import threading
import time

from _comun import seccion, titulo
from singletons.gestor_bloqueo import GestorBloqueoSillas
from singletons.secuenciadores import SecuenciadorTiquete
from singletons.validador_tarifa import ValidadorTarifaEspecial

titulo("DEMO SINGLETON — una sola instancia, ni con hilos")


def limpiar():
    GestorBloqueoSillas().limpiar()
    SecuenciadorTiquete().reiniciar(1)
    ValidadorTarifaEspecial().limpiar()


limpiar()
seccion("1. Misma instancia siempre (is, no ==)")
print(f"   GestorBloqueoSillas() is GestorBloqueoSillas(): "
      f"{GestorBloqueoSillas() is GestorBloqueoSillas()}")
print(f"   SecuenciadorTiquete() is SecuenciadorTiquete(): "
      f"{SecuenciadorTiquete() is SecuenciadorTiquete()}")

seccion("2. Bloqueo transaccional: la silla se reserva una sola vez")
gestor = GestorBloqueoSillas()
print(f"   Taquilla 1 bloquea silla 7: {gestor.bloquear(101, 7, 'Taquilla')}")
print(f"   Web intenta silla 7:        {gestor.bloquear(101, 7, 'Web')}")
print(f"   Sillas bloqueadas ahora: {gestor.bloqueadas()}")

seccion("3. Expiración: el bloqueo muere solo (ttl 0.2 s en la demo)")
gestor.limpiar()
print(f"   Bloqueo corto: {gestor.bloquear(102, 3, 'Web', duracion=0.2)}")
time.sleep(0.3)
print(f"   Tras expirar, la silla vuelve: {gestor.bloquear(102, 3, 'Web')}")
gestor.limpiar()

seccion("4. 50 hilos, 50 números distintos (consecutivo nacional)")
sec = SecuenciadorTiquete()
sec.reiniciar(1)
numeros = []
cerrojo = threading.Lock()


def pedir():
    n = sec.siguiente()
    with cerrojo:
        numeros.append(n)


hilos = [threading.Thread(target=pedir) for _ in range(50)]
[t.start() for t in hilos]
[t.join() for t in hilos]
print(f"   Generados: {len(numeros)}, únicos: {len(set(numeros))}, "
      f"primero: {min(numeros)}, último: {max(numeros)}")
sec.reiniciar(1)

seccion("5. 20 taquillas pelean 1 silla: gana exactamente una")
gestor.limpiar()
ganadas = []
cerrojo2 = threading.Lock()


def vender(canal):
    if gestor.bloquear(103, 9, canal):
        with cerrojo2:
            ganadas.append(canal)


hilos = [threading.Thread(target=vender, args=(f"Caja-{i}",)) for i in range(20)]
[t.start() for t in hilos]
[t.join() for t in hilos]
print(f"   Ganó 1 de 20: {ganadas}")
gestor.limpiar()

seccion("6. Caché de soportes: la segunda validación no reconsulta")
val = ValidadorTarifaEspecial()
print(f"   Estudiante con CARNE-2026: {val.validar('estudiante', 'CARNE-2026')}")
print(f"   Otra vez (caché):          {val.validar('estudiante', 'CARNE-2026')}")
print(f"   Adulto 59 años:            {val.validar('adulto_mayor', 'EDAD:59')}")
val.limpiar()
