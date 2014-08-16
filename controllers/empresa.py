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
    email = auth.user['email']
    instancia.eliminar_db(nombre, email)

    session.instancias = 0


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


def aceptar():
    """
    Inserta un registro en la tabla `mi_empresa` para darle acceso a otro
    usuario
    """

    empresa_id = request.vars.empresa_id
    usuario_id = auth.user['id']

    db_maestro.mi_empresa.insert(
            user_id = usuario_id,
            empresa_id = empresa_id,
            tipo = 2
            )

    redirect(URL('default','index'))


def respaldar():
    """
    Crea un respaldo de la base de datos
    """
    pass


def opciones():
    """
    Opciones de configuración de cada empresa:
    - eliminar
    - crear respaldos
    - compartir empresas
    """

    # enviar el email temporalmente desde aquí
    # se declara `to` como lista, para que se puedan agregar varios correos
    # ToDo: 

    from gluon.utils import md5_hash
    from gluon.restricted import RestrictedError
    from gluon.tools import Mail
    import hashlib
    import datetime

    empresa_id = session.instancias

    fields = [Field('invitado', requires=IS_EMAIL(), label=T('Email'))]
    form = SQLFORM.factory(*fields)

    if form.process().accepted:

        invitacion = form.vars.invitado + auth.user['email'] + empresa_id
        
        url_hash = hashlib.sha1(invitacion).hexdigest()
        url = URL('empresa', 'invitacion', args=[url_hash], host=True)

        usuario = '{} {}'.format(auth.user['first_name'], auth.user['last_name'])
        asunto = '{} quiere compartir una empresa contigo'.format(usuario)
        mensaje = '{} quiere compartir una empresa contigo a través\
                de Sistemas Contables XYZ. Dale click a la URL:\
                {}'.format(usuario, url)

        to = []
        to.append(form.vars.invitado)
        
        if mail.send(to=to, subject=asunto, message=mensaje):
            response.flash = 'Mensaje enviado'
            db_maestro.invitacion.insert(
                    user_id = auth.user['id'],
                    empresa_id = session.instancias,
                    email_invitado = form.vars.invitado,
                    fecha = datetime.date.today(),
                    url_hash = url_hash
                    )
        else:
            response.flash = 'Mensaje no enviado'

    elif form.errors:
        print 'errores en el formulario'
    else:
        print 'formulario incompleto'

    return dict(form=form)


def invitacion():
    url_hash = request.args(0)
    query = url_hash == db_maestro.invitacion.url_hash

    invitacion = db_maestro(query).select(
            db_maestro.invitacion.empresa_id,
            db_maestro.invitacion.user_id
            ).first()

    razon_social = db_maestro(
            db_maestro.empresa.id == invitacion.empresa_id
            ).select(
                    db_maestro.empresa.razon_social
                ).first().razon_social

    usuario = db_maestro(
            db_maestro.auth_user.id == invitacion.user_id
            ).select(
                    db_maestro.auth_user.first_name,
                    db_maestro.auth_user.last_name
                ).first()
    usuario = '{} {}'.format(usuario.first_name, usuario.last_name)
    vars = {'empresa_id': invitacion.empresa_id,
            'usuario_id': invitacion.user_id}

    return dict(
            usuario=usuario,
            razon_social=razon_social,
            vars = vars
            )
