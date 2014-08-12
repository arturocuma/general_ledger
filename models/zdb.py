# -*- coding: utf-8 -*-

from gluon.tools import Auth
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os


class EmpresaDB(object):
    """
    Recupera las bases de datos
    """

    def crear_instancia(self, indice):
        """
        `indice` es el valor usado para mandar llamar una instancia
        """
        instancia = db_maestro(
                (db_maestro.mi_empresa.empresa_id == indice) &\
                (db_maestro.mi_empresa.user_id == self.user_id)
            ).select(
                    db_maestro.empresa.razon_social,
                    db_maestro.empresa.id
                    )


    def __init__(self, db):
        """
        Método init
        """

        self.db = db

        # crear la variable diccionario que almacene los ids
        auth = Auth(db)

        try:
            self.user_id = auth.user['id']
        except:
            self.user_id = None

        lista = db(
                    (db.mi_empresa.empresa_id == db.empresa.id) &\
                    (db.mi_empresa.user_id == self.user_id)
            ).select(
                db.empresa.razon_social, db.empresa.id
            )

        dbs = {}

        for i in lista:

            indice = i.razon_social.lower()

            dbs[i.id] = DAL(
                    'postgres://web2py:w3b2py@localhost/{}'.format(indice),
                    check_reserved = ['all'],
                    migrate = True
                    )

        for instancia in dbs:

            dbs[instancia].define_table('pais',
                    Field('nombre', 'string'),
                    format='%(nombre)s'
                    )

            dbs[instancia].define_table('estado',
                    Field('clave_interna', 'string'),
                    Field('nombre', 'string'),
                    Field('pais_id', 'reference pais'),
                    format='%(nombre)s'
                    )

            dbs[instancia].define_table('municipio',
                    Field('clave_interna'),
                    Field('nombre', 'string'),
                    Field('estado_id', 'reference estado'),
                    format='%(nombre)s'
                    )

            dbs[instancia].define_table('localidad',
                    Field('clave_interna', 'string'),
                    Field('nombre', 'string'),
                    Field('lat_grad', 'string'),
                    Field('lon_grad', 'string'),
                    Field('lat_dec', 'string'),
                    Field('lon_dec', 'string'),
                    Field('municipio_id', 'reference municipio'),
                    format='%(nombre)s'
                    )

            dbs[instancia].define_table('banco',
                    Field('nombre', 'string', label='Nombre del Banco'),
                    format='%(nombre)s'
                    )

            dbs[instancia].define_table('persona',
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

            dbs[instancia].define_table('empresa',
                    Field('razon_social', 'string', label='Razón Social'),
                    Field('nombre_comercial', 'string', label='Nombre Comercial'),
                    dbs[instancia].persona,
                    format='%(razon_social)s'
                    )

            dbs[instancia].define_table('empresa_banco',
                    Field('empresa_id','reference empresa'),
                    Field('banco_id','reference banco'),
                    Field('clabe','string', label='Número de Cuenta Interbancaria'),
                    Field('cuenta','string', label='Número de Cuenta Bancaria'),
                    format='%(banco_id)s %(cuenta)s'
                    )

            dbs[instancia].define_table('sucursal',
                    Field('empresa_id', 'reference empresa', label='Empresa'),
                    Field('nombre', 'string', label='Nombre de la Sucursal'),
                    dbs[instancia].persona,
                    format='%(nombre)s'
                    )

            dbs[instancia].define_table('departamento',
                    Field('sucursal_id', 'reference sucursal', label='Sucursal'),
                    Field('nombre', 'string'),
                    format='%(nombre)s'
                    )

            dbs[instancia].define_table('puesto',
                    Field('departamento_id', 'reference departamento', label='Departamento'),
                    Field('nombre', 'string'),
                    format='%(nombre)s'
                    )

            dbs[instancia].define_table('empleado',
                    Field('puesto_id', 'reference puesto'),
                    Field('nombre', 'string', label='Nombre'),
                    Field('ap_paterno', 'string', label='Apellido Paterno'),
                    Field('ap_materno', 'string', label='Apellido Materno'),
                    dbs[instancia].persona,
                    format='%(nombre)s %(ap_paterno)s %(ap_materno)s'
                    )

            dbs[instancia].define_table('proveedor',
                    Field('razon_social', 'string', label='Razón Social'),
                    Field('nombre_comercial', 'string', label='Nombre Comercial'),
                    dbs[instancia].persona,
                    Field('producto_comercial', 'string', label='Producto comercial'),
                    format='%(razon_social)s'
                    )

            dbs[instancia].define_table('proveedor_banco',
                    Field('proveedor_id','reference proveedor'),
                    Field('banco_id','reference banco'),
                    Field('clabe','string', label='Número de Cuenta Interbancaria'),
                    Field('cuenta','string', label='Número de Cuenta Bancaria'),
                    format='%(banco_id)s %(cuenta)s'
                    )

            dbs[instancia].define_table('cc_naturaleza',
                    Field('nombre','string'),
                    format='%(nombre)s'
                    )

            dbs[instancia].define_table('cc_vista',
               Field('nombre','string'),
               format='%(nombre)s'
               )

            # considerar como clave secundaria
            dbs[instancia].define_table('cc_empresa',
                Field('num_cc', 'string', label='Número de Cuenta Contable'),
                Field('descripcion', 'string', label='Descripción'),
                Field('clave_sat', 'string', label='Clave SAT'),
                Field('cc_naturaleza_id', 'reference cc_naturaleza'),
                Field('cc_vista_id', 'reference cc_vista'),
                Field('lft','integer', default=0),
                Field('rgt','integer', default=0),
                format='%(num_cc)s %(descripcion)s'
                )

            dbs[instancia].define_table('tipo_poliza',
                Field('nombre','string'),
                format='%(nombre)s'
            )

            dbs[instancia].define_table('poliza',
                Field('f_poliza', 'datetime', default=request.now, label='Fecha de Póliza'),
                Field('concepto_general', 'string', label='Concepto de la Póliza'),
                Field('tipo', 'reference tipo_poliza'),
                Field('importe', 'double', 
                    default = 0.0, 
                    represent = lambda value, row: calcula_importe(row.id) if row else 0.0)
            )
            dbs[instancia].poliza.id.label='#Póliza'

            dbs[instancia].define_table('asiento',
                Field('poliza_id', 'reference poliza', label='#Póliza'),
                Field('f_asiento', 'datetime', default=request.now, label='Fecha de Asiento'),
                Field('cc_empresa_id', 'reference cc_empresa', label='Cuenta Contable'),
                Field('concepto_asiento', 'string'),
                Field('debe', 'double', default=0.0),
                Field('haber', 'double', default=0.0)
            )
            dbs[instancia].asiento.id.label='#Asiento'

        self.dbs = dbs


class Web2Postgress():
    """
    Interactua con postgres
    """

    def __init__(self):
        self.egg = 'What are you looking for?'


    def crear_db(self, nombre):
        """
        #ToDo: crear exepciones
        """

        con = connect(
                dbname = 'postgres',
                user = 'web2py',
                host = 'localhost',
                password = 'w3b2py'
                )

        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        cur.execute('create database {}'.format(nombre))
        cur.close()
        con.close()


    def eliminar_db(self, nombre):
        """
        #ToDo: crear exepciones
        """

        con = connect(
                dbname = 'postgres',
                user = 'web2py',
                host = 'localhost',
                password = 'w3b2py'
                )

        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()

        #cur.execute("select pg_terminate_backend(pg_stat_activity.procpid)\
        #from pg_stat_activity\
        #where pg_stat_activity.datname = '{}'\
        #and procpid <> pg_backend_pid();".format(nombre))

        cur.execute('drop database {}'.format(nombre))

        cur.close()
        con.close()


    def cerrar_sesiones():
        pass

empresas = EmpresaDB(db_maestro)
