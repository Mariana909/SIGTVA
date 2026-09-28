from models.database import db
from models.entidades_base import ClienteModel, EmpleadoModel, BusModel

class ClienteDAO:
    @staticmethod
    def registrarCliente(id_cliente, tipo_documento, nombre_completo, telefono, email, es_corporativo=False):
        """
        Registra un cliente evitando duplicados. Si ya existe, actualiza los datos.
        Corresponde a registrarCliente() / consultarCliente() del UML.
        """
        cliente = ClienteModel.query.get(id_cliente)
        if not cliente:
            cliente = ClienteModel(
                id_cliente=id_cliente,
                tipo_documento=tipo_documento,
                nombre_completo=nombre_completo,
                telefono=telefono,
                email=email,
                es_corporativo=es_corporativo
            )
            db.session.add(cliente)
            db.session.commit()
        return cliente

    @staticmethod
    def consultarCliente(id_cliente):
        return ClienteModel.query.get(id_cliente)

    @staticmethod
    def modificarCliente(id_cliente, **kwargs):
        cliente = ClienteModel.query.get(id_cliente)
        if cliente:
            for clave, valor in kwargs.items():
                if hasattr(cliente, clave):
                    setattr(cliente, clave, valor)
            db.session.commit()
        return cliente


class EmpleadoDAO:
    @staticmethod
    def registrarEmpleado(id_empleado, nombre_completo, cargo, login, password_hash):
        # Validación de duplicados por id_empleado o login
        existente = EmpleadoModel.query.filter(
            (EmpleadoModel.id_empleado == id_empleado) | (EmpleadoModel.login == login)
        ).first()
        
        if existente:
            return existente

        empleado = EmpleadoModel(
            id_empleado=id_empleado,
            nombre_completo=nombre_completo,
            cargo=cargo,
            login=login,
            password_hash=password_hash
        )
        db.session.add(empleado)
        db.session.commit()
        return empleado

    @staticmethod
    def consultarEmpleado(id_empleado):
        return EmpleadoModel.query.get(id_empleado)

    @staticmethod
    def autenticar(login):
        return EmpleadoModel.query.filter_by(login=login).first()


class BusDAO:
    @staticmethod
    def registrarBus(id_bus, placa, tipo_bus, capacidad_sillas, capacidad_carga):
        bus = BusModel.query.filter((BusModel.id_bus == id_bus) | (BusModel.placa == placa)).first()
        if not bus:
            bus = BusModel(
                id_bus=id_bus,
                placa=placa,
                tipo_bus=tipo_bus,
                capacidad_sillas=capacidad_sillas,
                capacidad_carga=capacidad_carga
            )
            db.session.add(bus)
            db.session.commit()
        return bus

    @staticmethod
    def consultarBus(id_bus):
        return BusModel.query.get(id_bus)

    @staticmethod
    def listarBuses():
        return BusModel.query.order_by(BusModel.id_bus).all()
