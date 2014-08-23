# coding: utf8
# try something like
import time

if session.instancias:
    db=empresas.dbs[int(session.instancias)]
(auth.user or request.args(0) == 'login') or redirect(URL('default', 'login'))

def index(): return dict(message="hello from reportes.py")

def sumas():
    query = (db.cc_empresa.id>0) & (db.cc_empresa.empresa_id==db.empresa.id) & (db.empresa.id==1)
    return dict(message=query)
def ancestor(num_cc):
    tabla = db['cc_empresa']
    node = db(tabla.num_cc == num_cc).select().first()
    return db( (tabla.lft < node.lft) & (tabla.rgt > node.rgt) ).select(tabla.num_cc, orderby=tabla.lft).last()

def c():
    rows=db().select(
        db.asiento.ALL, db.poliza.ALL,
        left=db.asiento.on(db.asiento.poliza_id==db.poliza.id)
        )
    loquesea=db(db.asiento.poliza_id==db.poliza.id).select(db.poliza.ALL)
    return loquesea

def cc_grid2():
    num_cc='1.1'
    nivel='2'
    cc_empresa = hijos_nivel(num_cc, nivel)
    tabla='<table>'
    for cc in cc_empresa:
        tabla+='<tr><td>'+cc[0]+' '+cc[1]+'</td></tr>'
    tabla+='</table>'
    return dict(cc_empresa=XML(tabla))


def balanza():
    cc_empresa = tabla_balanza()
    return dict(cc_empresa=cc_empresa)

def hijos_nivel(num_cc,nivel):
    if num_cc!='':
        cuenta= " AND node.num_cc = "+num_cc
    else:
        cuenta= " "
    query="SELECT node.num_cc, node.descripcion, (COUNT(parent.id) - (sub_tree.depthh + 1)) AS depth,"\
                               " node.id, node.cc_vista_id FROM cc_empresa AS node,"\
                               " cc_empresa AS parent,"\
                               " cc_empresa AS sub_parent,"\
                               " ("\
                               " SELECT node.id, node.num_cc, node.descripcion, (COUNT(parent.id) - 1) AS depthh"\
                               " FROM cc_empresa AS node,"\
                               " cc_empresa AS parent"\
                               " WHERE node.lft BETWEEN parent.lft AND parent.rgt"\
                               " "+cuenta+""\
                               " GROUP BY node.id"\
                               " ORDER BY node.lft"\
                               " )AS sub_tree"\
                               " WHERE node.lft BETWEEN parent.lft AND parent.rgt"\
                               " AND node.lft BETWEEN sub_parent.lft AND sub_parent.rgt"\
                               " AND sub_parent.id = sub_tree.id"\
                               " GROUP BY node.id"\
                               " HAVING depth = "+nivel+""\
                               " ORDER BY node.lft;"
    hijos = db.executesql(query)
    return hijos

def color_nivel(nivel):
    color = '#000'
    if nivel == 0:
        color = '#000'
    elif nivel == 1:
        color = '#111640'
    elif nivel == 2:
        color = '#212C7F'
    elif nivel == 3:
        color = '#3242BF'
    elif nivel == 4:
        color = '#4258FF'
    elif nivel == 5:
        color = '#168BBF'
    elif nivel == 6:
        color = '#1DBAFF'
    else:
        color = '#28DDFF'
    return color

def importe_cuenta_balanza(num_cc, cc_naturaleza_id, fecha):
    #fecha_actual=time.strftime("%Y-%m-%d 23:59:59")
    #mes_actual=time.strftime("%Y-%m-01 00:00:00")
    #if acumulado==True:
    filtro=" AND poliza.fecha_usuario <= '"+str(fecha)+"'"
    #elif acumulado==False:
    #cadena=" AND f_asiento between '"+fecha_inicial+"' and '"+fecha_final+"'"
    '''
    cantidad = db.executesql("SELECT SUM(debe) as suma_debe, SUM(haber) as suma_haber  "\
                                 "FROM asiento, cc_empresa "\
                                 "WHERE asiento.cc_empresa_id = cc_empresa.id "\
                                 "AND cc_empresa.num_cc like '"+str(num_cc)+"%'"\
                                 +cadena)
    '''
    cantidad = db.executesql("SELECT SUM(debe) as suma_debe, SUM(haber) as suma_haber  "\
                                 " FROM poliza, asiento, cc_empresa "\
                                 " WHERE asiento.cc_empresa_id = cc_empresa.id "\
                                 " AND poliza.id = asiento.poliza_id "\
                                 " AND poliza.estatus= 3 "\
                                 " AND cc_empresa.num_cc like '"+num_cc+"%'"\
                                 +filtro)
    debe=cantidad[0][0] if cantidad[0][0]!=None else 0.0
    haber=cantidad[0][1] if cantidad[0][1]!=None else 0.0
    if cc_naturaleza_id==2: #Deudora
        importe=haber-debe
    else:
        importe=debe-haber
    return importe

def tabla_balanza():
    filtro = ""
    fecha_final=time.strftime("%Y-%m-%d 23:59:59")
    fecha_inicial=time.strftime("%Y-%m-01 00:00:00")
    tipo_cuentas=request.vars.tipo_cuentas
    if request.vars.fecha_ini:
        fecha_inicial=request.vars.fecha_ini
        filtro += " AND poliza.fecha_usuario >= '"+str(request.vars.fecha_ini) +"'"
    else:
        filtro += " AND poliza.fecha_usuario >= '"+str(fecha_inicial) +"'"
    if request.vars.fecha_fin:
        fecha_final=request.vars.fecha_fin
        filtro += " AND poliza.fecha_usuario <= '"+str(request.vars.fecha_fin) +"'"
    else:
        filtro += " AND poliza.fecha_usuario <= '"+str(fecha_final) +"'"
        
    categories = db.executesql("SELECT node.num_cc, node.descripcion,(COUNT(parent.descripcion) - 1) AS depth, "\
                   "node.id, node.cc_vista_id, node.cc_naturaleza_id "\
                   " FROM cc_empresa AS node , cc_empresa AS parent "\
                   " WHERE node.lft BETWEEN parent.lft AND parent.rgt "\
                   " GROUP BY node.id "\
                   " ORDER BY node.lft;")


    cadena='<div class="table-responsive">'\
	'<table class="table">'\
	'	<thead>'\
	'		<tr>'\
	'			<th style="width:10px;">Op</th>'\
	'			<th>No. cuenta</th>'\
    '			<th>Descripción</th>'\
	'			<th>Saldo Inicial</th>'\
	'			<th>Debe</th>'\
	'			<th>Haber</th>'\
    '			<th>Saldo Final</th>'\
	'		</tr>'\
	'	</thead>'\
	'	<tbody>'

    for cat in categories:
        num_cc=cat[0]
        descripcion=cat[1]
        nivel = cat[2]
        cc_naturaleza_id=cat[5]
        id_padre= ancestor(num_cc)
        if id_padre:
            padre=id_padre.num_cc
        else:
            padre=''

        padre = padre.replace('.', '')
        clase_tr= 'hijo-'+XML(str(padre))+' padre'
        #clase_tr= "child-row "+str(id_padre)+" parent"
        cantidad = db.executesql("SELECT SUM(debe) as suma_debe, SUM(haber) as suma_haber  "\
                                 " FROM poliza, asiento, cc_empresa "\
                                 " WHERE asiento.cc_empresa_id = cc_empresa.id "\
                                 " AND poliza.id = asiento.poliza_id "\
                                 " AND poliza.estatus= 3 "\
                                 " AND cc_empresa.num_cc like '"+num_cc+"%'"\
                                 +filtro)

        importe_inicial=importe_cuenta_balanza(num_cc,cc_naturaleza_id, fecha_inicial)
        importe_final=importe_cuenta_balanza(num_cc,cc_naturaleza_id, fecha_final)
        debe=cantidad[0][0] or 0.0
        haber=cantidad[0][1] or 0.0

        id_row = num_cc
        color=XML(color_nivel(cat[2]))
        padding=XML(str(cat[2]*20))

        display = ''
        if nivel >= 1:
            display = 'none'

        if tipo_cuentas=='con_saldo':
            
            if (cantidad[0][0])!=None or (cantidad[0][1]!=None):
                
                cadena += """<tr id='{}' class='{}' style=color:'{}'>\
                <td><i class='fa fa-plus-circle'></i></td>\
                <td style="padding-left: {}px;">{}</td>\
                <td>{}</td>\
                <td>{}</td>\
                <td>{}</td>\
                <td>{}</td>\
                <td>{}</td>\
                </tr>""".format(XML(num_cc), clase_tr, color,
                        padding, XML(num_cc),
                        XML(descripcion),
                        XML(importe_inicial),
                        XML(debe), 
                        XML(haber),
                        XML(importe_final)
                        )
        else:
            cadena += """<tr id='{}' class='{}' style="color:{}; display:{};">\
            <td><i class='fa fa-plus-circle'></i></td>\
            <td style="padding-left: {}px;">{}</td>\
            <td>{}</td>\
            <td>{}</td>\
            <td>{}</td>\
            <td>{}</td>\
            <td>{}</td>\
            </tr>""".format(XML(id_row), clase_tr, color, display,
                    padding, XML(num_cc), 
                    XML(descripcion),
                    XML(importe_inicial),
                    XML(debe),
                    XML(haber),
                    XML(importe_final),
                    )
            
    cadena+='</tbody></table></div>'

    return XML(cadena)

def balance_general():
    return dict(balance=tabla_balance())

def catalogo_cuentas():
    catalogo = db.executesql("SELECT node.num_cc, node.descripcion,(COUNT(parent.descripcion) - 1) AS depth, "\
                   "node.id, node.cc_vista_id "\
                   "FROM cc_empresa AS node , cc_empresa AS parent "\
                   "WHERE node.lft BETWEEN parent.lft AND parent.rgt "\
                   "GROUP BY node.id "\
                   "ORDER BY node.lft;")
    return catalogo

def tabla_balance():
    categories = catalogo_cuentas()
    nivel=0
    cont=0
    cc_nivel=['','','']
    descrip_nivel=['','','']
    cant_nivel=['','','']
    pasivo_capital=0
    cadena='<table>'
    estilo_negritas='style="font-weight: bold; color: #111640"'
    for cat in categories:
        cantidad = db.executesql("SELECT SUM(debe) as suma_debe, SUM(haber) as suma_haber  "\
                                 " FROM poliza, asiento, cc_empresa "\
                                 " WHERE asiento.cc_empresa_id = cc_empresa.id "\
                                 " AND poliza.id=asiento.poliza_id "\
                                 " AND cc_empresa.num_cc like '"+cat[0]+"%'")
        nivel_cc=cat[2]
        digito=int(cat[0][0])
        if (nivel_cc < 3) and (digito<4):
            num_cc=str(cat[0])
            descrip_cc=cat[1]
            debe_cc=cantidad[0][0] if cantidad[0][0]!=None else 0.0
            haber_cc=cantidad[0][1] if cantidad[0][1]!=None else 0.0
            if num_cc[0]=='1':
                resultado_cc=debe_cc-haber_cc
            else:
                resultado_cc=haber_cc-debe_cc
            if nivel_cc<nivel:
                if nivel_cc==1:
                    cadena+='<tr><td '+estilo_negritas+'>Total de: '+XML(cc_nivel[1])+'</td><td '+estilo_negritas+'>'+XML(descrip_nivel[1])+'</td><td '+estilo_negritas+'>'+XML(cant_nivel[1])+'</td></tr>'
                else:
                    cadena+='<tr><td '+estilo_negritas+'>Total de: '+XML(cc_nivel[0])+'</td><td '+estilo_negritas+'>'+XML(descrip_nivel[0])+'</td><td '+estilo_negritas+'>'+XML(cant_nivel[0])+'</td></tr>'
                    cadena+='<tr><td colspan=3>-</td></tr>'
            if nivel_cc==0:
                if num_cc=='2' or num_cc=='3':
                    pasivo_capital+=resultado_cc
                    if num_cc=='2':
                        cadena+='<tr><td colspan="3" '+estilo_negritas+'>Pasivo y Capital</td></tr>'
                cadena+='<tr><td colspan="3" '+estilo_negritas+'>'+num_cc+' '+XML(descrip_cc)+'</td></tr>'
            elif nivel_cc==1:
                cadena+='<tr><td colspan=3>-</td></tr>'
                cadena+='<tr><td colspan="3" '+estilo_negritas+'>'+num_cc+' '+XML(descrip_cc)+'</td></tr>'
            else:
                cadena+='<tr><td>'+XML(num_cc)+'</td><td>'+XML(descrip_cc)+'</td><td style="text-align:right;">'+XML(resultado_cc)+'</td></tr>'
            nivel=cat[2]
            cant_nivel[nivel_cc]=resultado_cc
            descrip_nivel[nivel_cc]=descrip_cc
            cc_nivel[nivel_cc]=num_cc

    if nivel_cc>0:
        cadena+='<tr><td '+estilo_negritas+'>Total de: '+XML(cc_nivel[1])+'</td><td '+estilo_negritas+'>'+XML(descrip_nivel[1])+'</td><td '+estilo_negritas+'>'+XML(cant_nivel[1])+'</td></tr>'
        cadena+='<tr><td '+estilo_negritas+'>Total de: '+XML(cc_nivel[0])+'</td><td '+estilo_negritas+'>'+XML(descrip_nivel[0])+'</td><td '+estilo_negritas+'>'+XML(cant_nivel[0])+'</td></tr>'
        cadena+='<tr><td '+estilo_negritas+'>Total de: </td><td '+estilo_negritas+'>Pasivo y Capital</td><td '+estilo_negritas+'>'+XML(pasivo_capital)+'</td></tr>'
        cadena+='</table>'
    else:
        cadena+='<tr><td '+estilo_negritas+'>Total de: </td><td '+estilo_negritas+'>Pasivo y Capital</td><td '+estilo_negritas+'>'+XML(pasivo_capital)+'</td></tr>'
        cadena+='</table>'
    return XML(cadena)

def libro_diario():

    filtro = ""

    if request.vars.tipo_poliza_id:
        filtro += " AND tp.id = "+str(request.vars.tipo_poliza_id)
    if request.vars.fecha_ini:
        filtro += " AND p.creada_en >= '"+str(request.vars.fecha_ini) +"'"
    if request.vars.fecha_fin:
        filtro += " AND p.creada_en <= '"+str(request.vars.fecha_fin) +"'"
    if request.vars.concepto_general:
        filtro += " AND p.concepto_general LIKE '%"+ str(request.vars.concepto_general) +"%'"
    if request.vars.num_poliza:
        filtro = " AND p.id = "+ str(request.vars.num_poliza)

    query = "SELECT p.id , tp.nombre AS tipo_poliza, p.creada_en, \
            p.concepto_general, cc.num_cc,cc.descripcion,a.id AS asiento_id, a.concepto_asiento, a.debe, a.haber, p.importe\
            FROM poliza p \
            LEFT JOIN asiento a ON (a.poliza_id = p.id) \
            LEFT JOIN cc_empresa cc ON (a.cc_empresa_id = cc.id)\
            LEFT JOIN tipo_poliza tp ON (p.tipo = tp.id)\
            WHERE p.id > 0 "+ filtro

    query = db.executesql(query, as_dict=True)

    tipo_poliza = db(db.tipo_poliza.id > 0).select(db.tipo_poliza.ALL)

    return dict(datos = query, tipo_poliza= tipo_poliza)


def estado_resultados():
    tabla=''
    nombre_reporte= db(db.reporte.nombre=='estado_resultados').select(db.reporte.descripcion).first()
    if nombre_reporte:
        desc_ingresos= db(db.seccion_reporte.nombre=='ingresos').select(db.seccion_reporte.descripcion).first()
        desc_costos= db(db.seccion_reporte.nombre=='costos').select(db.seccion_reporte.descripcion).first()
        desc_gastos= db(db.seccion_reporte.nombre=='gastos').select(db.seccion_reporte.descripcion).first()
        desc_otros= db(db.seccion_reporte.nombre=='otros').select(db.seccion_reporte.descripcion).first()
        desc_impuestos= db(db.seccion_reporte.nombre=='impuestos').select(db.seccion_reporte.descripcion).first()
        cuentas_ingresos=db( (db.seccion_reporte.nombre=='ingresos')
                            & (db.cuentas_seccion_reporte.seccion_reporte_id==db.seccion_reporte.id )
                            & (db.cc_empresa.id==db.cuentas_seccion_reporte.cc_empresa_id)).select(db.cc_empresa.ALL, groupby=db.cc_empresa.id)
        cuentas_costos=db( (db.seccion_reporte.nombre=='costos')
                            & (db.cuentas_seccion_reporte.seccion_reporte_id==db.seccion_reporte.id )
                            & (db.cc_empresa.id==db.cuentas_seccion_reporte.cc_empresa_id)).select(db.cc_empresa.ALL, groupby=db.cc_empresa.id)
        cuentas_gastos=db( (db.seccion_reporte.nombre=='gastos')
                            & (db.cuentas_seccion_reporte.seccion_reporte_id==db.seccion_reporte.id )
                            & (db.cc_empresa.id==db.cuentas_seccion_reporte.cc_empresa_id)).select(db.cc_empresa.ALL, groupby=db.cc_empresa.id)
        cuentas_otros=db( (db.seccion_reporte.nombre=='otros')
                            & (db.cuentas_seccion_reporte.seccion_reporte_id==db.seccion_reporte.id )
                            & (db.cc_empresa.id==db.cuentas_seccion_reporte.cc_empresa_id)).select(db.cc_empresa.ALL, groupby=db.cc_empresa.id)
        cuentas_impuestos=db( (db.seccion_reporte.nombre=='impuestos')
                            & (db.cuentas_seccion_reporte.seccion_reporte_id==db.seccion_reporte.id )
                            & (db.cc_empresa.id==db.cuentas_seccion_reporte.cc_empresa_id)).select(db.cc_empresa.ALL, groupby=db.cc_empresa.id)
        
        #Obtenemos los datos de las cuentas
        total_ingresos=total_cuentas_er(cuentas_ingresos)
        total_costos=total_cuentas_er(cuentas_costos)
        total_gastos=total_cuentas_er(cuentas_gastos)
        total_otros=total_cuentas_er(cuentas_otros)
        total_impuestos=total_cuentas_er(cuentas_impuestos)
        seccion_ingresos=fila_seccion_er(cuentas_ingresos,total_ingresos)
        seccion_costos=fila_seccion_er(cuentas_costos,total_ingresos)
        seccion_gastos=fila_seccion_er(cuentas_gastos,total_ingresos)
        seccion_otros=fila_seccion_er(cuentas_otros,total_ingresos)
        seccion_impuestos=fila_seccion_er(cuentas_impuestos,total_ingresos)
        utilidad_bruta=dict(actual=0.0,acumulado=0.0)
        utilidad_bruta['actual']=total_ingresos['actual']-total_ingresos['actual']
        utilidad_bruta['acumulado']=total_ingresos['acumulado']-total_ingresos['acumulado']
        utilidad=dict(actual=0.0,acumulado=0.0)
        utilidad['actual']=utilidad_bruta['actual']-total_gastos['actual']
        utilidad['acumulado']=utilidad_bruta['acumulado']-total_gastos['acumulado']
        utilidad_neta=dict(actual=0.0,acumulado=0.0)
        utilidad_neta['actual']=utilidad['actual']-total_otros['actual']+total_impuestos['actual']
        utilidad_neta['acumulado']=utilidad['acumulado']-total_otros['acumulado']+total_impuestos['acumulado']
        #Comienza la tabla
        tabla='<table id="dt_basic" class="table table-striped table-bordered table-hover">'
        #Encabezado
        tabla+='<thead><tr><td>Cuentas</td><td>Este mes</td><td>% de las ventas</td><td>Acum. este mes</td><td>% de las ventas</td></tr></thead>'
        #Etiqueta de ingresos
        tabla+='<tbody>'
        tabla+=cabecera_seccion_er(desc_ingresos)
        tabla+=seccion_ingresos['fila']
        tabla+=utilidad_er(total_ingresos,'Total de '+desc_ingresos.descripcion,total_ingresos)
        tabla+=cabecera_seccion_er(desc_costos)
        tabla+=seccion_costos['fila']
        tabla+=utilidad_er(total_costos,'Total de '+desc_costos.descripcion,total_ingresos)
        tabla+=utilidad_er(utilidad_bruta,'Utilidad bruta',total_ingresos)
        tabla+=cabecera_seccion_er(desc_gastos)
        tabla+=seccion_gastos['fila']
        tabla+=utilidad_er(total_gastos,'Total de '+desc_gastos.descripcion,total_ingresos)
        tabla+=utilidad_er(utilidad,'Utilidades antes de '+desc_otros.descripcion,total_ingresos)
        tabla+=cabecera_seccion_er(desc_otros)
        tabla+=seccion_otros['fila']
        tabla+=utilidad_er(total_otros,'Total de '+desc_otros.descripcion,total_ingresos)
        tabla+=cabecera_seccion_er(desc_impuestos)
        tabla+=seccion_impuestos['fila']
        tabla+=utilidad_er(total_impuestos,'Total de '+desc_impuestos.descripcion,total_ingresos)
        tabla+=utilidad_er(utilidad_neta,'Utilidad Neta',total_ingresos)
        tabla+='</tbody>'
        tabla+='</table>'

    else:
        tabla+='<table><th><tr><td>Configure el reporte en la sección de Configuración</td></tr></th></table>'
    return dict(tabla=XML(tabla))

def utilidad_er(utilidad, desc,total_ingresos):
    porc_actual=(100.0/total_ingresos['actual'])*utilidad['actual'] if total_ingresos['actual'] > 0 else 0.0
    porc_acumulado=(100.0/total_ingresos['acumulado'])*utilidad['acumulado'] if total_ingresos['acumulado'] > 0 else 0.0
    fila='<tr><td>'+XML(desc)+'</td>'\
        +'<td>'+XML(round(utilidad['actual']),2)+'</td>'\
        +'<td>'+XML(round(porc_actual,2))+'</td>'\
        +'<td>'+XML(round(utilidad['acumulado'],2))+'</td>'\
        +'<td>'+XML(round(porc_acumulado,2))
    return XML(fila)

def cabecera_seccion_er(desc):
    cabecera='<tr><td>'+desc.descripcion+'</td><td></td><td></td><td></td><td></td></tr>'
    return XML(cabecera)

def importe_cuenta_er(cuenta, acumulado):
    fecha_actual=time.strftime("%Y-%m-%d 23:59:59")
    mes_actual=time.strftime("%Y-%m-01 00:00:00")
    if acumulado==True:
        cadena=" AND f_asiento <= '"+mes_actual+"'"
    elif acumulado==False:
        cadena=" AND f_asiento between '"+mes_actual+"' and '"+fecha_actual+"'"
    cantidad = db.executesql("SELECT SUM(debe) as suma_debe, SUM(haber) as suma_haber  "\
                                 "FROM asiento, cc_empresa "\
                                 "WHERE asiento.cc_empresa_id = cc_empresa.id "\
                                 "AND cc_empresa.num_cc like '"+str(cuenta.num_cc)+"%'"\
                                 +cadena)
    debe=cantidad[0][0] if cantidad[0][0]!=None else 0.0
    haber=cantidad[0][1] if cantidad[0][1]!=None else 0.0
    if cuenta.cc_naturaleza_id==2: #Deudora
        importe=haber-debe
    else:
        importe=debe-haber
    return importe

def total_cuentas_er(cuentas):
    total_acreedora=dict(actual=0.0,acumulado=0.0)
    total_deudora=dict(actual=0.0,acumulado=0.0)
    total=dict(actual=0.0,acumulado=0.0)
    for cuenta in cuentas:
        actual = importe_cuenta_er(cuenta,False)
        acumulado = importe_cuenta_er(cuenta,True)
        if cuenta.cc_naturaleza_id==1:
            total_acreedora['actual']+=total_acreedora['actual']
            total_acreedora['acumulado']+=total_acreedora['acumulado']
        elif cuenta.cc_naturaleza_id==2:
            total_deudora['actual']+=total_deudora['actual']
            total_deudora['acumulado']+=total_deudora['acumulado']
    total['actual']=total_acreedora['actual']-total_deudora['actual']
    total['acumulado']=total_acreedora['acumulado']-total_deudora['acumulado']
    return dict(actual=total['actual'],acumulado=total['acumulado'])

def seccion_er(cuentas,total_ingresos):
    seccion=[]
    for cuenta in cuentas:
        row=[]
        row.append(cuenta.descripcion)
        actual = importe_cuenta_er(cuenta,False)
        row.append(actual)
        porc_actual=(100.0/total_ingresos['actual'])*actual if actual > 0 else 0.0
        row.append(porc_actual)
        acumulado = importe_cuenta_er(cuenta,True)
        row.append(acumulado)
        porc_acumulado=(100.0/total_ingresos['acumulado'])*acumulado if acumulado > 0 else 0.0
        row.append(porc_acumulado)
        seccion.append(row)
    return seccion

def fila_seccion_er(cuentas,total_ingresos):
    seccion=seccion_er(cuentas,total_ingresos)
    fila=''
    for elemento in seccion:
        fila+='<tr><td>'+XML(elemento[0])+'</td>'\
        +'<td>'+XML(round(elemento[1]),2)+'</td>'\
        +'<td>'+XML(round(elemento[2],2))+'</td>'\
        +'<td>'+XML(round(elemento[3],2))+'</td>'\
        +'<td>'+XML(round(elemento[4],2))
    return dict(fila=fila)

def cuentas_especificas():
    cc_empresa=catalogo_cuentas()
    tabla=''
    return dict(tabla=tabla, cc_empresa=cc_empresa)

def libro_mayor():
    datos=[]
    row = []
    query_asientos = "SELECT a.cc_empresa_id, cc.num_cc, date_part('month',p.fecha_usuario) AS mes, SUM(a.debe) as debe, SUM(a.haber) as haber\
                        FROM asiento a, poliza p, cc_empresa cc\
                        WHERE a.cc_empresa_id = cc.id\
                        AND a.poliza_id = p.id\
                        GROUP BY a.cc_empresa_id, cc.num_cc, date_part('month',p.fecha_usuario)"

    asientos = db.executesql(query_asientos,as_dict=True)

    for a in asientos:
        a['mes']= mes(a['mes'])

    for a in asientos:
        datos.append([cc_mayor(a['num_cc']),a])
        
    return dict(asientos = asientos,datos=datos)

def cc_mayor(num_cc):
    tabla = db['cc_empresa']
    node = db(tabla.num_cc == num_cc).select().first()
    return db( (tabla.lft < node.lft) & (tabla.rgt > node.rgt) ).select(tabla.ALL, orderby=tabla.lft).last()

def mes(mes):
    if mes == 1:
        mes = 'ENE'
    elif mes == 2:
        mes = 'FEB'
    elif mes == 3:
        mes = 'MAR'
    elif mes == 4:
        mes = 'ABR'
    elif mes == 5:
        mes = 'MAY'
    elif mes == 6:
        mes = 'JUN'
    elif mes == 7:
        mes = 'JUL'
    elif mes == 8:
        mes = 'AGO'
    elif mes == 9:
        mes = 'SEP'
    elif mes == 10:
        mes = 'OCT'
    elif mes == 11:
        mes = 'NOV'
    elif mes == 12:
        mes = 'DIC'
    return mes
