# coding: utf8
# try something like
def index(): return dict(message="hello from asiento.py")

def listar():
    form = SQLFORM.smartgrid(db.poliza, linked_tables=['asiento'])
    return dict(form=form)
