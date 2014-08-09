# coding: utf8
# try something like
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

def cc_grid():
    num_cc='1.1'
    nivel='2'
    cc_empresa = hijos_nivel(num_cc, nivel)
    tabla='<table>'
    for cc in cc_empresa:
        tabla+='<tr><td>'+cc[0]+' '+cc[1]+'</td></tr>'
    tabla+='</table>'
    return dict(cc_empresa=XML(tabla))

def cc_grid2():
    cc_empresa = ul_list()
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

def ul_list():
    tipo_cuentas=request.vars.tipo_cuentas
    
    
                                
    categories = db.executesql("SELECT node.num_cc, node.descripcion,(COUNT(parent.descripcion) - 1) AS depth, "\
                   "node.id, node.cc_vista_id "\
                   "FROM cc_empresa AS node , cc_empresa AS parent "\
                   "WHERE node.lft BETWEEN parent.lft AND parent.rgt "\
                   "GROUP BY node.id "\
                   "ORDER BY node.lft;")

   
    cadena='<div class="table-responsive">'\
	'<table class="table table-hover">'\
	'	<thead>'\
	'		<tr>'\
	'			<th>Op</th>'\
	'			<th>No. cuenta</th>'\
	'			<th>Descripción</th>'\
	'			<th>Debe</th>'\
	'			<th>Haber</th>'\
	'		</tr>'\
	'	</thead>'\
	'	<tbody>'
    
    for cat in categories:
        id_padre= ancestor(cat[0])
        if id_padre:
            padre=id_padre.num_cc
        else:
            padre=''
        
        padre = padre.replace('.', '')
        clase_tr= 'hijo-'+XML(str(padre))+' padre'
        #clase_tr= "child-row "+str(id_padre)+" parent"
        cantidad = db.executesql("SELECT SUM(debe) as suma_debe, SUM(haber) as suma_haber  "\
                                 "FROM asiento, cc_empresa "\
                                 "WHERE asiento.cc_empresa_id = cc_empresa.id "\
                                 "AND cc_empresa.num_cc like '"+cat[0]+"%'")
        
        id_row = cat[0].replace('.', '')
        padding=XML(str(cat[2]*20))
        if tipo_cuentas=='con_saldo':
            if (cantidad[0][0])!=None or (cantidad[0][1]!=None):
                cadena+='<tr id="'+XML(id_row)+'" class="'+clase_tr+'"><td><i class="fa fa-plus-circle"></i></td><td style="padding-left: '+padding+'px;">'+XML(cat[0])+'</td><td>'+XML(cat[1])+'</td><td>'+XML(str(cantidad[0][0]))+'</td><td>'+XML(str(cantidad[0][1]))+'</td></tr>'
        else:
            cadena+='<tr id="'+XML(id_row)+'" class="'+clase_tr+'"><td><i class="fa fa-plus-circle"></i></td><td style="padding-left: '+padding+'px;">'+XML(cat[0])+'</td><td>'+XML(cat[1])+'</td><td>'+XML(str(cantidad[0][0]))+'</td><td>'+XML(str(cantidad[0][1]))+'</td></tr>'
        
    cadena+='</tbody></table></div>'
   
    return XML(cadena)

def balance_general():
    balance = ul_list_balance()
    return dict(balance=balance)

def ul_list_balance():
    categories = db.executesql("SELECT node.num_cc, node.descripcion,(COUNT(parent.descripcion) - 1) AS depth, "\
                   "node.id, node.cc_vista_id "\
                   "FROM cc_empresa AS node , cc_empresa AS parent "\
                   "WHERE node.lft BETWEEN parent.lft AND parent.rgt "\
                   "GROUP BY node.id "\
                   "ORDER BY node.lft;")
    nivel=0
    cont=0
    cc_nivel=['','','']
    descrip_nivel=['','','']
    cant_nivel=['','','']
    pasivo_capital=0
    cadena='<table>'
    estilo_negritas='style="font-weight: bold"'
    for cat in categories:
        cantidad = db.executesql("SELECT SUM(debe) as suma_debe, SUM(haber) as suma_haber  "\
                                 "FROM asiento, cc_empresa "\
                                 "WHERE asiento.cc_empresa_id = cc_empresa.id "\
                                 "AND cc_empresa.num_cc like '"+cat[0]+"%'")
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
                cadena+='<tr><td>'+XML(num_cc)+'</td><td>'+XML(descrip_cc)+'</td><td>'+XML(resultado_cc)+'</td></tr>'
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
