# coding: utf8

# For referencing static and views from other application
def index(): return dict(message="hello from poliza.py")

def listar():
    db.asiento.f_asiento.represent = lambda value, row: DIV(value if value!='' else '-', _class='f_asiento', _id=str(row.id)+'.f_asiento')
    db.asiento.cc_empresa_id.widget = SQLFORM.widgets.autocomplete(request, db.cc_empresa.descripcion, id_field=db.cc_empresa.id, limitby=(0,10), min_length=1)
    db.asiento.cc_empresa_id.represent = lambda value, row: DIV( db.cc_empresa(value).num_cc + ' ' + db.cc_empresa(value).descripcion if value else '-', _class='cc_empresa_id', _id=str(row.id)+'.cc_empresa_id')
    db.asiento.concepto_asiento.represent = lambda value, row: DIV(value if value!='' else '-', _class='concepto_asiento', _id=str(row.id)+'.concepto_asiento')
    db.asiento.debe.represent = lambda value, row: DIV(value if value!='' else '-', _class='debe', _id=str(row.id)+'.debe')
    db.asiento.haber.represent = lambda value, row: DIV(value if value!='' else '-', _class='haber', _id=str(row.id)+'.haber')

    polizas = SQLFORM.smartgrid(db.poliza, linked_tables=['asiento'],
                                onvalidation=valida,
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
        boton_agregar_asiento = A(SPAN(_class="glyphicon glyphicon-indent-left"),' Agregar Asiento', _class="button btn btn-default", _href=URL("poliza", "agregar_asiento" ,args=["poliza", request.args(-1)]))
        boton_contabilizar = A(SPAN(_class="glyphicon glyphicon-book"),' Contabilizar', _class="button btn btn-default", _href=URL("poliza", "contabilizar" ,args=["poliza", request.args(-1)]))
        polizas[2].insert(-1, boton_agregar_asiento)
        polizas[2].insert(-1, boton_contabilizar)

    return dict(polizas=polizas)

def agregar_asiento():
    db.asiento.insert(
            poliza_id = request.args[1],
            concepto_asiento = '',
            debe = 0,
            haber = 0
            )
    redirect(URL('poliza/listar/poliza', 'asiento.poliza_id', args=request.args))

def contabilizar():
    poliza = db.poliza(request.args[1])
    asientos = db(db.asiento.poliza_id==request.args[1]).select()
    debe = 0.0
    haber = 0.0
    for asiento in asientos:
        debe = debe + asiento.debe if asiento.debe else 0.0
        haber = haber + asiento.haber if asiento.haber else 0.0
    session.msgContabiliza = ''
    print debe
    print haber
    if debe!=haber:
        session.msgContabiliza = '\nPóliza no cuadrada.\n Debe = %s Haber = %s'%(debe,haber)
    else:
        session.msgContabiliza = '\nPóliza cuadrada.\n Debe = %s Haber = %s'%(debe,haber)

    redirect(URL('poliza/listar/poliza', 'asiento.poliza_id', args=(request.args)))


def valida(form):
    print "In onvalidation callback"
    print form.vars
    #form.errors= True  #this prevents the submission from completing

    #...or to add messages to specific elements on the form
    #form.errors.first_name = "Do not name your child after prominent deities"
    #form.errors.last_name = "Last names must start with a letter"
    response.flash = "I don't like your submission"


def actualiza_asiento():
    id, column = request.post_vars.id.split('.')
    value = request.post_vars.value
    db(db.asiento.id == id).update(**{column:value})
    return value


def actualiza_descripcion():
    """
    Actualiza el campo `descripcion` de la tabla `asiento`.
    """
    id, column = request.post_vars.id.split('.')
    valor = request.post_vars.value
    resultado = db(db.cc_empresa.id == valor).select(
            db.cc_empresa.num_cc,
            db.cc_empresa.descripcion
            ).first()

    db(db.asiento.id == id).update(**{column:valor})

    return "%s %s" % (resultado.num_cc, resultado.descripcion)

def carga_cc():
    """
    Carga el catálogo de cuentas a un objeto JSON
    """

    from json import loads, dumps

    diccionario = dict()

    result = db(db.cc_empresa.id > 0).select(
            db.cc_empresa.id,
            db.cc_empresa.descripcion
            )

    [diccionario.update({x[1]['id']: x[1]['descripcion']})\
            for x in result.as_dict().items()]

    return dumps(diccionario)
