# -*- coding: utf-8 -*-

from gluon.tools import Auth
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os
import hashlib


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
                (db_maestro.mi_empresa.tipo == 1) &\
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
                    (db.mi_empresa.user_id == self.user_id) &\
                    (db.mi_empresa.user_id == db.auth_user.id)
            ).select(
                db.empresa.id.with_alias('id'),
                db.empresa.razon_social.with_alias('razon_social'),
                db.mi_empresa.tipo.with_alias('tipo'),
            )

        dbs = {}

        for i in lista:
            instancia=i.id
            if i.tipo == 1:
                # bases de datos propias
                hashear = i.razon_social + auth.user['email']
                nombre_hasheado = hashlib.sha1(hashear).hexdigest()

                dbs[i.id] = DAL(
                        'postgres://web2py:w3b2py@localhost/_{}_{}'.format(
                            auth.user['email'], nombre_hasheado
                            ),
                        check_reserved = ['all'],
                        migrate = False
                        )
            else:
                # bases de datos que se le comparten al usuario

                # obtener email propietario/invitador
                email = db(
                        (db.mi_empresa.empresa_id == i.id) &\
                        (db.mi_empresa.tipo == 1) &\
                        (db.mi_empresa.user_id == db.auth_user.id)
                        ).select(
                            db.auth_user.email.with_alias('email')
                        ).first().email

                hashear = i.razon_social + email
                nombre_hasheado = hashlib.sha1(hashear).hexdigest()

                dbs[i.id] = DAL(
                        'postgres://web2py:w3b2py@localhost/_{}_{}'.format(
                            email, nombre_hasheado
                            ),
                        check_reserved = ['all'],
                        migrate = False
                        )
                pass


        

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

            # Tablas para configuración de reportes
            dbs[instancia].define_table('reporte',
                Field('nombre', 'string', label='Nombre'),
                Field('descripcion', 'string', label='Descripción'),
                format='%(descripcion)s'
                )
            dbs[instancia].define_table('seccion_reporte',
                Field('reporte_id', 'reference reporte', label='Reporte'),
                Field('nombre', 'string', label='Nombre de la sección'),
                Field('descripcion', 'string', label='Etiqueta'),
                format='%(nombre)s %(descripcion)s'
                )
            dbs[instancia].define_table('cuentas_seccion_reporte',
                Field('seccion_reporte_id', 'reference seccion_reporte', label='Etiqueta'),
                Field('cc_empresa_id', 'reference cc_empresa', label='Cuenta'),
                format='%(cc_empresa_id)s'
                )
            '''
            dbs[instancia].define_table('balanza',
                Field('mes', 'reference mes'),
                Field('anio', 'reference anio'),
                Field('saldo_inicial', 'double', represent = lambda value, row: DIV(locale.currency(value, grouping=True ), _style='text-align: right;')),
                Field('cargo', 'double', represent = lambda value, row: DIV(locale.currency(value, grouping=True ), _style='text-align: right;')),
                Field('abono', 'double', represent = lambda value, row: DIV(locale.currency(value, grouping=True ), _style='text-align: right;')),
                Field('saldo_final', 'double', represent = lambda value, row: DIV(locale.currency(value, grouping=True ), _style='text-align: right;')),
                Field('cc_empresa_id', 'reference cc_empresa', label='Cuenta Contable'),
                Field('cierre', 'boolean', default=False)
            )
            '''    
        self.dbs = dbs


class Web2Postgress():
    """
    Interactua con postgres
    """

    def __init__(self):
        self.egg = 'What are you looking for?'


    def crear_db(self, nombre, email):
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

        nombre_hasheado = hashlib.sha1(nombre + email).hexdigest()
        cur.execute('create database "_{}_{}"'.format(email, nombre_hasheado))

        cur.close()
        con.close()


    def eliminar_db(self, nombre, email):
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

        nombre_hasheado = hashlib.sha1(nombre + email).hexdigest()
        cur.execute('drop database "_{}_{}"'.format(email, nombre_hasheado))

        cur.close()
        con.close()


    def cerrar_sesiones():
        pass

empresas = EmpresaDB(db_maestro)
