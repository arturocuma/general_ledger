
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
