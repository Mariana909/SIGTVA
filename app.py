import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps

# 1. SQLAlchemy / Configuración
from models.database import db

# 2. DAOs
from dao.entidades_base_dao import ClienteDAO, EmpleadoDAO, BusDAO
from dao.operaciones_dao import ViajeDAO
from dao.transacciones_dao import TiqueteDAO, EnvioDAO, FacturaDAO

# 3. Modelos SQLAlchemy
from models.operaciones import ViajeModel

# 4. PATRONES DE DISEÑO: FÁBRICAS Y BUILDERS
from factories.fabrica_venta import FabricaWeb, FabricaTaquilla, FabricaAliada
from factories.fabrica_envio import FabricaPaqueteo, FabricaCorporativa, FabricaRemesa
from builders.constructor_tiquete import (
    ConstructorTiqueteImpl, 
    Taquillero, 
    Viaje as ViajeDTO, 
    Silla as SillaDTO, 
    Pasajero as PasajeroDTO, 
    Pago as PagoDTO
)
from builders.constructor_envio import (
    ConstructorEnvioImpl, 
    AuxiliarEncomiendas
)

app = Flask(__name__)
app.secret_key = 'clave_secreta_transporte_nacional'

# ==========================================
# CONFIGURACIÓN E INICIALIZACIÓN DE LA BD
# ==========================================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sigtva.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# ==========================================
# HELPER / DECORADOR PARA CONTROL DE ROLES
# ==========================================
def requiere_rol(*roles_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            rol_actual = session.get('rol', 'invitado')
            if rol_actual not in roles_permitidos:
                flash(f"Acceso denegado. Se requiere rol: {', '.join(roles_permitidos)}", "error")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ==========================================
# RUTAS PRINCIPALES
# ==========================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/pasajeros', methods=['GET', 'POST'])
def pasajeros():
    origen = request.form.get('origen') if request.method == 'POST' else None
    destino = request.form.get('destino') if request.method == 'POST' else None
    fecha_raw = request.form.get('fecha', '') if request.method == 'POST' else ''

    query = ViajeModel.query
    if origen:
        query = query.filter_by(origen=origen)
    if destino:
        query = query.filter_by(destino=destino)
    
    viajes = query.all()

    return render_template(
        'pasajeros.html', 
        viajes=viajes, 
        origen=origen, 
        destino=destino, 
        fecha_raw=fecha_raw,
        fecha_formateada=fecha_raw
    )


@app.route('/comprar/<int:viaje_id>', methods=['POST'])
def comprar_tiquete(viaje_id):
    documento = request.form.get('documento')
    nombre_completo = request.form.get('nombre_completo')
    numero_silla = int(request.form.get('numero_silla', 1))
    precio = float(request.form.get('precio', 85000))
    canal_venta = request.form.get('canal_venta', 'web').lower()
    id_usuario_actual = session.get('user_id', 1)

    try:
        # 1. Selección de la fábrica
        if canal_venta == 'taquilla':
            fabrica_venta = FabricaTaquilla()
            canal_nombre = "Taquilla"
        elif canal_venta == 'aliada':
            fabrica_venta = FabricaAliada()
            canal_nombre = "Agencia Aliada"
        else:
            fabrica_venta = FabricaWeb()
            canal_nombre = "Web"
        
        builder_tiquete = ConstructorTiqueteImpl(fabrica_venta)
        taquillero = Taquillero(builder_tiquete)

        viaje_db = ViajeModel.query.get(viaje_id)
        origen_str = viaje_db.origen if viaje_db else "Origen Genérico"
        destino_str = viaje_db.destino if viaje_db else "Destino Genérico"

        # Construcción vía Builder
        tiquete_dto = taquillero.venderTiquete(
            viaje=ViajeDTO(origen=origen_str, destino=destino_str),
            silla=SillaDTO(numero=numero_silla, estado="Bloqueada"),
            pasajero=PasajeroDTO(documento=documento, nombre=nombre_completo),
            pago=PagoDTO(metodo=f"Pago/{canal_nombre}", valor=precio),
            tarifa=precio
        )

        # 2. Persistencia Cliente y Tiquete
        cliente = ClienteDAO.registrarCliente(
            id_cliente=tiquete_dto.pasajero.documento,
            tipo_documento="CC",
            nombre_completo=tiquete_dto.pasajero.nombre,
            telefono="",
            email=""
        )

        exito_tq, msg_tq, tiquete_db = TiqueteDAO.registrarTiquete(
            id_viaje=viaje_id,
            id_cliente=cliente.id_cliente,
            id_usuario_registra=id_usuario_actual,
            numero_silla=tiquete_dto.silla.numero,
            precio_total=tiquete_dto.valorFinal,
            canal_venta=canal_nombre
        )

        if not exito_tq:
            flash(msg_tq, "error")
            return redirect(url_for('pasajeros'))

        # 3. Emisión de Factura
        cufe_info = "POS-LOCAL"
        monto_factura = tiquete_dto.valorFinal

        if hasattr(tiquete_dto, 'factura'):
            if isinstance(tiquete_dto.factura, dict):
                cufe_info = tiquete_dto.factura.get('cufe', 'POS-LOCAL')
                monto_factura = tiquete_dto.factura.get('total', monto_factura)
            elif hasattr(tiquete_dto.factura, 'cufe'):
                cufe_info = tiquete_dto.factura.cufe
                monto_factura = getattr(tiquete_dto.factura, 'total', monto_factura)

        # AJUSTE AQUÍ: Desempaquetar la tupla retornada por el DAO
        res_factura = FacturaDAO.registrarFactura(
            monto_total=monto_factura,
            id_cajero=id_usuario_actual,
            id_tiquete=tiquete_db.id_tiquete
        )

        # Si el DAO retorna una tupla (ej. exito, msg, factura) extraemos el objeto
        if isinstance(res_factura, tuple):
            factura_db = res_factura[-1] # Toma el último elemento que es el objeto Factura
        else:
            factura_db = res_factura

        # 4. MOSTRAR FACTURA EN PANTALLA
        return render_template(
            'factura.html',
            factura=factura_db,
            tiquete=tiquete_db,
            tiquete_dto=tiquete_dto,
            cufe=cufe_info,
            tipo_comprobante="Tiquete de Viaje"
        )
    
    except Exception as e:
        flash(f"Error en el proceso de compra: {str(e)}", "error")
        return redirect(url_for('pasajeros'))


@app.route('/envios', methods=['GET', 'POST'])
def gestionar_envios():
    if request.method == 'POST':
        doc_rem = request.form.get('doc_remitente')
        nom_rem = request.form.get('nom_remitente')
        doc_des = request.form.get('doc_destinatario')
        nom_des = request.form.get('nom_destinatario')
        peso_kg = float(request.form.get('peso_kg', 1.0))
        dims = request.form.get('dimensiones', '30x30x30')
        tipo_servicio = request.form.get('tipo_servicio', 'paqueteo').lower()
        id_usuario_actual = session.get('user_id', 1)

        try:
            # 1. Fábrica y Validación
            if tipo_servicio == 'corporativa':
                fabrica_envio = FabricaCorporativa()
            elif tipo_servicio == 'remesa':
                fabrica_envio = FabricaRemesa()
            else:
                fabrica_envio = FabricaPaqueteo()

            validador_peso = fabrica_envio.crearPeso()
            if not validador_peso.validar(peso=peso_kg, dims=dims):
                max_kg = getattr(validador_peso, 'maxKg', getattr(validador_peso, 'limite_peso', 'permitido'))
                flash(f"El peso ({peso_kg} kg) supera el límite máximo para {tipo_servicio.capitalize()} ({max_kg} kg).", "error")
                return redirect(url_for('gestionar_envios'))

            # 2. Flete y Envio DTO
            flete_calculador = fabrica_envio.crearFlete()
            monto_flete_calculado = flete_calculador.calcular(ruta="Ruta Base", peso=peso_kg)

            builder_envio = ConstructorEnvioImpl(fabrica_envio)
            auxiliar = AuxiliarEncomiendas(builder_envio)

            envio_dto = auxiliar.registrarEnvio(
                peso=peso_kg,
                dims=dims,
                origen="Terminal Norte",
                destino="Terminal Sur",
                cliente_doc=doc_rem,
                bodega_ub="Bodega Central"
            )

            guia_generada = None
            if hasattr(envio_dto, 'guia'):
                if isinstance(envio_dto.guia, dict):
                    guia_generada = envio_dto.guia.get('codigoBarras') or envio_dto.guia.get('numero')
                else:
                    guia_generada = getattr(envio_dto.guia, 'codigoBarras', getattr(envio_dto.guia, 'numero', None))

            # 3. Persistencia
            remitente = ClienteDAO.registrarCliente(doc_rem, "CC", nom_rem, "", "")
            destinatario = ClienteDAO.registrarCliente(doc_des, "CC", nom_des, "", "")

            exito_env, msg_env, envio_db = EnvioDAO.registrarEnvio(
                id_remitente=remitente.id_cliente,
                id_destinatario=destinatario.id_cliente,
                id_usuario_registra=id_usuario_actual,
                peso_kg=getattr(envio_dto, 'pesoFacturable', peso_kg),
                monto_flete=monto_flete_calculado,
                modalidad=tipo_servicio.capitalize(),
                numero_guia_custom=guia_generada
            )

            if exito_env:
                # AJUSTE AQUÍ: Manejar si el DAO retorna tupla
                res_factura = FacturaDAO.registrarFactura(
                    monto_total=monto_flete_calculado,
                    id_cajero=id_usuario_actual,
                    id_envio=envio_db.id_envio
                )

                if isinstance(res_factura, tuple):
                    factura_db = res_factura[-1]
                else:
                    factura_db = res_factura

                # MOSTRAR FACTURA EN PANTALLA
                return render_template(
                    'factura.html',
                    factura=factura_db,
                    envio=envio_db,
                    envio_dto=envio_dto,
                    remitente=remitente,
                    destinatario=destinatario,
                    tipo_comprobante="Comprobante de Encomienda"
                )
            else:
                flash(msg_env, "error")

        except Exception as e:
            flash(f"Error al registrar el envío: {str(e)}", "error")

        return redirect(url_for('gestionar_envios'))

    return render_template('envios.html')


@app.route('/rastrear', methods=['GET'])
def rastrear_envio():
    numero_guia = request.args.get('numero_guia')
    envio = None
    if numero_guia:
        envio = EnvioDAO.consultarEnvio(numero_guia)
        if not envio:
            flash(f"No se encontró la guía: {numero_guia}", "error")
    
    return render_template('rastrear.html', envio=envio, numero_guia=numero_guia)


@app.route('/crear-viaje', methods=['GET', 'POST'])
@requiere_rol('admin', 'operador')
def crear_viaje():
    if request.method == 'POST':
        origen = request.form.get('origen')
        destino = request.form.get('destino')
        id_bus = int(request.form.get('id_bus', 1))

        ViajeDAO.registrarViaje(
            origen=origen,
            destino=destino,
            fecha_salida=datetime.datetime.now(),
            id_bus=id_bus
        )
        
        flash("Viaje programado correctamente.", "success")
        return redirect(url_for('pasajeros'))

    return render_template('crear_viaje.html')


# ==========================================
# SIMULACIÓN DE ROLES Y SESIÓN PARA PRUEBAS
# ==========================================

@app.route('/cambiar-rol/<nuevo_rol>')
def cambiar_rol(nuevo_rol):
    session['rol'] = nuevo_rol
    session['user_id'] = 1
    flash(f"Rol actualizado a: {nuevo_rol}", "success")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)