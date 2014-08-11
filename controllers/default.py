# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

import csv

def insertar_pais(nombre):
    """
    Inserta un registro `pais` si no existe,
    en caso contrario retorna su id
    """
    pais = db(db.pais.nombre == nombre).select(db.pais.id).first()
    if not pais:
        return db.pais.insert(nombre = nombre)
    else:
        return pais.id


def insertar_estado(nombre, clave_interna, pais_id):
    """
    Inserta un registro `estado` si no existe,
    en caso contrario retorna su id
    """
    estado = db(db.estado.nombre == nombre).select(db.estado.id).first()
    if not estado:
        return db.estado.insert(
                nombre = nombre,
                clave_interna = clave_interna,
                pais_id = pais_id
                )
    else:
        return estado.id


def insertar_municipio(nombre, clave_interna, estado_id):
    """
    Inserta un registro `municipio` si no existe,
    en caso contrario retorna su id
    """

    municipio = db(
            (db.municipio.nombre == nombre) &
            (db.municipio.estado_id == estado_id)
            ).select(db.municipio.id).first()
    if not municipio:
        return db.municipio.insert(
                nombre = nombre,
                clave_interna = clave_interna,
                estado_id = estado_id
                )
    else:
        return municipio.id


def insertar_localidad(
        nombre,
        clave_interna,
        lat_grad,
        lon_grad,
        lat_dec,
        lon_dec,
        municipio_id
        ):
    """
    Inserta un registro `localidad`
    """

    db.localidad.insert(
            nombre = nombre,
            clave_interna = clave_interna,
            lat_grad = lat_grad,
            lon_grad = lon_grad,
            lat_dec = lat_dec,
            lon_dec = lon_dec,
            municipio_id = municipio_id
        )


def precargar():
    pais_id = insertar_pais('MÉXICO')

    # precargar estados
    with open('localidades.csv', 'rb') as f:

        reader = csv.reader(f)

        for line in reader:

            estado_id = insertar_estado(line[1], line[0], pais_id)
            municipio_id = insertar_municipio(line[3], line[2], estado_id)
            insertar_localidad(
                    line[5], line[4],
                    float(line[6]), float(line[7]),
                    float(line[8]), float(line[9]),
                    municipio_id
                    )
    return dict()


def cargar_paises():
    """
    Genera un objeto SELECT de los países que ya existen en la BD.
    """

    opciones = [OPTION(pais.nombre, _value=pais.id) for pais in\
               db().select(
                   db.pais.ALL,
                   #cache=(cache.ram, 3600) #problemas SQLite
                   )
               ]

    #opciones[:0] = [OPTION('TODOS', _value='')]

    resultado = SELECT(
        _id='pais_id',
        *opciones,
        **dict(
            _name='paises',
            requires = IS_IN_DB(db,'pais.nombre')
        )
    )
    return resultado


def cargar_estados():
    """
    Genera un objeto SELECT de los estados del pais X.
    """

    opciones = [OPTION(estado.nombre, _value=estado.id) for estado in\
               db(db.estado.pais_id == request.vars.pais_id).select(
                   db.estado.ALL,
                   #cache=(cache.ram, 3600) #problemas SQLite
                   )
               ]
    #opciones[:0] = [OPTION('TODOS', _value='')]

    resultado = SELECT(
        _id='estado_id',
        *opciones,
        **dict(
            _name='estados',
            requires = IS_IN_DB(db, 'estado.nombre')
        )
    )
    return resultado


def cargar_municipios():
    """
    Genera un objeto SELECT de los municipios del estado X.
    """

    opciones = [OPTION(municipio.nombre, _value=municipio.id) for municipio in\
               db(db.municipio.estado_id == request.vars.estado_id).select(
                   db.municipio.ALL,
                   #cache=(cache.ram, 3600) #problemas SQLite
                   )
               ]

    #opciones[:0] = [OPTION('TODOS', _value='')]

    resultado = SELECT(
        _id='municipio_id',
        *opciones,
        **dict(
            _name='municipios',
            requires = IS_IN_DB(db, 'municipio.nombre')
        )
    )
    return resultado


def cargar_localidades():
    """
    Genera un objeto SELECT de las localidades del municipio X.
    """

    opciones = [OPTION(localidad.nombre, _value=localidad.id) for localidad in\
               db(db.localidad.municipio_id == request.vars.municipio_id).select(
                   db.localidad.ALL,
                   #cache=(cache.ram, 3600) #problemas SQLite
                   )
               ]

    # opciones[:0] = [OPTION('TODOS', _value='')]

    resultado = SELECT(
        _id='localidad_id',
        *opciones,
        **dict(
            _name='localidad',
            requires = IS_IN_DB(db, 'localidad.nombre')
        )
    )
    return resultado


@auth.requires_login()
def empresa_wizard():
    """
    Útil para introducir los datos iniciales de una empresa
    """

    campos = [
        Field('pais_id', 'string', label=T('País')),
        Field('estado_id', 'string', label=T('Estado')),
        Field('municipio_id', 'string', label=T('Municipio')),
        Field('localidad_id', 'string', label=T('Localidad')),
        Field('registro_fiscal', 'string', label='Registro Fiscal'),
        Field('dir_calle', 'string', label=T('Calle')),
        Field('dir_num_ext', 'string', label=T('Número Exterior')),
        Field('dir_num_int', 'string', label=T('Número Interior')),
        Field('dir_colonia', 'string', label='Colonia'),
        Field('dir_cp', 'string', label='Código Postal'),
        Field('dir_telefono', 'string', label='Teléfono'),
        Field('dir_movil', 'string', label='Móvil'),
        Field('dir_email', requires=IS_EMAIL(), label='Email'),
        Field('razon_social', 'string', label='Razón Social'),
        Field('nombre_comercial', 'string', label='Nombre Comercial'),
    ]

    form = SQLFORM.factory(*campos)

    if form.process().accepted:
        
        empresa_id = db.empresa.insert(**db.empresa._filter_fields(form.vars))
        vars = {'empresa_id': empresa_id}

        session.flash = 'Se han configurado correctamente los datos de la empresa'
        db.mi_empresa.insert(user_id=auth.user['id'], empresa_id=empresa_id)

        # se crea la base de datos con el nombre de la misma
        nombre = form.vars.razon_social
        instancia = Web2Postgress()
        instancia.crear_db(nombre)

        redirect(URL('cc_empresa', 'cc_wizard', vars=vars))

    elif form.errors:
        response.flash = 'Errores en el formulario'
    else:
        response.flash = 'Formulario incompleto'

    return dict(form=form)


def index3():
    """
    Útil para introducir los datos iniciales de una sucursal y departamento
    """

    campos = [
        Field('pais_id', 'string', label=T('País')),
        Field('estado_id', 'string', label=T('Estado')),
        Field('municipio_id', 'string', label=T('Municipio')),
        Field('localidad_id', 'string', label=T('Localidad')),
        Field('registro_fiscal', 'string', label='Registro Fiscal'),
        Field('dir_calle', 'string', label=T('Calle')),
        Field('dir_num_ext', 'string', label=T('Número Exterior')),
        Field('dir_num_int', 'string', label=T('Número Interior')),
        Field('dir_colonia', 'string', label=T('Colonia')),
        Field('dir_cp', 'string', label=T('Código Postal')),
        Field('dir_telefono', 'string', label=T('Teléfono')),
        Field('dir_movil', 'string', label=T('Móvil')),
        Field('dir_email', requires=IS_EMAIL(), label=T('Email')),
        Field('nombre_suc', 'string', label=T('Nombre Sucursal')),
    ]

    form = SQLFORM.factory(*campos)

    if form.process().accepted:

        form.vars.empresa_id = request.vars.empresa_id
        form.vars.nombre = request.vars.nombre_suc
        sucursal_id = db.sucursal.insert(**db.sucursal._filter_fields(form.vars))

        vars = {'sucursal_id': sucursal_id, 'empresa_id': request.vars.empresa_id}

        response.flash = 'Se han configurado correctamente los datos de la sucursal'
        session.flash = 'Se han configurado correctamente los datos de la sucursal'
        redirect(URL('default', 'index4', vars=vars))

    elif form.errors:
        response.flash = 'Errores en el formulario'
    else:
        response.flash = 'Formulario incompleto'

    return dict(form=form)


def index4():
    """
    Útil para introducir los datos iniciales del departamento y usuario
    """

    fields = [
        Field('pais_id', 'string', label=T('País')),
        Field('estado_id', 'string', label=T('Estado')),
        Field('municipio_id', 'string', label=T('Municipio')),
        Field('localidad_id', 'string', label=T('Localidad')),
        Field('registro_fiscal', 'string', label='Registro Fiscal'),
        Field('dir_calle', 'string', label=T('Calle')),
        Field('dir_num_ext', 'string', label=T('Número Exterior')),
        Field('dir_num_int', 'string', label=T('Número Interior')),
        Field('dir_colonia', 'string', label=T('Colonia')),
        Field('dir_cp', 'string', label=T('Código Postal')),
        Field('dir_telefono', 'string', label=T('Teléfono')),
        Field('dir_movil', 'string', label=T('Móvil')),
        Field('dir_email', requires=IS_EMAIL(), label=T('Email')),
        Field('nombre_emp', 'string', label=T('Nombre Empleado')),
        Field('ap_paterno', 'string', label=T('Apellido Paterno')),
        Field('ap_materno', 'string', label=T('Apellido Materno')),
        Field('nombre_pue', 'string', label=T('Puesto')),
        Field('nombre_dep', 'string', label=T('Departamento')),
    ]

    form = SQLFORM.factory(*fields)

    if form.process().accepted:

        # insertar departamento
        form.vars.sucursal_id = request.vars.sucursal_id
        form.vars.nombre = request.vars.nombre_dep
        departamento_id = db.departamento.insert(
                **db.departamento._filter_fields(form.vars)
                )

        # insertar puesto
        form.vars.nombre = request.vars.nombre_pue
        puesto_id = db.puesto.insert(**db.puesto._filter_fields(form.vars))

        # insertar empleado
        form.vars.nombre = form.vars.nombre_emp
        form.vars.departamento_id = departamento_id
        form.vars.puesto_id = puesto_id
        empleado_id = db.empleado.insert(
                **db.empleado._filter_fields(form.vars)
                )

        vars = {'empresa_id': request.vars.empresa_id}

        session.flash = 'Se han configurado correctamente los datos de la sucursal'
        #redirect(URL('default', 'index5', vars=vars))

    elif form.errors:
        response.flash = 'Errores en el formulario'
    else:
        response.flash = 'Formulario incompleto'

    return dict(form=form)

def user():

    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    if request.args(0)=='logout':

        #print '<-----------------'
        #print dir(empresas.dbs[1])
        #print '----------------->'
        #for instancia in empresas.dbs:
        #    empresas.dbs[1].close()

        cookieDelete()

    elif request.args(0)=='login':
        auth.settings.login_form=GoogleAccount()
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

def cookieCreate():
        response.cookies['login_general_ledger'] = auth.user['email']
        response.cookies['login_general_ledger']['expires'] = 24 * 3600
        response.cookies['login_general_ledger']['path'] = '/'

        response.cookies['picture_usr'] = session.picture
        response.cookies['picture_usr']['expires'] = 24 * 3600
        response.cookies['picture_usr']['path'] = '/'

        response.cookies['id_usuario']= auth.user['id']
        response.cookies['id_usuario']['expires'] = 24 * 3600
        response.cookies['id_usuario']['path'] = '/'

def cookieDelete():
        response.cookies['login_general_ledger'] = 'invalid'
        response.cookies['login_general_ledger']['expires'] = -10
        response.cookies['login_general_ledger']['path'] = '/'

        response.cookies['id_usuario']= 'invalid'
        response.cookies['id_usuario']['expires'] = 24 * 3600
        response.cookies['id_usuario']['path'] = '/'

        response.cookies['picture_usr'] = 'invalid'
        response.cookies['picture_usr']['expires'] = -10
        response.cookies['picture_usr']['path'] = '/'

def login():
    from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
    auth = Auth(db)
    #auth.settings.login_form=GoogleAccount()
    form = auth.login()

    return dict(form=form)


def index():
    import urllib
    import urllib2
    import gluon.contrib.simplejson
    from gluon.storage import Storage
    from uuid import uuid4
    from gluon.storage import Storage

    print session.instancias

    if session.auth:

        if not request.cookies.has_key('login_general_ledger'):
            cookieCreate()
            #session.instancias = []
            session.instancias = 0

        #código repetido, digno de eliminarse
        mias = db(
                (db.mi_empresa.user_id == auth.user['id']) &\
                (db.mi_empresa.empresa_id == db.empresa.id) &\
                (db.mi_empresa.tipo == 1)
           ).select(
                   db.empresa.razon_social,
                   db.empresa.id
                   )

        compartidas = db(
                (db.mi_empresa.user_id == auth.user['id']) &\
                (db.mi_empresa.empresa_id == db.empresa.id) &\
                (db.mi_empresa.tipo == 2)
            ).select(
                    db.empresa.razon_social,
                    db.empresa.id
                    )

    elif request.cookies.has_key('login_general_ledger'):
        usuario = db(db.auth_user.email==request.cookies['login_general_ledger'].value).select()
        #if 'picture' in data:
        #    session.picture = data['picture']
        user = db(db.auth_user.id==usuario[0].id).select().first()
        auth.settings.long_expiration = 3600*24*30 # one month
        auth.settings.remember_me_form = True
        auth.user = Storage(auth.settings.table_user._filter_fields(user, id=True))
        session.auth = Storage(user=auth.user, last_visit=request.now, expiration=auth.settings.expiration)
        session.picture = request.cookies['picture_usr'].value

        #session.instancias = []
        session.instancias = 0

        mias = db(
                (db.mi_empresa.user_id == auth.user['id']) &\
                (db.mi_empresa.empresa_id == db.empresa.id) &\
                (db.mi_empresa.tipo == 1)
           ).select(
                   db.empresa.razon_social,
                   db.empresa.id
                   )

        compartidas = db(
                (db.mi_empresa.user_id == auth.user['id']) &\
                (db.mi_empresa.empresa_id == db.empresa.id) &\
                (db.mi_empresa.tipo == 2)
            ).select(
                    db.empresa.razon_social,
                    db.empresa.id
                    )
    else:
        # the user is not logged
        mias = ''
        compartidas = ''

    return dict(mias=mias, compartidas=compartidas)
