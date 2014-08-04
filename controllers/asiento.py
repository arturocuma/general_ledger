# coding: utf8
# try something like
(auth.user or request.args(0) == 'login') or redirect(URL('default', 'user', args='login'))

def index(): return dict(message="hello from asiento.py")

def listar():
    form = SQLFORM.smartgrid(db.poliza, linked_tables=['asiento'])
    return dict(form=form)
