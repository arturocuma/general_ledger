# coding: utf8
# intente algo como
import csv
from datetime import datetime
db=empresas.dbs[int(session.instancias)]

def index(): return dict(message="hello from configuracion/reportes.py")

def estado_resultados():
    msg=''
    tipo_msg=''
    cc_empresa = db.executesql("SELECT node.num_cc, node.descripcion,(COUNT(parent.descripcion) - 1) AS depth, "\
                   "node.id, node.cc_vista_id "\
                   "FROM cc_empresa AS node , cc_empresa AS parent "\
                   "WHERE node.lft BETWEEN parent.lft AND parent.rgt "\
                   "GROUP BY node.id "\
                   "ORDER BY node.lft;")
    print request.vars
    if request.vars:
        if request.vars.nombre_reporte == '':
            tipo_msg='error'
            msg='Asigne un nombre al reporte'
        elif request.vars.etiqueta_1=='':
            tipo_msg='error'
            msg='Asigne una etiqueta a la primer sección'
        elif not request.vars.cuentas_1:
            tipo_msg='error'
            msg='Asigne al menos una cuenta a las cuentas de la primer sección'
        else:
            #try:

                #Nombre del reporte
                reporte_id= db(db.reporte.nombre==request.vars.nombre_reporte).select(db.reporte.ALL).first()
                msg='Error al insertar el nombre del reporte'
                if not reporte_id:
                    reporte_id=db.reporte.insert(nombre=request.vars.nombre_reporte, descripcion=request.vars.nombre_reporte)
                else:
                    reporte_id = reporte_id.id
                #seccion_1
                msg='Error en la etiqueta de ingresos'
                for i in range(1,6):
                    nombre_seccion='seccion_'+str(i)
                    etiqueta_seccion='etiqueta_'+str(i)
                    cuentas_seccion='cuentas_'+str(i)
                    if request.vars[etiqueta_seccion]!='':
                        insert_seccion=db.seccion_reporte.update_or_insert((db.seccion_reporte.reporte_id==reporte_id) & (db.seccion_reporte.nombre==nombre_seccion), reporte_id=reporte_id, nombre=nombre_seccion, descripcion=request.vars[etiqueta_seccion])
                        seccion_id= db((db.seccion_reporte.nombre==nombre_seccion) & (db.seccion_reporte.reporte_id==reporte_id)).select(db.seccion_reporte.ALL).first().id
                        msg='Error al eliminar las cuentas de la seccion'+str(i)
                        db(db.cuentas_seccion_reporte.seccion_reporte_id==seccion_id).delete()
                        if isinstance(request.vars[cuentas_seccion], list):
                            msg='Error en la seccion '+str(i)+' (1)'
                            lista= request.vars[cuentas_seccion]
                            for cc_1 in lista:
                                db.cuentas_seccion_reporte.insert(seccion_reporte_id=seccion_id,
                                                              cc_empresa_id=int(cc_1))
                        elif isinstance(request.vars[cuentas_seccion], str):
                            msg='Error en la seccion '+str(i)+' (2)'
                            db.cuentas_seccion_reporte.insert(seccion_reporte_id=seccion_id,
                                                              cc_empresa_id=int(request.vars[cuentas_seccion]))
                msg='Configuración del reporte realizada'
            #    db.commit()
                tipo_msg='exito'
            #except:
            #    tipo_msg='error'
            #    db.rollback()
    
    return dict(cc_empresa=cc_empresa, msg=XML(msg), tipo_msg=XML(tipo_msg))

def wizard_reportes():
    msg=''
    tipo_msg=''
    cc_empresa = db.executesql("SELECT node.num_cc, node.descripcion,(COUNT(parent.descripcion) - 1) AS depth, "\
                   "node.id, node.cc_vista_id "\
                   "FROM cc_empresa AS node , cc_empresa AS parent "\
                   "WHERE node.lft BETWEEN parent.lft AND parent.rgt "\
                   "GROUP BY node.id "\
                   "ORDER BY node.lft;")
    print request.vars
    if request.vars:
        if request.vars.nombre_reporte == '':
            tipo_msg='error'
            msg='Asigne un nombre al reporte'
        elif request.vars.etiqueta_1=='':
            tipo_msg='error'
            msg='Asigne una etiqueta a la primer sección'
        elif not request.vars.cuentas_1:
            tipo_msg='error'
            msg='Asigne al menos una cuenta a las cuentas de la primer sección'
        else:
            #try:

                #Nombre del reporte
                reporte_id= db(db.reporte.nombre==request.vars.nombre_reporte).select(db.reporte.ALL).first()
                msg='Error al insertar el nombre del reporte'
                if not reporte_id:
                    reporte_id=db.reporte.insert(nombre=request.vars.nombre_reporte, descripcion=request.vars.nombre_reporte)
                else:
                    reporte_id = reporte_id.id
                #seccion_1
                msg='Error en la etiqueta de ingresos'
                for i in range(1,7):
                    nombre_seccion='seccion_'+str(i)
                    etiqueta_seccion='etiqueta_'+str(i)
                    cuentas_seccion='cuentas_'+str(i)
                    if request.vars[etiqueta_seccion]!='':
                        insert_seccion=db.seccion_reporte.update_or_insert((db.seccion_reporte.reporte_id==reporte_id) & (db.seccion_reporte.nombre==nombre_seccion), reporte_id=reporte_id, nombre=nombre_seccion, descripcion=request.vars[etiqueta_seccion])
                        seccion_id= db((db.seccion_reporte.nombre==nombre_seccion) & (db.seccion_reporte.reporte_id==reporte_id)).select(db.seccion_reporte.ALL).first().id
                        msg='Error al eliminar las cuentas de la seccion'+str(i)
                        db(db.cuentas_seccion_reporte.seccion_reporte_id==seccion_id).delete()
                        if isinstance(request.vars[cuentas_seccion], list):
                            msg='Error en la seccion '+str(i)+' (1)'
                            lista= request.vars[cuentas_seccion]
                            for cc_1 in lista:
                                db.cuentas_seccion_reporte.insert(seccion_reporte_id=seccion_id,
                                                              cc_empresa_id=int(cc_1))
                        elif isinstance(request.vars[cuentas_seccion], str):
                            msg='Error en la seccion '+str(i)+' (2)'
                            db.cuentas_seccion_reporte.insert(seccion_reporte_id=seccion_id,
                                                              cc_empresa_id=int(request.vars[cuentas_seccion]))
                msg='Configuración del reporte realizada'
            #    db.commit()
                tipo_msg='exito'
            #except:
            #    tipo_msg='error'
            #    db.rollback()
    
    return dict(cc_empresa=cc_empresa, msg=XML(msg), tipo_msg=XML(tipo_msg))

def cambiar_catalogo():
    db(db.cc_empresa).delete()
    db.executesql('delete from sqlite_sequence where name="cc_empresa";')
    if type(request.vars.csv_catalogo) != str:
        try:
            msg= 'Error al insertar la póliza'
            campos=['lft','rgt', 'clave_usuario','descripcion', 'nivel']
            file = request.vars.csv_catalogo.file
            reader = csv.reader(file)
            for row in reader:
                    
                    valores=[]
                    valores.append(int(row[0]))
                    valores.append(int(row[1]))
                    valores.append(row[2])
                    valores.append(row[3])
                    valores.append(int(row[4]))
                    dictionary = dict(zip(campos, valores))
                    db[db.asiento].insert(**dictionary)
        except:
            db.rollback()
            tipo_msg='error'
        else:
            db.commit()
            tipo_msg='exito'
            msg= 'Catálogo actualizado'
    else:
        tipo_msg='error'
        msg= 'Elija un archivo para subir'
    return dict(tipo_msg=tipo_msg,msg=msg)


def validar_periodo(fecha_usuario):
    periodo = db(
                (db.periodo.inicio <=fecha_usuario) &
                (db.periodo.fin >=fecha_usuario) &
                (db.periodo.estatus_periodo_id != 2)).select(
            db.periodo.ALL,
        ).first()
    if periodo:
        activo=True
    else:
        activo=False
    return activo

def importar_polizas():
    tipo_msg='error'
    tipo = type(request.vars.csv_saldo_inicial)
    if type(request.vars.csv_saldo_inicial)!='str' and request.vars:
                tipo = type(request.vars.csv_saldo_inicial)
                file = request.vars.csv_saldo_inicial.file
                reader = csv.reader(file)
                
                campos=['poliza_id','cc_empresa_id', 'concepto_asiento','debe', 'haber']
                for row in reader:
                    folio_externo=row[0]
                    tipo_poliza=int(row[1])
                    fecha_poliza=row[2]
                    concepto_general=row[3]
                    estatus = validar_periodo(fecha_poliza)
                    if not estatus:
                        msg = 'El periodo de la fecha '+fecha_poliza+' de la póliza '+folio_externo +' no se encuentra activo'
                        break
                    else:
                        poliza = db(db.poliza.folio_externo==folio_externo).select(db.poliza.ALL).first()
                        validacion_poliza=True
                        if not poliza:
                            try:
                                poliza_id = agregar_poliza_csv(folio_externo, tipo_poliza, fecha_poliza, concepto_general)
                            except:
                                msg = 'Error al insertar la póliza. Verifique el formato del archivo CSV'
                                validacion_poliza=False
                        else:
                            poliza_id = poliza.id
                        if validacion_poliza:
                            num_cc=row[4]
                            concepto=row[5]
                            debe=float(row[6])
                            haber=float(row[7])
                            cc=db(db.cc_empresa.num_cc==num_cc).select(db.cc_empresa.id).first()
                            if not cc:
                                msg= 'El número de cuenta '+num_cc+' no existe'
                            else:
                                valores=[]
                                valores.append(poliza_id)
                                valores.append(int(cc.id))
                                valores.append(concepto)
                                valores.append(debe)
                                valores.append(haber)
                                msg= 'Error al insertar los asientos'
                                dictionary = dict(zip(campos, valores))
                                db[db.asiento].insert(**dictionary)
                                tipo_msg='exito'
                                msg= 'Polizas guardadas'
    else:
        tipo_msg='info'
        msg= 'Elija un archivo para subir'
    return dict(tipo_msg=tipo_msg,msg=msg)

def agregar_poliza_csv(folio_externo, tipo, fecha_usuario, concepto_general):
    """
    Agrega un elemento a la tabla `póliza`
    """
    periodo = db(
                (db.periodo.inicio <=fecha_usuario)&
                (db.periodo.fin >=fecha_usuario)).select(
            db.periodo.ALL,
        ).first()
    db(db.periodo.id == periodo.id).update(
                consecutivo = periodo.consecutivo+1
                )
    folio = armar_folio(consecutivo+1, tipo, periodo.fecha_inicio)
    id = db(db.poliza.id == id).update(
            folio = folio,
            tipo=tipo,
            folio_externo=folio_externo,
            fecha_usuario=fecha_usuario,
            concepto_general=concepto_general
                )
    return id
