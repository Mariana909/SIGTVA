"""
Datos mínimos para poder probar la aplicación (empleado, buses y viajes).
Es idempotente: si ya hay viajes, no hace nada.
"""
import datetime

from dao.entidades_base_dao import BusDAO, EmpleadoDAO
from dao.operaciones_dao import ViajeDAO
from models.operaciones import ViajeModel
from werkzeug.security import generate_password_hash

RUTAS = [
    ("Bogotá", "Medellín"), ("Bogotá", "Cali"), ("Bogotá", "Barranquilla"),
    ("Bogotá", "Bucaramanga"), ("Medellín", "Bogotá"), ("Medellín", "Cali"),
    ("Cali", "Bogotá"), ("Cali", "Medellín"), ("Barranquilla", "Bogotá"),
    ("Bucaramanga", "Bogotá"),
]
HORAS = (6, 14, 22)


def cargar_datos_demo() -> None:
    if ViajeModel.query.count() > 0:
        return
    EmpleadoDAO.registrarEmpleado("1", "Cajero Demo", "Cajero", "cajero", generate_password_hash("demo123"))
    buses = [
        BusDAO.registrarBus("BUS-01", "ABC123", "Clásico", 30, 500.0),
        BusDAO.registrarBus("BUS-02", "DEF456", "Preferencial Plus", 30, 500.0),
        BusDAO.registrarBus("BUS-03", "GHI789", "Clásico", 30, 500.0),
    ]
    manana = datetime.datetime.now() + datetime.timedelta(days=1)
    for i, (origen, destino) in enumerate(RUTAS):
        # La primera ruta sale 3 veces; las demás una sola vez.
        horas = HORAS if i == 0 else (HORAS[i % 3],)
        for j, hora in enumerate(horas):
            # El minuto distinto por ruta evita el choque con la validación de duplicados del DAO.
            salida = manana.replace(hour=hora, minute=i * 5, second=0, microsecond=0)
            ViajeDAO.registrarViaje(origen, destino, salida, buses[(i + j) % len(buses)].id_bus)
