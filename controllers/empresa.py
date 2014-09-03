# coding: utf8

from gluon.utils import md5_hash
from gluon.restricted import RestrictedError
from gluon.tools import Mail

vars={'_next':request.env.request_uri}
(auth.user or request.args(0) == 'login') or\
redirect(URL('default', 'user', args='login', vars=vars))

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
    import os
    import shutil

    id = request.vars.id

    nombre = db_maestro(db_maestro.empresa.id == id).select(
            db_maestro.empresa.razon_social
            ).first().razon_social

    instancia = Web2Postgres()

    # eliminar registro de la base de datos maestra
    db_maestro(db_maestro.empresa.id == id).delete()

    # cerrar cesión
    empresas.dbs[int(id)].close()
    
    # eliminar instancia de base de datos
    email = auth.user['email']
    instancia.eliminar_db(nombre, email)

    # eliminar del folder databases
    hashear = nombre + email
    nombre_hasheado = hashlib.sha1(hashear).hexdigest()
    path = os.path.join(request.folder, 'databases/{}/'.format(nombre_hasheado))
    shutil.rmtree(path)

    session.instancias = 0


def invitar():
    """
    Lo que está en `opciones` debe ir aquí cuando se use AJAX en la vista
    """
    pass


def aceptar():
    """
    Este controlador es ejecutado por el invitado:
    - Inserta un registro en la tabla `mi_empresa` para darle acceso a otro
    usuario
    - Elimina la invitación
    - Envia una notificación al propietario de que la invitación ha sido
    aceptada
    """

    empresa_id = request.vars.empresa_id
    usuario_id = auth.user['id']

    db_maestro.mi_empresa.insert(
            user_id = usuario_id,
            empresa_id = empresa_id,
            tipo = 2
            )

    # eliminar invitación
    url_hash = request.vars.url_hash
    db_maestro(db_maestro.invitacion.url_hash == url_hash).delete()

    # notificar al propietario
    email_propietario = request.vars.email_propietario
    asunto = 'La invitación a {} ha sido aceptada'.format('invitado')
    mensaje = asunto
    
    if mail.send(to=[email_propietario], subject=asunto, message=mensaje):
        redirect(URL('default', 'index'))
    else:
        response.flash = 'Mensaje no enviado'

    redirect(URL('default','index'))


def respaldar():
    """
    Crea un respaldo de la base de datos
    """
    from json import loads, dumps
    id = request.vars.id

    razon_social = db_maestro(db_maestro.empresa.id == id).select(
            db_maestro.empresa.razon_social
            ).first().razon_social

    instancia = Web2Postgres()

    # crear respaldo
    email = auth.user['email']
    path = instancia.crear_respaldo(razon_social, email)
    diccionario = {'url': URL('static', path)}

    return dumps(diccionario)


def configuracion():
    """
    Opciones de configuración de cada empresa:
    - eliminar
    - crear respaldos
    - compartir empresas
    """

    # enviar el email temporalmente desde aquí
    # se declara `to` como lista, para que se puedan agregar varios correos
    # ToDo: 

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
                    fecha = datetime.datetime.now(),
                    url_hash = url_hash
                    )
        else:
            response.flash = 'Mensaje no enviado'

    elif form.errors:
        print 'errores en el formulario'
    else:
        pass

    return dict(form=form)


def invitacion():
    url_hash = request.args(0)
    query = url_hash == db_maestro.invitacion.url_hash

    invitado = auth.user['email']

    invitacion = db_maestro(query).select(
            db_maestro.invitacion.empresa_id,
            db_maestro.invitacion.email_invitado,
            db_maestro.invitacion.user_id,
            db_maestro.invitacion.url_hash,
            ).first()

    if invitacion: 
        if invitado == invitacion.email_invitado:
            razon_social = db_maestro(
                    db_maestro.empresa.id == invitacion.empresa_id
                    ).select(
                            db_maestro.empresa.razon_social
                        ).first().razon_social

            usuario = db_maestro(
                    db_maestro.auth_user.id == invitacion.user_id
                    ).select(
                            db_maestro.auth_user.first_name,
                            db_maestro.auth_user.last_name,
                            db_maestro.auth_user.email
                        ).first()

            email_propietario = usuario.email
            usuario = '{} {}'.format(usuario.first_name, usuario.last_name)

            vars = {'empresa_id': invitacion.empresa_id,
                    'email_propietario': email_propietario,
                    'url_hash': invitacion.url_hash}

            return dict(
                    no_invitado=False,
                    usuario=usuario,
                    razon_social=razon_social,
                    vars = vars
                    )
        else:
            # invitado incorrecto
            return dict(no_invitado=True)
    else:
        # invitacion inexistente
        return dict(no_invitado=True)
