# -*- coding: utf-8 -*-
import locale
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )

T.force('es')

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
## auth.define_tables(username=False, signature=False) ##se comenta para que no se creee dado que agregaremos campos personalizados a esta tabla

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
#from gluon.contrib.login_methods.janrain_account import use_janrain
#use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

db.define_table('pais',
    Field('nombre', 'string'),
    format='%(nombre)s'
    )

db.define_table('estado',
    Field('clave_interna', 'string'),
    Field('nombre', 'string'),
    Field('pais_id', 'reference pais'),
    format='%(nombre)s'
    )

db.define_table('municipio',
    Field('clave_interna'),
    Field('nombre', 'string'),
    Field('estado_id', 'reference estado'),
    format='%(nombre)s'
    )
        
db.define_table('localidad',
    Field('clave_interna', 'string'),
    Field('nombre', 'string'),
    Field('lat_grad', 'string'),
    Field('lon_grad', 'string'),
    Field('lat_dec', 'string'),
    Field('lon_dec', 'string'),
    Field('municipio_id', 'reference municipio'),
    format='%(nombre)s'
    )

db.define_table('banco',
    Field('nombre', 'string', label='Nombre del Banco'),
    format='%(nombre)s'
    )

db.define_table('persona',
    Field('registro_fiscal', 'string', label='Registro Fiscal'),
    Field('dir_calle', 'string', label='Calle'),
    Field('dir_num_ext', 'string', label='Número Exterior'),
    Field('dir_num_int', 'string', label='Número Interior'),
    Field('dir_colonia', 'string', label='Colonia'),
    Field('dir_cp', 'string', label='Código Postal'),
    Field('dir_telefono', 'string', label='Teléfono'),
    Field('dir_movil', 'string', label='Móvil'),
    Field('dir_email', requires=IS_EMAIL(), label='Email'),
    Field('localidad_id', 'reference localidad', label='Localidad/Ciudad')
    )

db.define_table('empresa',
    Field('razon_social', 'string', label='Razón Social'),
    Field('nombre_comercial', 'string', label='Nombre Comercial'),
    db.persona,
    format='%(razon_social)s'
    )
db.define_table('empresa_banco',
    Field('empresa_id','reference empresa'),
    Field('banco_id','reference banco'),
    Field('clabe','string', label='Número de Cuenta Interbancaria'),
    Field('cuenta','string', label='Número de Cuenta Bancaria'),
    format='%(banco_id)s %(cuenta)s'
    )

db.define_table('sucursal',
    Field('empresa_id', 'reference empresa', label='Empresa'),
    Field('nombre', 'string', label='Nombre de la Sucursal'),
    db.persona,
    format='%(nombre)s'
    )

db.define_table('departamento',
    Field('sucursal_id', 'reference sucursal', label='Sucursal'),
    Field('nombre', 'string'),
    format='%(nombre)s'
    )

db.define_table('puesto',
    Field('nombre', 'string'),
    format='%(nombre)s'
    )

db.define_table('empleado',
    Field('departamento_id', 'reference departamento', label='Departamento Adscrito'),
    Field('puesto_id', 'reference puesto'),
    Field('nombre', 'string', label='Nombre'),
    Field('ap_paterno', 'string', label='Apellido Paterno'),
    Field('ap_materno', 'string', label='Apellido Materno'),
    db.persona,
    format='%(nombre)s %(ap_paterno)s %(ap_materno)s'
    )

db.define_table('proveedor',
    Field('razon_social', 'string', label='Razón Social'),
    Field('nombre_comercial', 'string', label='Nombre Comercial'),
    db.persona,
    Field('producto_comercial', 'string', label='Producto comercial'),
    format='%(razon_social)s'
    )

db.define_table('proveedor_banco',
    Field('proveedor_id','reference proveedor'),
    Field('banco_id','reference banco'),
    Field('clabe','string', label='Número de Cuenta Interbancaria'),
    Field('cuenta','string', label='Número de Cuenta Bancaria'),
    format='%(banco_id)s %(cuenta)s'
    )

auth.settings.extra_fields['auth_user']= [
    Field('empleado_id', 'reference empleado', requires=IS_NULL_OR(IS_IN_DB(db, 'empleado.id', '%(nombre)s %(ap_paterno)s %(ap_materno)s'))),
    ]

auth.define_tables(username=False, signature=False)

db.auth_user._format = '%(first_name)s %(last_name)s (%(email)s)'
## auth.settings.everybody_group_id = 1 ##asignar a nuevos usuarios a un grupo por default 1=ADMIN, 2=BASICO, 3=ETC
## auth.settings.create_user_groups = None

db.define_table('tipo_naturaleza',
   Field('nombre','string'),
   format='%(nombre)s'
   )

db.define_table('tipo_cc',
   Field('nombre','string'),
   format='%(nombre)s'
   )

db.define_table('cc_empresa',
    Field('empresa_id', 'reference empresa', label='Empresa'),
    Field('cuenta_padre', 'reference cc_empresa', represent = lambda id,row: db.cc_empresa(row.cuenta_padre).num_cc if row.cuenta_padre != None else 'Raíz', requires=IS_NULL_OR(IS_IN_DB(db, 'cc_empresa.id', '%(num_cc)s %(descripcion)s')), label='Cuenta Padre'),
    Field('num_cc', 'string', label='Número de Cuenta Contable'),
    Field('descripcion', 'string', label='Descripción'),
    Field('nivel', 'integer'),
    Field('tipo_naturaleza_id', 'reference tipo_naturaleza'), ##ACREEDORA, DEUDORA, DE RESULTADO
    Field('tipo_cc_id', 'reference tipo_cc'), ## DETALLE, ACUMULATIVA
    format='%(num_cc)s %(descripcion)s'
    )

db.define_table('niveles_cc_empresa',
    Field('empresa_id', 'reference empresa', label='Empresa'),
    Field('niveles', 'integer', label='Niveles'),
    Field('digitos_cc_acum', 'integer', label='Dígitos cuentas acum'),
    Field('digitos_cc_aux', 'integer', label='Dígitos cuentas aux'),
    format='%(niveles)s',
    )

db.define_table('tipo_asiento',
    Field('nombre','string'),
    format='%(nombre)s'
    )

db.define_table('poliza',
    Field('f_poliza', 'datetime', label='Fecha de Póliza'),
    Field('concepto_general', 'string'),
    )
db.poliza.id.label='#Póliza'

db.define_table('asiento',
    Field('poliza_id', 'reference poliza', label='#Póliza'),
    Field('tipo', 'reference tipo_asiento'),
    Field('f_asiento', 'datetime', label='Fecha de Asiento'),
    Field('cc_empresa_id', 'reference cc_empresa', label='Cuenta Contable'),
    Field('concepto_movimiento','string'),
    Field('debe', 'double', represent = lambda value, row: DIV(locale.currency(value, grouping=True ), _style='text-align: right;')),
    Field('haber', 'double', represent = lambda value, row: DIV(locale.currency(value, grouping=True ), _style='text-align: right;'))
    )
db.asiento.id.label='#Asiento'

db.define_table('mes',
    Field('nombre','string'),
    format='%(nombre)s'
    )

db.define_table('anio',
    Field('numero','integer'),
    format='%(numero)s'
    )

db.define_table('balanza',
    Field('mes', 'reference mes'),
    Field('anio', 'reference anio'),
    Field('saldo_inicial', 'double', represent = lambda value, row: DIV(locale.currency(value, grouping=True ), _style='text-align: right;')),
    Field('cargo', 'double', represent = lambda value, row: DIV(locale.currency(value, grouping=True ), _style='text-align: right;')),
    Field('abono', 'double', represent = lambda value, row: DIV(locale.currency(value, grouping=True ), _style='text-align: right;')),
    Field('saldo_final', 'double', represent = lambda value, row: DIV(locale.currency(value, grouping=True ), _style='text-align: right;')),
    Field('cc_empresa_id', 'reference cc_empresa', label='Cuenta Contable')
    )
