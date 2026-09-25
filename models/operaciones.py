from models.database import db

class ViajeModel(db.Model):
    __tablename__ = 'viaje'

    id_viaje = db.Column(db.Integer, primary_key=True, autoincrement=True)
    origen = db.Column(db.String(80), nullable=False)
    destino = db.Column(db.String(80), nullable=False)
    fecha_salida = db.Column(db.DateTime, nullable=False)
    id_bus = db.Column(db.String(10), db.ForeignKey('bus.id_bus'), nullable=False)
    estado = db.Column(db.String(20), default='Programado')

    # Relación
    bus = db.relationship('BusModel', backref='viajes')

    def __repr__(self):
        return f"<Viaje #{self.id_viaje}: {self.origen} -> {self.destino} [{self.fecha_salida.strftime('%Y-%m-%d %H:%M')}]>"