
def agrega_cuadrar(items):
    """
    agrega un TR al final
    """

    row = TR(_class='fila-final')
    for x in xrange(8):
        row.append(TD(''))

    items.append(row)

    return items
