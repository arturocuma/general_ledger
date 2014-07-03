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
import sqlite3

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

    municipio = db(db.municipio.nombre == nombre).select(db.municipio.id).first()
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
    with open('csvs/localidades.csv', 'rb') as f:

        reader = csv.reader(f)
        lines = [line for line in reader]

        for line in lines:

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

    opciones[:0] = [OPTION('TODOS', _value='')]

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

    opciones[:0] = [OPTION('TODOS', _value='')]

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

    opciones[:0] = [OPTION('TODOS', _value='')]

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

    opciones[:0] = [OPTION('TODOS', _value='')]

    resultado = SELECT(
        _id='localidad_id',
        *opciones,
        **dict(
            _name='localidad',
            requires = IS_IN_DB(db, 'localidad.nombre')
        )
    )
    return resultado


def index2():
    """
    Útil para introducir los datos iniciales de una empresa
    """

    db.pais.nombre.writable = False
    db.pais.nombre.readable = False

    db.estado.nombre.writable = False
    db.estado.nombre.readable = False
    db.estado.clave_interna.writable = False
    db.estado.clave_interna.readable = False

    db.municipio.nombre.writable = False
    db.municipio.nombre.readable = False
    db.municipio.clave_interna.writable = False
    db.municipio.clave_interna.readable = False

    db.localidad.nombre.writable = False
    db.localidad.nombre.readable = False
    db.localidad.clave_interna.writable = False
    db.localidad.clave_interna.readable = False
    db.localidad.lat_grad.writable = False
    db.localidad.lat_grad.readable = False
    db.localidad.lon_grad.writable = False
    db.localidad.lon_grad.readable = False
    db.localidad.lat_dec.writable = False
    db.localidad.lat_dec.readable = False
    db.localidad.lon_dec.writable = False
    db.localidad.lon_dec.readable = False

    form = SQLFORM.factory(db.pais, db.estado, db.municipio,  db.localidad,\
                        db.empresa)

    if form.process().accepted:

        empresa_id = db.empresa.insert(**db.empresa._filter_fields(form.vars))
        vars = {'empresa_id': empresa_id}
        redirect(URL('default', 'index3', vars=vars))
        response.flash = 'OK'

    elif form.errors:
        response.flash = 'Errores en el formulario'
    else:
        response.flash = 'Formulario incompleto'

    return dict(form=form)


def index3():
    """
    Útil para introducir los datos iniciales de una sucursal y departamento
    """

    db.pais.nombre.writable = False
    db.pais.nombre.readable = False

    db.estado.nombre.writable = False
    db.estado.nombre.readable = False
    db.estado.clave_interna.writable = False
    db.estado.clave_interna.readable = False

    db.municipio.nombre.writable = False
    db.municipio.nombre.readable = False
    db.municipio.clave_interna.writable = False
    db.municipio.clave_interna.readable = False

    db.localidad.nombre.writable = False
    db.localidad.nombre.readable = False
    db.localidad.clave_interna.writable = False
    db.localidad.clave_interna.readable = False
    db.localidad.lat_grad.writable = False
    db.localidad.lat_grad.readable = False
    db.localidad.lon_grad.writable = False
    db.localidad.lon_grad.readable = False
    db.localidad.lat_dec.writable = False
    db.localidad.lat_dec.readable = False
    db.localidad.lon_dec.writable = False
    db.localidad.lon_dec.readable = False

    db.sucursal.empresa_id.writable = False
    db.sucursal.empresa_id.readable = False
    db.sucursal.nombre.writable = True
    db.sucursal.nombre.readable = True

    form = SQLFORM.factory(db.sucursal, db.pais, db.estado, db.municipio,\
            db.localidad)

    form.vars.empresa_id = request.vars.empresa_id

    if form.process().accepted:

        sucursal_id = db.sucursal.insert(**db.sucursal._filter_fields(form.vars))

        vars = {'sucursal_id': sucursal_id, 'empresa_id': request.vars.empresa_id}

        redirect(URL('default', 'index4', vars=vars))
        response.flash = 'OK'

    elif form.errors:
        response.flash = 'Errores en el formulario'
    else:
        response.flash = 'Formulario incompleto'

    return dict(form=form)


def index4():
    """
    Útil para introducir los datos iniciales de la sucursal inicial
    """

    db.pais.nombre.writable = False
    db.pais.nombre.readable = False

    db.estado.nombre.writable = False
    db.estado.nombre.readable = False
    db.estado.clave_interna.writable = False
    db.estado.clave_interna.readable = False

    db.municipio.nombre.writable = False
    db.municipio.nombre.readable = False
    db.municipio.clave_interna.writable = False
    db.municipio.clave_interna.readable = False

    db.localidad.nombre.writable = False
    db.localidad.nombre.readable = False
    db.localidad.clave_interna.writable = False
    db.localidad.clave_interna.readable = False
    db.localidad.lat_grad.writable = False
    db.localidad.lat_grad.readable = False
    db.localidad.lon_grad.writable = False
    db.localidad.lon_grad.readable = False
    db.localidad.lat_dec.writable = False
    db.localidad.lat_dec.readable = False
    db.localidad.lon_dec.writable = False
    db.localidad.lon_dec.readable = False

    db.empleado.departamento_id.writable = False
    db.empleado.departamento_id.readable = False
    db.empleado.puesto_id.writable = False
    db.empleado.puesto_id.readable = False

    fields  = [f for f in db.pais]
    fields += [f for f in db.estado]
    fields += [f for f in db.municipio]
    fields += [f for f in db.localidad]
    fields += [f for f in db.puesto]
    fields += [f for f in db.empleado]

    fields += [
        Field('nombre_dep', 'string', label=T('Nombre de Departamento')),
        Field('nombre_emp', 'string', label=T('Nombre de Administrador')),
        Field('nombre_pue', 'string', label=T('Puesto'))
    ]

    #form = SQLFORM.factory(db.pais, db.estado)
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
        redirect(URL('default', 'index5', vars=vars))

        response.flash = 'OK'

    elif form.errors:
        print form.errors
        response.flash = 'Errores en el formulario'
    else:
        response.flash = 'Formulario incompleto'

    return dict(form=form)

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to web2py!")
    return dict(message=T('Hello World'))


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
