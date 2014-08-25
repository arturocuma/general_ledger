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

    query = (db.periodo.anio == db.anio.id) &\
            (db.periodo.anio == db.mes.id)

    periodos = db(query).select(
            db.periodo.ALL
            )

    periodos = SQLFORM.grid(db.periodo)

    return dict(periodos=periodos)


def listar():
    """
    Crear archivo JSON de los periodos contables
    """

    query = (db.periodo.anio == db.anio.id) &\
            (db.periodo.anio == db.mes.id)

    periodos = db(query).select(
            db.periodo.id.with_alias('id'),
            db.anio.numero.with_alias('numero'),
            db.mes.nombre.with_alias('nombre'),
            db.periodo.estatus.with_alias('estatus')
            )

    diccionario = periodos.as_dict()

    return dumps(diccionario, sort_keys=True)


def cerrar():
    """
    Cierra un periodo contable
    """
    id = request.vars.cerrar
    db(db.periodo.id == id).update(estatus = False) 


def abrir():
    """
    Abre un periodo contable
    """
    id = request.vars.abrir
    db(db.periodo.id == id).update(estatus = True) 


def iniciar():
    """
    Inicia un periodo contable, 
    #ToDo:
    - Recibe como parámetro año y mes de un periodo
    """

    hoy = date.today()

    anio = obtener_id_anio(hoy.strftime('%Y'))
    mes = obtener_id_mes(hoy.strftime('%B').upper())

    inicio = date(hoy.year, hoy.month, 1)
    ultimo_dia = calendar.monthrange(hoy.year, hoy.month)[1]
    fin = date(hoy.year, hoy.month, ultimo_dia)

    db.periodo.insert(
            inicio = inicio,
            fin = fin,
            anio = anio,
            mes = mes,
            estatus = True,
            consecutivo = 0
            )
