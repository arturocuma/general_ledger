# coding: utf8
# try something like
def index(): return dict(message="hello from cc_empresa.py")

def listar():
    form = SQLFORM.smartgrid(db.cc_empresa, linked_tables=['empresa'])
    return dict(form=form)

def resumen():
    query = db.cc_empresa.id==db.asiento.cc_empresa_id
    form = SQLFORM.grid(query)
    return dict(form=form)
