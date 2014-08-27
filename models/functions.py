# coding: utf8

"""
Colección de funciones/hacks
"""

def armar_folio(consecutivo, tipo, fecha):

    folio = ''

    # tipo de póliza
    if tipo == 1:
        folio += 'IN' 
    elif tipo == 2:
        folio += 'EG' 
    elif tipo == 3:
        folio += 'DI' 
    else:
        folio += 'XX'
    
    # números consecutivos
    folio += str(consecutivo).zfill(6)

    # mes y año
    folio += fecha.strftime('%b').upper()
    folio += fecha.strftime('%y')

    return folio


def comparar_flotantes(a, b):
    """
    compara flotantes que en apariencia son iguales D:
    """
    if abs(a-b) < 0.0000000001:
        return True
    else:
        return False
    

def cambia_breadcrumb(items):
    """
    Hack para hacer funcionar el código, este código es muy extraño
    """

    if request.vars.id:
        id = request.vars.id
    else:
        poliza_id = request.args(-1)
        id = db(db.poliza.id == poliza_id).select(
                db.poliza.periodo_id
                ).first().periodo_id

    items[0] = A(
            'Póliza',
            _href=URL('listar', vars={'id': id})
            )
    return items


def agrega_cuadrar(items):
    """
    agrega un TR al final
    """
    row = TR(_class='fila-final')
    for x in xrange(8):
        row.append(TD(''))

    items.append(row)

    return items


def calcula_importe(poliza_id):
    """
    calcula el importe de la póliza, esto es, la suma de los asientos
    """

    db = empresas.dbs[int(session.instancias)]
    asientos = db(db.asiento.poliza_id == poliza_id).select(
            db.asiento.debe, db.asiento.haber
            )

    if asientos:
        deb = reduce(lambda x,y: (x or 0) + (y or 0), [asi.debe for asi in asientos])
        hab = reduce(lambda x,y: (x or 0) + (y or 0), [asi.haber for asi in asientos])

        if comparar_flotantes(deb, hab):
            flag = DIV(
                    '{}'.format(locale.currency(deb, grouping=True)), 
                    _class='verde derecha',
                    )
        else:
            flag = DIV(
                    '{} <> {}'.format(locale.currency(deb, grouping=True),
                    locale.currency(hab, grouping=True)),
                    _class='rojo derecha'
                    )

    else:
        flag = DIV('Póliza sin asientos', _class='rojo derecha')

    return flag


def obtener_tipo_poliza(tipo_poliza_id):
    """
    Retorna el tipo de póliza a partir de un id
    """
    resultado = db(db.tipo_poliza.id == tipo_poliza_id).select(
            db.tipo_poliza.nombre
            ).first()

    return resultado.nombre


def selector_fecha(id):

    fecha_poliza = db(db.poliza.id == id).select(
            db.poliza.fecha_usuario
            ).first().fecha_usuario

    fecha = INPUT(
            _name = 'fecha',
            _class='fecha_poliza',
            _id='{}-fecha_usuario'.format(id),
            value = fecha_poliza
            )

    return fecha


def crear_selector_status(id):
    """
    Retorna el estatus de la póliza a partir de un id
    """
    opciones_estatus = [OPTION(estatus.nombre, _value=estatus.id) for\
            estatus in db().select(
                db.estatus_poliza.ALL,
                cache=(cache.ram, 3600)
                )]

    estatus = db(db.poliza.id == id).select(
            db.poliza.estatus
            ).first().estatus

    select = SELECT(
            _name = 'estatus{}'.format(id),
            _id = '{}.estatus'.format(id),
            _class = 'cambiar_estatus',
            value = estatus,
            *opciones_estatus
            )

    return select


def crear_selector_tipo(id):
    """
    Retorna el estatus de la póliza a partir de un id
    """
    opciones_tipos = [OPTION(tipos.nombre, _value=tipos.id) for\
            tipos in db().select(
                db.tipo_poliza.ALL,
                cache=(cache.ram,3600)
                )]

    tipo = db(db.poliza.id == id).select(
            db.poliza.tipo
            ).first().tipo

    select = SELECT(
            _name = 'tipo{}'.format(id),
            _id = '{}.tipo'.format(id),
            _class = 'cambiar_tipo',
            value = tipo,
            *opciones_tipos
            )

    return select


def eliminar(ids):
    """
    Recibe una lista de ids y los elimina
    """

    [db_maestro(db_maestro[id.split('.')[1]].id == id.split('.')[0]).delete() for id in ids]


def obtener_id_anio(anio):
    registro = db(db.anio.numero == anio).select(db.anio.id).first()
    if registro:
        return registro.id
    else:
        return db.anio.insert(numero = anio)


def obtener_id_mes(mes):
    registro = db(db.mes.nombre == mes).select(db.mes.id).first()
    return registro.id
