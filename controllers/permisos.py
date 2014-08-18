# -*- coding: utf-8 -*-
vars={'_next':request.env.request_uri}
(auth.user or request.args(0) == 'login') or\
redirect(URL('default', 'login', vars=vars))

#########################################################################
## En este controlador se administra la sección de roles y permisos
## - index is the default action of any application
#########################################################################

import csv
import sqlite3
db=db_maestro


def crear_permisos():
    """
    Crear permisos por default
    """
    db.auth_permission.insert(name = 'compartir')
    return dict()


def crear_grupos():
    """
    Crear roles por default en el sistema
    """
    db.auth_group.insert(
            role = 'ADMIN',
            description = 'Acceso a todas las funciones del sistema',
            )

    db.auth_group.insert(
            role = 'AUXILIAR CONTABLE',
            description = 'Acceso a pocas funciones del sistema',
            )
    return dict()


def index():
    """
    Por default muestra `usuarios`
    """

    db.auth_user.empleado_id.readable = False
    db.auth_user.id.readable = False

    usuarios = SQLFORM.smartgrid(
            db.auth_user,
            linked_tables=[''],
            exportclasses=dict(
                csv_with_hidden_cols=False,
                json=False,
                tsv_with_hidden_cols=False,
                tsv=False,
                xml=False
                )
            )

    return dict(usuarios=usuarios)

#@auth.requires(auth.has_membership('ADMIN'))
def grupos():
    """
    Muestra los `grupos` de usuarios
    """
    db.auth_user.empleado_id.readable = False
    db.auth_user.empleado_id.writable = False

    db.auth_permission.name.widget = SQLFORM.widgets.autocomplete(
            request,
            db.auth_permission.name,
            limitby = (0, 10),
            min_length = 1
            )

    form = SQLFORM.factory(db.auth_permission)

    db.auth_permission.name.represent = lambda value, row: DIV(
            value if value != '' else '-',
            _class='name',
            _id=str(row.id)+'.name'
            )

    db.auth_group.id.readable = False
    grupos = SQLFORM.smartgrid(
            db.auth_group,
            linked_tables=['auth_permission', 'auth_membership']
            )
    return dict(grupos=grupos)


def actualiza_permiso():

    id, column = request.post_vars.id.split('.')

    value = request.post_vars.value
    db(db.auth_permission.id == id).update(**{column:value})
    return value


#@auth.requires(auth.has_membership('ADMIN'))
def membresia():

    db.auth_membership.id.readable = False
    membresia = SQLFORM.smartgrid(
            db.auth_membership,
            exportclasses=dict(
                csv_with_hidden_cols=False,
                json=False,
                tsv_with_hidden_cols=False,
                tsv=False,
                xml=False
                )
            )
    return dict(membresia=membresia)

#@auth.requires(auth.has_membership('ADMIN'))
def permisos():
    """
    Muestra una lista de `permisos`
    """
    db.auth_permission.id.readable = False
    permisos = SQLFORM.smartgrid(
            db.auth_permission,
            exportclasses=dict(
                csv_with_hidden_cols=False,
                json=False,
                tsv_with_hidden_cols=False,
                tsv=False,
                xml=False
                )
            )
    return dict(permisos=permisos)


def carga_cc():
    """
    Carga el catálogo de cuentas a un objeto JSON
    """

    from json import loads, dumps

    diccionario = dict()

    result = db(db.cc_empresa.id > 0).select(
            db.cc_empresa.id,
            db.cc_empresa.descripcion
            )

    [diccionario.update({x[1]['id']: x[1]['descripcion']})\
            for x in result.as_dict().items()]

    return dumps(diccionario)
