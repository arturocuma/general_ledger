# coding: utf8
# try something like
def index(): return dict(message="hello from poliza.py")

def listar():
    db.asiento.f_asiento.represent = lambda value, row: DIV(value if value!='' else '-', _class='f_asiento', _id=str(row.id)+'.f_asiento')
    db.asiento.cc_empresa_id.widget = SQLFORM.widgets.autocomplete(request, db.cc_empresa.descripcion, id_field=db.cc_empresa.id, limitby=(0,10), min_length=1)
    db.asiento.cc_empresa_id.represent = lambda value, row: DIV( db.cc_empresa(value).num_cc + ' ' + db.cc_empresa(value).descripcion if value else '-', _class='cc_empresa_id', _id=str(row.id)+'.cc_empresa_id')
    db.asiento.concepto_asiento.represent = lambda value, row: DIV(value if value!='' else '-', _class='concepto_asiento', _id=str(row.id)+'.concepto_asiento')
    db.asiento.debe.represent = lambda value, row: DIV(value if value!='' else '-', _class='debe', _id=str(row.id)+'.debe')
    db.asiento.haber.represent = lambda value, row: DIV(value if value!='' else '-', _class='haber', _id=str(row.id)+'.haber')

    if request.args(-3) == 'poliza' and request.args(-2) == 'asiento.poliza_id':
        links=[dict(header=T('Action'), 
                        body=lambda row: DIV(A(I(_class='icon-print'), _title=T("Print invoice"), 
                                               _target="_blank", _class="button", 
                                               _href=URL("print", "print_invoice", args=[row.id])), 
                                               A(I(_class='icon-envelope'), _title=T("Mail invoice"), 
                                                 _target="_blank", _class="button", 
                                                 _href="#"
                                              )
                        ))
                      ]
        links = [lambda row: A(SPAN(_class="glyphicon glyphicon-indent-left"),' Agregar Asiento', _class="button btn btn-default", _href=URL("poliza", "agregar_asiento" ,args=["poliza", request.args(-1)]))]

    else:
        links=None

    polizas = SQLFORM.smartgrid(db.poliza, linked_tables=['asiento'],
                                links=links,
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
    return dict(polizas=polizas)

def agregar_asiento():
    db.asiento.insert(poliza_id=request.args[1])
    redirect(URL('poliza/listar/poliza', 'asiento.poliza_id', args=request.args))


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
