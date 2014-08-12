# coding: utf8
# intente algo como
def index(): return dict(message="hello from configuracion/reportes.py")
def estado_resultados():
    msg=''
    nombre_reporte= db(db.reporte.nombre=='estado_resultados').select(db.reporte.descripcion)
    desc_ingresos= db(db.seccion_reporte.nombre=='ingresos').select(db.seccion_reporte.descripcion)
    desc_costos= db(db.seccion_reporte.nombre=='costos').select(db.seccion_reporte.descripcion)
    desc_gastos= db(db.seccion_reporte.nombre=='gastos').select(db.seccion_reporte.descripcion)
    desc_otros= db(db.seccion_reporte.nombre=='otros').select(db.seccion_reporte.descripcion)
    desc_impuestos= db(db.seccion_reporte.nombre=='impuestos').select(db.seccion_reporte.ALL)
    cuentas_ingresos=db( (db.seccion_reporte.nombre=='ingresos')
                        & (db.cuentas_seccion_reporte.seccion_reporte_id==db.seccion_reporte.id )
                        & (db.cc_empresa.id==db.cuentas_seccion_reporte.cc_empresa_id)).select(db.cc_empresa.ALL)
    cuentas_costos=db( (db.seccion_reporte.nombre=='costos')
                        & (db.cuentas_seccion_reporte.seccion_reporte_id==db.seccion_reporte.id )
                        & (db.cc_empresa.id==db.cuentas_seccion_reporte.cc_empresa_id)).select(db.cc_empresa.ALL)
    cuentas_gastos=db( (db.seccion_reporte.nombre=='gastos')
                        & (db.cuentas_seccion_reporte.seccion_reporte_id==db.seccion_reporte.id )
                        & (db.cc_empresa.id==db.cuentas_seccion_reporte.cc_empresa_id)).select(db.cc_empresa.ALL)
    cuentas_otros=db( (db.seccion_reporte.nombre=='otros')
                        & (db.cuentas_seccion_reporte.seccion_reporte_id==db.seccion_reporte.id )
                        & (db.cc_empresa.id==db.cuentas_seccion_reporte.cc_empresa_id)).select(db.cc_empresa.ALL)
    cuentas_impuestos=db( (db.seccion_reporte.nombre=='impuestos')
                        & (db.cuentas_seccion_reporte.seccion_reporte_id==db.seccion_reporte.id )
                        & (db.cc_empresa.id==db.cuentas_seccion_reporte.cc_empresa_id)).select(db.cc_empresa.ALL)
    cc_empresa = db.executesql("SELECT node.num_cc, node.descripcion,(COUNT(parent.descripcion) - 1) AS depth, "\
                   "node.id, node.cc_vista_id "\
                   "FROM cc_empresa AS node , cc_empresa AS parent "\
                   "WHERE node.lft BETWEEN parent.lft AND parent.rgt "\
                   "GROUP BY node.id "\
                   "ORDER BY node.lft;")
    if request.vars.nombre_reporte=='':
        response.flash=T('Asigne un nombre al reporte')
    elif request.vars.etiqueta_ingresos=='':
        response.flash=T('Asigne una etiqueta a los ingresos')
    elif not request.vars.sel_ingresos:
        response.flash=T('Asigne al menos una cuenta a las cuentas de ingresos')
    elif request.vars.etiqueta_costos=='':
        response.flash=T('Asigne una etiqueta a los costos')
    elif not request.vars.sel_costos:
        response.flash=T('Asigne al menos una cuenta a las cuentas de costos')
    elif request.vars.etiqueta_gastos=='':
        response.flash=T('Asigne una etiqueta a los gastos')
    elif not request.vars.sel_gastos:
        response.flash=T('Asigne al menos una cuenta a las cuentas de gastos')
    elif request.vars.etiqueta_otros=='':
        response.flash=T('Asigne una etiqueta a los otros ingresos y costos')
    elif not request.vars.sel_otros:
        response.flash=T('Asigne al menos una cuenta a las cuentas de otros ingresos y costos')
    elif request.vars.etiqueta_impuestos=='':
        response.flash=T('Asigne una etiqueta a los impuestos')
    elif not request.vars.sel_impuestos:
        response.flash=T('Asigne al menos una cuenta a las cuentas de impuestos')
    else:
        try:
            #Nombre del reporte
            msg='Error en el nombre del reporte'
            reporte=db.reporte.update_or_insert(db.reporte.nombre=='estado_resultados', nombre='estado_resultados', descripcion=request.vars.nombre_reporte)
            #ingresos
            msg='Error en la etiqueta de ingresos'
            ingresos=db.seccion_reporte.update_or_insert(((db.seccion_reporte.reporte_id==reporte) & (db.seccion_reporte.nombre=='ingresos')), reporte_id=reporte, nombre='ingresos', descripcion=request.vars.etiqueta_ingresos)
            msg='Error al eliminar las cuentas de ingresos'
            db(db.cuentas_seccion_reporte.seccion_reporte_id==ingresos).delete()
            if isinstance(request.vars.sel_ingresos, list):
                msg='Error en la seccion de ingresos (1)'
                for cc_ingresos in request.vars.sel_ingresos:
                    db.cuentas_seccion_reporte.insert(seccion_reporte_id=ingresos,
                                                  cc_empresa_id=cc_ingresos)
            else:
                msg='Error en la seccion de ingresos (2)'
                db.cuentas_seccion_reporte.insert(seccion_reporte_id=ingresos,
                                                  cc_empresa_id=request.vars.sel_ingresos)
            #costos
            msg='Error en la etiqueta de costos'
            costos=db.seccion_reporte.update_or_insert(((db.seccion_reporte.reporte_id==reporte) & (db.seccion_reporte.nombre=='costos')), reporte_id=reporte, nombre='costos', descripcion=request.vars.etiqueta_costos)
            msg='Error al eliminar las cuentas de costos'
            db(db.cuentas_seccion_reporte.seccion_reporte_id==costos).delete()
            if isinstance(request.vars.sel_costos, list):
                msg='Error en la sección de costos (1) '
                for cc_costos in request.vars.sel_costos:
                    db.cuentas_seccion_reporte.insert(seccion_reporte_id=costos, cc_empresa_id=cc_costos)
            else:
                msg='Error en la sección de costos (2)'
                db.cuentas_seccion_reporte.insert(seccion_reporte_id=costos, cc_empresa_id=request.vars.sel_costos)
            #gastos
            msg='Error en la etiqueta de gastos'
            gastos=db.seccion_reporte.update_or_insert(((db.seccion_reporte.reporte_id==reporte) & (db.seccion_reporte.nombre=='gastos')), reporte_id=reporte, nombre='gastos', descripcion=request.vars.etiqueta_gastos)
            msg='Error al eliminar las cuentas de gastos'
            db(db.cuentas_seccion_reporte.seccion_reporte_id==gastos).delete()
            if isinstance(request.vars.sel_gastos, list):
                msg='Error en la seccion de gastos (1)'
                for cc_gastos in request.vars.sel_gastos:
                    db.cuentas_seccion_reporte.insert(seccion_reporte_id=gastos, cc_empresa_id=cc_gastos)
            else:
                msg='Error en la seccion de gastos (2)'
                db.cuentas_seccion_reporte.insert(seccion_reporte_id=gastos, cc_empresa_id=request.vars.sel_gastos)
            #otros
            msg='Error en la etiqueta de otros'
            otros=db.seccion_reporte.update_or_insert(((db.seccion_reporte.reporte_id==reporte) & (db.seccion_reporte.nombre=='otros')), reporte_id=reporte, nombre='otros', descripcion=request.vars.etiqueta_otros)
            db(db.cuentas_seccion_reporte.seccion_reporte_id==otros).delete()
            if isinstance(request.vars.sel_otros, list):
                msg='Error en la seccion de otros (1)'
                for cc_otros in request.vars.sel_otros:
                    db.cuentas_seccion_reporte.insert(seccion_reporte_id=otros, cc_empresa_id=cc_otros)
            else:
                msg='Error en la seccion de otros (2)'
                db.cuentas_seccion_reporte.insert(seccion_reporte_id=otros, cc_empresa_id=request.vars.sel_otros)
            #impuestos
            msg='Error en la etiqueta de impuestos'
            impuestos=db.seccion_reporte.update_or_insert(((db.seccion_reporte.reporte_id==reporte) & (db.seccion_reporte.nombre=='impuestos')), reporte_id=reporte, nombre='impuestos', descripcion=request.vars.etiqueta_impuestos)
            db(db.cuentas_seccion_reporte.seccion_reporte_id==impuestos).delete()
            if isinstance(request.vars.sel_impuestos, list):
                msg='Error en la seccion de impuestos (1)'
                for cc_impuestos in request.vars.sel_impuestos:
                    db.cuentas_seccion_reporte.insert(seccion_reporte_id=impuestos, cc_empresa_id=cc_impuestos)
            else:
                msg='Error en la seccion de impuestos (2)'
                db.cuentas_seccion_reporte.insert(seccion_reporte_id=impuestos, cc_empresa_id=request.vars.sel_impuestos)
            
        except:
            db.rollback()
            response.flash=T(msg)
        else:
            db.commit()
            response.flash=T('Configuración realizada')
    
    return dict(cc_empresa=cc_empresa, nombre_reporte=nombre_reporte, desc_ingresos=desc_ingresos, desc_costos=desc_costos, desc_gastos=desc_gastos, desc_otros=desc_otros, desc_impuestos=desc_impuestos, cuentas_ingresos=cuentas_ingresos, cuentas_costos=cuentas_costos, cuentas_gastos=cuentas_gastos, cuentas_otros=cuentas_otros, cuentas_impuestos=cuentas_impuestos)
