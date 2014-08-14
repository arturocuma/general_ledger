# coding: utf8
# try something like
(auth.user or request.args(0) == 'login') or redirect(URL('default','login'))

def index(): return dict(message="hello from empresa.py")

def listar():
    form = SQLFORM.smartgrid(db.empresa, linked_tables=['sucursal','departamento','empleado','auth_user'])
    return dict(form=form)


def eliminar():
    """
    Elimina:
    - un registro en la tabla `mi_empresa`
    - cierra sesión de la instancia abierta
    - elimina una instancia de base de datos D:
    """

    id = request.vars.id

    nombre = db_maestro(db_maestro.empresa.id == id).select(
            db_maestro.empresa.razon_social
            ).first().razon_social

    instancia = Web2Postgress()

    # eliminar registro de la base de datos maestra
    db_maestro(db_maestro.empresa.id == id).delete()

    # cerrar cesión
    empresas.dbs[int(id)].close()
    
    # eliminar instancia de base de datos
    instancia.eliminar_db(nombre)


def invitar():
    """
    Envia un email a un usuario 
    """
    from gluon.utils import md5_hash
    from gluon.restricted import RestrictedError
    from gluon.tools import Mail

    empresa_id = request.vars.empresa_id
    usuario = 'Cory Doctorow'
    mensaje = '{} quiere compartir una base de datos contigo'.format(usuario)

    fields = [Field('email_invitado', requires=IS_EMAIL(), label=T('Email'))]

    form = SQLFORM.factory(*fields)

    to = []
    if form.process().accepted:

        email_invitado = form.vars.email_invitado
        to.append(email_invitado)
        
        if mail.send(to=to, subject=mensaje, message=mensaje):
            redirect(URL('default', 'index'))
        else:
            response.flash = 'Mensaje no enviado'

    elif form.errors:
        print 'errores en el formulario'
    else:
        print 'formulario incompleto'

    return dict(form = form)


def compartir():
    """
    Inserta un registro en la tabla `mi_empresa` para darle acceso a otro
    usuario
    """

    empresa_id = request.vars.empresa_id
    usuario_id = request.vars.usuario_id

    db_maestro.mi_empresa.insert(
            user_id = usuario_id,
            empresa_id = empresa_id,
            tipo = 2
            )


def respaldar():
    """
    Crea un respaldo de la base de datos
    """
    pass

