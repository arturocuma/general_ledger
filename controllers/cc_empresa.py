# coding: utf8
# try something like
def index(): return dict(message="hello from cc_empresa.py")

def crear_cc(form):
    if form.record:
        form.vars.num_cc = form.vars.num_cc
    elif (form.vars.num_cc != ''):
        empresa_id=1
        niveles_cc_empresa=db(db.niveles_cc_empresa.empresa_id==empresa_id).select()
        niveles_cc=niveles_cc_empresa[0]
        if form.vars.tipo_cc_id=='1':#Acumulativa
            num_niv=int(niveles_cc['digitos_cc_acum'])
        elif form.vars.tipo_cc_id=='2':#Auxiliar
            num_niv=int(niveles_cc['digitos_cc_aux'])
    
        num_cc= form.vars.num_cc
        num_cc= str(num_cc).zfill(num_niv)
        form.vars.num_cc = db.cc_empresa(form.vars.cuenta_padre).num_cc +'.'+ num_cc
        print form.vars
    return

def listar():
    form = SQLFORM.smartgrid(db.cc_empresa,
                             ##onvalidation = crear_cc,
                             editable = True,
                             linked_tables=['empresa'])
    return dict(form=form)

def resumen():
    return dict(message='resumen')
