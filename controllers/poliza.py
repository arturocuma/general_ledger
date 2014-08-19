# coding: utf8
(auth.user or request.args(0) == 'login') or redirect(URL('default', 'login'))

from datetime import datetime

empresa_id = session.instancias
db = empresas.dbs[int(empresa_id)]

# For referencing static and views from other application
def index(): return dict(message="hello from poliza.py")

def listar():

    # modificaciones a campos de la tabla `asiento`
    db.asiento.f_asiento.represent = lambda value, row: DIV(value if value!='' else '-', _class='f_asiento', _id=str(row.id)+'.f_asiento')
    db.asiento.cc_empresa_id.widget = SQLFORM.widgets.autocomplete(request, db.cc_empresa.descripcion, id_field=db.cc_empresa.id, limitby=(0,10), min_length=1)
    db.asiento.cc_empresa_id.represent = lambda value, row: DIV( db.cc_empresa(value).num_cc + ' ' + db.cc_empresa(value).descripcion if value else '-', _class='cc_empresa_id', _id=str(row.id)+'.cc_empresa_id')
    db.asiento.concepto_asiento.represent = lambda value, row: DIV(value if value!='' else '-', _class='concepto_asiento', _id=str(row.id)+'.concepto_asiento')
    db.asiento.debe.represent = lambda value, row: DIV(value if value!='' else '-', _class='debe', _id=str(row.id)+'.debe')
    db.asiento.haber.represent = lambda value, row: DIV(value if value!='' else '-', _class='haber', _id=str(row.id)+'.haber')

    # modificaciones a campos de la tabla `poliza`
    db.poliza.importe.writable = False
    db.poliza.concepto_general.represent = lambda value, row:\
            DIV(
                value if value != '' else '-',
                _class='concepto_general',
                _id=str(row.id)+'.concepto_general'
                )
    db.poliza.tipo.represent = lambda value, row:\
            DIV(
                obtener_tipo_poliza(value) if value != None else '-',
                _class='tipo_poliza',
                _id=str(row.id)+'.tipo_poliza'
                )

    #selectable = [
            #('Editar', lambda ids, table: [accion(ids, table)]),
            #('Editar', lambda ids: [accion(ids)]),
            #]

    polizas = SQLFORM.smartgrid(
            db.poliza,
            linked_tables=['asiento'],
            onvalidation=valida,
            #selectable=selectable,
            #deletable=auth.has_permission('delete_poliza') or False,
            deletable=True,
            searchable=False,
            editable=True,
            create=False,
            user_signature=True,
            exportclasses=dict(
                #csv=False,
                csv_with_hidden_cols=False,
                #html=False,
                json=False,
                tsv_with_hidden_cols=False,
                tsv=False,
                #xml=False
                )
            )

    if request.args(-3) == 'poliza' and request.args(-2) == 'asiento.poliza_id':

        boton_agregar_asiento = A(
                SPAN(_class="glyphicon glyphicon-indent-left"),
                'Agregar Asiento',
                _class="button btn btn-default",
                _href=URL(
                    "poliza",
                    "agregar_asiento",
                    args=["poliza", request.args(-1)]
                    )
                )
        polizas[2].insert(-1, boton_agregar_asiento)
        polizas.element('tbody', replace = lambda items: agrega_cuadrar(items))
    else:
        boton_agregar_poliza = A(
                SPAN(_class="glyphicon glyphicon-indent-left"),
                'Agregar Póliza',
                _class="button btn btn-default",
                _href=URL(
                    "poliza",
                    "agregar_poliza",
                    )
                )
        polizas[2].insert(-1, boton_agregar_poliza)

    return dict(polizas=polizas)


def agregar_asiento():
    """
    Agrega un elemento a la tabla `asiento`
    """

    db.asiento.insert(
            poliza_id = request.args[1],
            concepto_asiento = '',
            debe = 0,
            haber = 0
            )

    redirect(
            URL(
                'poliza/listar/poliza',
                'asiento.poliza_id',
                args=request.args[1]
                )
            )


def cuadrar_poliza():
    """
    Actualiza un debe/haber
    Compara la suma de los `deberes` y `haberes`
    """

    poliza_id = request.vars.id

    asientos = db(db.asiento.poliza_id == poliza_id).select(
            db.asiento.debe,
            db.asiento.haber
            )

    if asientos:
        deb = reduce(lambda x,y: (x if x else 0) + (y if y else 0), [asi.debe for asi in asientos])
        hab = reduce(lambda x,y: (x if x else 0) + (y if y else 0), [asi.haber for asi in asientos])

        row = TR(_class='fila-final')
        for x in xrange(4):
            row.append(TD(''))

        if comparar_flotantes(deb, hab):
            row.append(TD('Póliza Cuadrada', _class='verde'))
            row.append(TD(locale.currency(deb, grouping=True ), _class='verde'))
            row.append(TD(locale.currency(hab, grouping=True ), _class='verde'))
        else:
            row.append(TD('Póliza No Cuadrada', _class='rojo'))
            row.append(TD(locale.currency(deb, grouping=True ), _class='rojo'))
            row.append(TD(locale.currency(hab, grouping=True ), _class='rojo'))

        row.append(TD(''))

        return row


def valida(form):
    #print "In onvalidation callback"
    #print form.vars
    #form.errors= True  #this prevents the submission from completing

    #...or to add messages to specific elements on the form
    #form.errors.first_name = "Do not name your child after prominent deities"
    #form.errors.last_name = "Last names must start with a letter"
    response.flash = "I don't like your submission"


def actualiza_asiento():
    """
    Actualiza un campo de la tabla `asiento`
    """
    id, column = request.post_vars.id.split('.')
    value = request.post_vars.value
    db(db.asiento.id == id).update(**{column:value, 'f_asiento':datetime.now()})
    return value


def actualiza_descripcion():
    """
    Actualiza el campo `descripcion` de la tabla `asiento`.
    """
    id, column = request.post_vars.id.split('.')
    valor = request.post_vars.value

    num_cc = valor.split()[0]

    resultado = db(db.cc_empresa.num_cc == num_cc).select(
            db.cc_empresa.id,
            db.cc_empresa.num_cc,
            db.cc_empresa.descripcion
            ).first()

    db(db.asiento.id == id).update(**{
        column:resultado.id,
        'f_asiento':datetime.now()
        })

    return "%s %s" % (resultado.num_cc, resultado.descripcion)


def carga_cc():
    """
    Carga el catálogo de cuentas a un objeto JSON, función auxiliar
    """
    from json import loads, dumps

    query = ((db.cc_empresa.id > 0) & (db.cc_empresa.cc_vista_id==2))

    result = db(query).select(
            db.cc_empresa.id,
            db.cc_empresa.num_cc,
            db.cc_empresa.descripcion,
            )

    diccionario = dict()

    [diccionario.update({r.id: '{} {}'.format(r.num_cc, r.descripcion)})\
            for r in result]

    return dumps(diccionario)


def agregar_poliza():
    """
    Agrega un elemento a la tabla `póliza`
    """

    ultimo = db(db.poliza.id > 0).select(
            db.poliza.id,
            db.poliza.f_poliza,
            orderby =~ db.poliza.id
        ).first()

    # en caso de que no existan pólizas
    if ultimo:
        ultimo = int(ultimo.f_poliza.strftime('%m'))
    else:
        ultimo = int(datetime.now().strftime('%m'))
    # fin-en caso de que no existan pólizas

    id = db.poliza.insert(
            folio = '',
            concepto_general = '',
            tipo = '',
            importe = 0,
            )

    fila = db(db.poliza.id == id).select(
            db.poliza.tipo,
            db.poliza.f_poliza,
            ).first()
    ahora = int(fila.f_poliza.strftime('%m'))

    print 'último {} -- ahora {}'.format(ultimo, ahora)

    consecutivo_actual = db(db.misc.id > 0).select(
            db.misc.consecutivo_polizas
            ).first().consecutivo_polizas

    if ultimo < ahora:
        # cambio de mes
        consecutivo = 1 
        db(db.misc.consecutivo_polizas == consecutivo_actual).update(
                consecutivo_polizas = 0
                )
    else:
        consecutivo = consecutivo_actual
        db(db.misc.consecutivo_polizas == consecutivo_actual).update(
                consecutivo_polizas = consecutivo + 1
                )

    folio = armar_folio(consecutivo, fila.tipo, fila.f_poliza)
    db(db.poliza.id == id).update(folio = folio)

    redirect(URL('poliza', 'listar'))


def actualiza_poliza():
    """
    Actualiza un campo de la tabla `poliza`
    """
    id, column = request.post_vars.id.split('.')
    value = request.post_vars.value
    db(db.poliza.id == id).update(**{column:value, 'f_poliza':datetime.now()})
    return value


def actualiza_tipo_poliza():
    """
    Actualiza el campo `tipo` de la tabla `poliza`
    """
    id, column = request.post_vars.id.split('.')
    value = request.post_vars.value

    resultado = db(db.tipo_poliza.nombre == value).select(
            db.tipo_poliza.id,
            ).first()

    db(db.poliza.id == id).update(**{
        'tipo':resultado.id,
        'f_poliza':datetime.now()
        })

    # reducir el código aquí
    fila = db(db.poliza.id == id).select(
            db.poliza.folio,
            db.poliza.tipo,
            db.poliza.f_poliza,
            ).first()

    consecutivo = int(fila.folio[2:8])
    folio = armar_folio(consecutivo, fila.tipo, fila.f_poliza)
    db(db.poliza.id == id).update(folio = folio)
    # fin-reducir el código aquí

    return value


def carga_tipo_poliza():
    """
    Carga el catálogo de los tipos de póliza a un objeto JSON, función auxiliar
    """
    from json import loads, dumps

    query = (db.tipo_poliza.id > 0)

    resultado = db(query).select(
            db.tipo_poliza.id,
            db.tipo_poliza.nombre
            )

    diccionario = dict()

    [diccionario.update({r.id: '{}'.format(r.nombre)})\
            for r in resultado]

    return dumps(diccionario)
