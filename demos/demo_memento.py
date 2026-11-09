"""
DEMO — MEMENTO (Corrección de encomienda registrada: guardar y revertir)

Ejecutar desde la raíz del proyecto:   python demos/demo_memento.py
"""
from _comun import seccion, titulo

from domain.envio import Envio
from mementos.recuerdos import HistorialEnvios
from services.servicio_memento import AuxiliarEncomiendas

titulo("DEMO MEMENTO — guardar antes de corregir, revertir si hace falta")

envio = Envio(pesoFacturable=10.5, valorDeclarado=50000.0,
              tipoServicio="estandar", estado="Registrado")
aux = AuxiliarEncomiendas(HistorialEnvios())

seccion("1. Corregir: se guarda la foto previa y se aplica el cambio")
aux.corregirEnvio(envio, {"pesoFacturable": 12.0, "estado": "EnBodegaOrigen"})
print(f"   Tras corregir: peso={envio.pesoFacturable} estado={envio.estado}")

seccion("2. Segunda corrección: queda su propia foto")
aux.corregirEnvio(envio, {"valorDeclarado": 75000.0})
print(f"   Tras corregir: valor={envio.valorDeclarado}")

seccion("3. Revertir dos veces: primero la última, luego la anterior (pop)")
aux.revertir(envio)
print(f"   Revierte 1: valor={envio.valorDeclarado} peso={envio.pesoFacturable} "
      f"estado={envio.estado}")
aux.revertir(envio)
print(f"   Revierte 2: valor={envio.valorDeclarado} peso={envio.pesoFacturable} "
      f"estado={envio.estado}")
print(f"   Sin más fotos: {aux.revertir(envio)} (no revienta)")
