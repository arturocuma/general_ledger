# coding: utf8

"""
Colección de funciones/hacks
"""

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

    asientos = db(db.asiento.poliza_id == poliza_id).select(
            db.asiento.debe, db.asiento.haber
            )

    if asientos:
        deb = reduce(lambda x,y: x+y, [asi.debe for asi in asientos])
        hab = reduce(lambda x,y: x+y, [asi.haber for asi in asientos])
        if deb == hab:
            flag = DIV(deb, _class='verde')
        else:
            flag = DIV('{} != {}'.format(deb, hab), _class='rojo')

    else:
        flag = DIV('Póliza sin asientos', _class='rojo')

    return flag


def obtener_tipo_poliza(tipo_poliza_id):
    """
    Retorna el tipo de poliza a partir de un id
    """
    resultado = db(db.tipo_poliza.id == tipo_poliza_id).select(
            db.tipo_poliza.nombre
            ).first()

    return resultado.nombre


def eliminar(ids):
    """
    Recibe una lista de ids y los elimina
    """
    [db(db.poliza.id == id).delete() for id in ids]


def editar(ids):
    """
    Recibe una lista de ids, edita el primero que toma
    """
    print ids[0]
