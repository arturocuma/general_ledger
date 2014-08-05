# coding: utf8
# try something like
(auth.user or request.args(0) == 'login') or redirect(URL('default','login'))

def index(): return dict(message="hello from empresa.py")

def listar():
    form = SQLFORM.smartgrid(db.empresa, linked_tables=['sucursal','departamento','empleado','auth_user'])
    return dict(form=form)
