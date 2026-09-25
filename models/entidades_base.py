from models.database import db

class ClienteModel(db.Model):
    __tablename__ = 'cliente'

    id_cliente = db.Column(db.String(20), primary_key=True) # CC/NIT
    tipo_documento = db.Column(db.String(10), nullable=False)
    nombre_completo = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    es_corporativo = db.Column(db.Boolean, default=False)

    # Relaciones
    tiquetes = db.relationship('TiqueteModel', backref='cliente', lazy=True)
    envios_remitidos = db.relationship('EnvioModel', foreign_keys='EnvioModel.id_remitente', backref='remitente', lazy=True)

    def __repr__(self):
        return f"<Cliente {self.id_cliente}: {self.nombre_completo}>"


class EmpleadoModel(db.Model):
    __tablename__ = 'empleado'

    id_empleado = db.Column(db.String(20), primary_key=True)
    nombre_completo = db.Column(db.String(150), nullable=False)
    cargo = db.Column(db.String(50), nullable=False) # Cajero, Despachador, Conductor
    login = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Empleado {self.id_empleado}: {self.nombre_completo} ({self.cargo})>"


class BusModel(db.Model):
    __tablename__ = 'bus'

    id_bus = db.Column(db.String(10), primary_key=True) # Placa o ID interno
    placa = db.Column(db.String(10), unique=True, nullable=False)
    tipo_bus = db.Column(db.String(20), nullable=False) # Clásico, Preferencial Plus
    capacidad_sillas = db.Column(db.Integer, nullable=False)
    capacidad_carga = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Bus {self.placa} ({self.tipo_bus})>"