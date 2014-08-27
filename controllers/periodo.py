# coding: utf8
(auth.user or request.args(0) == 'login') or\
        redirect(URL('default', 'login'))

from datetime import datetime, date
import calendar
from json import dumps

empresa_id = session.instancias
db = empresas.dbs[int(empresa_id)]


def index(): 
    """
    Aquí se mostrará una lista de periodos
    Habrá un botón para crear, un filtro y así
    """

    campos = [
        Field('anio', 'integer', label='Año'),
        Field('mes', requires = IS_IN_DB(db, 'mes.nombre'), label='Mes'),
    ]

    form = SQLFORM.factory(*campos)

    #if request.vars:
    if form.process().accepted:

        form.vars.anio_id = obtener_id_anio(form.vars.anio)
        form.vars.mes_id = obtener_id_mes(form.vars.mes)

        cadena = '{}{}'.format(form.vars.anio, form.vars.mes)
        form.vars.clave = cadena
        fecha = datetime.strptime(cadena, "%Y%B").date()

        # crear un form.vars.clave
        form.vars.inicio = date(fecha.year, fecha.month, 1)
        ultimo_dia = calendar.monthrange(fecha.year, fecha.month)[1]
        form.vars.fin = date(fecha.year, fecha.month, ultimo_dia)

        periodo_id = db.periodo.insert(
                **db.periodo._filter_fields(form.vars)
                )

    elif form.errors:
        print form.errors
    else:
        pass

    query = (db.periodo.anio_id == db.anio.id) &\
            (db.periodo.mes_id == db.mes.id)

    periodos = db(query).select(
            db.periodo.id.with_alias('id'),
            db.anio.numero.with_alias('numero'),
            db.mes.nombre.with_alias('nombre'),
            db.periodo.estatus_periodo_id.with_alias('estatus')
            )

    return dict(form=form, periodos =periodos)

def cerrar_periodo():
    """
    Cierra un periodo contable
    """
    id = request.vars.periodo_id
    db(db.periodo.id == id).update(estatus_periodo_id = 2) 


def abrir_periodo():
    """
    Abre un periodo contable
    """
    id = request.vars.periodo_id
    db(db.periodo.id == id).update(estatus_periodo_id = 1) 


def iniciar():
    """
    Inicia un periodo contable, 
    #ToDo:
    - Recibe como parámetro año y mes de un periodo
    """

    hoy = date.today()
    anio_id = obtener_id_anio(hoy.strftime('%Y'))
    mes_id = obtener_id_mes(hoy.strftime('%B').upper())

    inicio = date(hoy.year, hoy.month, 1)
    ultimo_dia = calendar.monthrange(hoy.year, hoy.month)[1]
    fin = date(hoy.year, hoy.month, ultimo_dia)

    db.periodo.insert(
            inicio = inicio,
            fin = fin,
            anio_id = anio_id,
            mes_id = mes_id,
            estatus_periodo_id = 1,
            consecutivo = 0
            )

def crear():
    """
    Similar a `iniciar`,
    Crea un formulario para insertar un periodo
    """

    return dict(form=form)



def listar():
    """
    Crear archivo JSON de los periodos contables
    """

    query = (db.periodo.anio_id == db.anio.id) &\
            (db.periodo.mes_id == db.mes.id)

    periodos = db(query).select(
            db.periodo.id.with_alias('id'),
            db.anio.numero.with_alias('numero'),
            db.mes.nombre.with_alias('nombre'),
            db.periodo.estatus_periodo_id.with_alias('estatus')
            )

    diccionario = periodos.as_dict()

    return dumps(diccionario, sort_keys=True)
