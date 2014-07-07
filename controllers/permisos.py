# -*- coding: utf-8 -*-
vars={'_next':request.env.request_uri}
(auth.user or request.args(0) == 'login') or\
redirect(URL('default', 'user', args='login', vars=vars))

#########################################################################
## En este controlador se administra la sección de roles y permisos
## - index is the default action of any application
#########################################################################

import csv
import sqlite3

def index():
    """
    Por default muestra `usuarios`
    """
    db.auth_user.id.readable = False
    usuarios = SQLFORM.grid(db.auth_user,
                           searchable=True,
                           create=True,
                           editable=True,
                           deletable=True,
                           details=True,
                           orderby= db.auth_user.first_name,
                           user_signature=False,
                           maxtextlengths={'auth_user.email' : 50},
                           exportclasses=dict(
                               csv_with_hidden_cols=False,
                               json=False,
                               tsv_with_hidden_cols=False,
                               tsv=False,
                               xml=False)
                               )

    return dict(usuarios=usuarios)

#@auth.requires(auth.has_membership('ADMIN'))
def grupos():
    """
    Muestra los `grupos` de usuarios
    """

    db.auth_group.id.readable = False
    grupos = SQLFORM.grid(db.auth_group,
                           searchable=True,
                           create=True,
                           editable=True,
                           deletable=True,
                           details=True,
                           orderby= db.auth_group.role,
                           user_signature=False,
                           maxtextlengths={'auth_group.description' :100},
                           exportclasses=dict(
                               csv_with_hidden_cols=False,
                               tsv_with_hidden_cols=False,
                               tsv=False,
                               xml=False)
                               )
    return dict(grupos=grupos)

#@auth.requires(auth.has_membership('ADMIN'))
def membresia():

    db.auth_membership.id.readable = False
    membresia = SQLFORM.grid(db.auth_membership,
                           create=True,
                           editable=True,
                           deletable=True,
                           details=True,
                           orderby= db.auth_membership.group_id,
                           user_signature=False,
                           maxtextlengths={'auth_membership.user_id' : 60},
                           exportclasses=dict(
                               csv_with_hidden_cols=False,
                               json=False,
                               tsv_with_hidden_cols=False,
                               tsv=False,
                               xml=False)
                               )

    return dict(membresia=membresia)

#@auth.requires(auth.has_membership('ADMIN'))
def permisos():

    db.auth_permission.id.readable = False
    permisos = SQLFORM.grid(db.auth_permission,
                           create=True,
                           editable=True,
                           deletable=True,
                           details=True,
                           # orderby= db.auth_permission.group_id,
                           user_signature=False,
                           # maxtextlengths={'auth_permiss.user_id' : 60},
                           exportclasses=dict(
                               csv_with_hidden_cols=False,
                               json=False,
                               tsv_with_hidden_cols=False,
                               tsv=False,
                               xml=False)
                               )

    return dict(permisos=permisos)
