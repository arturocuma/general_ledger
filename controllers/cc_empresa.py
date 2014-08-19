# coding: utf8
(auth.user or request.args(0) == 'login') or redirect(URL('default', 'user', args='login'))

import csv

if session.instancias:
    db = empresas.dbs[int(session.instancias)]

def index():
    tipo="config"
    empresa_id = request.args(0)

    if empresa_id:
        session.instancias = empresa_id
        
    cc_empresa = ul_list(tipo, empresa_id)
    return dict(cc_empresa = cc_empresa)

def ancestor(num_cc):
    tabla = db['cc_empresa']
    node = db(tabla.num_cc == num_cc).select().first()
    return db( (tabla.lft < node.lft) & (tabla.rgt > node.rgt) ).select(tabla.num_cc, orderby=tabla.lft).last()

def cc_wizard():
    tipo="wizard"
    empresa_id = request.vars.empresa_id
    cc_empresa = ul_list(tipo, empresa_id)
    return dict(cc_empresa=cc_empresa)

##@auth.requires_permission('cc_grid')
def cc_grid2():
    tipo="grid"
    cc_empresa = ul_list2()
    return dict(cc_empresa=cc_empresa)

def cc_grid():
    tipo="config"
    empresa_id=int(session.instancias)
    cc_empresa = ul_list(tipo, empresa_id)
    return dict(cc_empresa=cc_empresa)

def ul_list2():
    tipo_cuentas=request.vars.tipo_cuentas

    categories = db.executesql("SELECT node.num_cc, node.descripcion,(COUNT(parent.descripcion) - 1) AS depth, "\
                   "node.id, node.cc_vista_id "\
                   "FROM cc_empresa AS node , cc_empresa AS parent "\
                   "WHERE node.lft BETWEEN parent.lft AND parent.rgt "\
                   "GROUP BY node.id "\
                   "ORDER BY node.lft;")


    cadena='<div class="table-responsive">'\
	'<table class="table">'\
	'	<thead>'\
	'		<tr>'\
	'			<th style="width:10px;">Op</th>'\
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

        id_row = cat[0] #.replace('.', '')
        color=XML(color_nivel(cat[2]))
        padding=XML(str(cat[2]*20))
        if tipo_cuentas=='con_saldo':
            if (cantidad[0][0])!=None or (cantidad[0][1]!=None):
                cadena+='<tr id="'+XML(id_row)+'" class="'+clase_tr+'" style="color:'+color+'"><td><i class="fa fa-plus-circle"></i></td><td style="padding-left: '+padding+'px;">'+XML(cat[0])+'</td><td>'+XML(cat[1])+'</td><td>'+XML(str(cantidad[0][0]))+'</td><td>'+XML(str(cantidad[0][1]))+'</td></tr>'
        else:
            cadena+='<tr id="'+XML(id_row)+'" class="'+clase_tr+'" style="color:'+color+'"><td><i class="fa fa-plus-circle"></i></td><td style="padding-left: '+padding+'px;">'+XML(cat[0])+'</td><td>'+XML(cat[1])+'</td><td>'+XML(str(cantidad[0][0]))+'</td><td>'+XML(str(cantidad[0][1]))+'</td></tr>'

    cadena+='</tbody></table></div>'
    cadena=XML(cadena)
    return cadena


def ul_list(tipo, empresa_id):

    db = empresas.dbs[int(empresa_id)]

    cadena=''
    if tipo=='wizard':
        empresa_id = empresa_id
        cadena='<div class="tree well"><ul>'
    elif tipo=='grid':
        empresa_id = empresa_id
        cadena='<div class="tree"><ul>'
    else:
        empresa_id = empresa_id
        cadena='<div class="tree"><ul>'
        
    categories = db.executesql("SELECT node.num_cc, node.descripcion,\
                   (COUNT(parent.descripcion) - 1) AS depth,\
                   node.id, node.cc_vista_id\
                   FROM cc_empresa AS node, cc_empresa AS parent\
                   WHERE node.lft BETWEEN parent.lft AND parent.rgt\
                   GROUP BY node.id\
                   ORDER BY node.lft;")
    algo="(SUM(asiento.debe)/COUNT(parent.descripcion)) as cantidad "

    seed = DIV(_class="tree well")
    child = UL()
    seed.append(UL())
    n=0

    for cat in categories:
        cantidad = db.executesql("SELECT SUM(debe) as suma_debe, SUM(haber) as suma_haber  "\
                                 "FROM asiento, cc_empresa "\
                                 "WHERE asiento.cc_empresa_id = cc_empresa.id "\
                                 "AND cc_empresa.num_cc like '"+cat[0]+"%'")
        if cat[2]>n:
            cadena+='<ul><li>'
        elif cat[2]==n:
            if n>0:
                cadena+='</li><li>'
            else:
                cadena+='<li>'
        else:
            for i in range(cat[2],n):
                cadena+='</li></ul>'
            cadena+='<li>'

        if tipo=="config":
            cadena+='<span><i class="fa fa-minus-circle"></i></span> '
            cadena+= '<div class="btn-group"><button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">'+cat[0]+' '+cat[1]+' <div class="fa fa-caret-down"></div></button><ul class="dropdown-menu" role="menu"><div class="menu-boton"><a href="javascript:editar_cuenta('+str(cat[3])+')" >Editar</a></div> <div class="menu-boton"><a href="javascript:crear_cuenta('+str(cat[3])+','+str(cat[4])+')">Crear Sub-cuenta</a></div></ul></div>'
        elif tipo=="wizard":
            cadena+='<span><i class="fa fa-minus-circle"></i> '+cat[0]+' '+cat[1]+'</span> '
        elif tipo=="grid":
            cadena+='<span><i class="fa fa-minus-circle"></i><div class="row_grid"><div class="cell_grid"></div><div class="cell_grid">   '+cat[0]+' </div><div class="cell_grid"> '+cat[1]+' </div><div class="cell_grid"> '+str(cantidad[0][0]) +' </div><div class="cell_grid">'+str(cantidad[0][1])+'</div>  </div></span> '
        n=cat[2]
    cadena+='</li></ul></div>'
    cadena=XML(cadena)
    return cadena


def ul_list_back():
    categories = db(db.cc_empresa.id>0).select(db.cc_empresa.ALL, orderby=db.cc_empresa.lft)

    rgt = []
    tree = []
    for cat in categories:
        if len(rgt) > 0:
            if rgt[-1] > cat.rgt:
                # open UL
                pass
            while rgt[-1] < cat.rgt:
                rgt.pop()
                if len(rgt) == 0:
                    break
        branch = UL(_class="branch")
        p=branch
        for i in range(len(rgt)):
            child = UL(_class="branch_leaf")
            p.append(LI(child, _class="leaf"))
            p=child
        p.append(LI(A(cat.num_cc+' '+cat.descripcion, _href='/'+cat.num_cc), _class="leaf",))
        tree.append(branch)
        rgt.append(cat.rgt)
    seed = DIV(_class="tree well")
    for branch in tree:
        seed.append(DIV(branch, _class="root_branch"))
    seed.components.extend([XML("""
        <style>
        .branch {
            padding: 0;
            margin: 0;
            padding-left: 10px;
            list-style-type: none;
        }
        .branch_leaf {
            padding: 0;
            margin: 0;
            padding-left: 20px;
            list-style-type: none;
        }
        .leaf {
            list-style-type: none;
        }

        </style>
                """)])

    return seed


def ancestors(num_cc, *fields):
    tabla = db['cc_empresa']
    node = db(tabla.num_cc == num_cc).select().first()
    return db( (tabla.lft <= node.lft) & (tabla.rgt >= node.rgt) ).select(tabla.ALL, orderby=tabla.lft, *fields)


def descendants(num_cc, *fields):
    tabla = db['cc_empresa']
    node = db(tabla.num_cc == num_cc).select().first()
    return db( (tabla.lft >= node.lft) & (tabla.rgt <= node.rgt) ).select(tabla.ALL, orderby=tabla.lft, *fields)


def add_node(
        padre_id=None,
        num_cc=None,
        descripcion=None,
        clave_sat=None,
        cc_naturaleza_id=None,
        cc_vista_id=None
        ):

    empresa_id = request.vars.empresa_id
    db = empresas.dbs[int(empresa_id)]
    
    tabla = db['cc_empresa']

    if padre_id:
        if isinstance(padre_id, int):
            padre = db(tabla.id == padre_id).select().first()
        else:
            padre = db(tabla.num_cc == padre_id).select().first()

        db(tabla.rgt >= padre.rgt).update(rgt=tabla.rgt+2)
        db(tabla.lft >= padre.rgt).update(lft=tabla.lft+2)

        node_id = tabla.insert(
                num_cc=num_cc,
                descripcion=descripcion,
                clave_sat=clave_sat,
                cc_naturaleza_id = cc_naturaleza_id,
                cc_vista_id = cc_vista_id,
                lft=padre.rgt,
                rgt=padre.rgt+1
                )
    else:
        top = db(tabla.lft > 0).select(orderby=tabla.rgt).last()
        if top:
            node_id = tabla.insert(
                    num_cc=num_cc,
                    descripcion=descripcion,
                    clave_sat=clave_sat,
                    cc_naturaleza_id=cc_naturaleza_id,
                    cc_vista_id=cc_vista_id,
                    lft=top.rgt+1,
                    rgt=top.rgt+2
                    )
        else:
            node_id = tabla.insert(
                    num_cc = num_cc,
                    descripcion = descripcion,
                    clave_sat = clave_sat,
                    cc_naturaleza_id = cc_naturaleza_id,
                    cc_vista_id = cc_vista_id,
                    lft = 1,
                    rgt = 2
                    )
    return node_id


def delete_node(num_cc):
    # Se elimina el nodo y también sus ramas
    tabla = db['cc_empresa']
    node = db(tabla.num_cc == num_cc).select().first()
    if node:
        children = db( (tabla.lft >= node.lft) & (tabla.rgt <= node.rgt) )

        diff = node.rgt - node.lft + 1
        rgt = node.rgt
        lft = node.lft

        children.delete() #se eliminan los hijos
        db(tabla.id == node.id).delete() #se elimina el nodo deseado

        db(tabla.lft > rgt).update(lft=tabla.lft - diff)
        db(tabla.rgt > rgt).update(rgt=tabla.rgt - diff)
        return True
    return False


def cat_cuentas_sat(empresa_id,cc_preconf):
    cc_sat=[]
    if cc_preconf=='1':
        archivo='cuentas_sat'
    else:
        archivo='cuentas_sat_nivel_uno'

    with open('applications/general_ledger/private/'+archivo+'.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            row[0]=str(empresa_id)
            cc_sat.append(row)

    return cc_sat

def cat_cuentas_personal(empresa_id,archivo):
    cc_personal=[]
    file = archivo
    reader = csv.reader(file)
    for row in reader:
        row[0]=str(empresa_id)
        cc_personal.append(row)
    return cc_personal

def wiz_cc():

    empresa_id = request.vars.empresa_id
    db_ = empresas.dbs[int(empresa_id)]

    tabla = db_['cc_empresa']
    cc_preconf = request.vars.cc_preconf
    if request.vars.csvfile != None:
        cc_sat=[]
        file = request.vars.csvfile.file
        reader = csv.reader(file)
        for row in reader:
            row[0]=str(empresa_id)
            cc_sat.append(row)
    else:
        cc_sat = cat_cuentas_sat(empresa_id, cc_preconf)

    db_(db_.cc_vista).delete()
    db_.executesql('alter sequence cc_vista_id_seq restart with 1')
    db_.cc_vista.insert(nombre = 'ACUMULATIVA')
    db_.cc_vista.insert(nombre = 'DETALLE')

    db_(db_.cc_naturaleza).delete()
    db_.executesql('alter sequence cc_naturaleza_id_seq restart with 1')
    db_.cc_naturaleza.insert(nombre = 'ACREEDORA')
    db_.cc_naturaleza.insert(nombre = 'DEUDORA')
    db_.cc_naturaleza.insert(nombre = 'CAPITAL')
    db_.cc_naturaleza.insert(nombre = 'RESULTADO')

    db_(db_.tipo_poliza).delete()
    db_.executesql('alter sequence tipo_poliza_id_seq restart with 1')
    db_.tipo_poliza.insert(nombre = 'INGRESO')
    db_.tipo_poliza.insert(nombre = 'EGRESO')
    db_.tipo_poliza.insert(nombre = 'DIARIO')

    db_(db_.misc).delete()
    db_.executesql('alter sequence misc_id_seq restart with 1')
    db_.misc.insert(consecutivo_polizas = 0)

    db_(db_.estatus_poliza).delete()
    db_.executesql('alter sequence estatus_poliza_id_seq restart with 1')
    db_.estatus_poliza.insert(nombre = 'EN REVISIÓN')
    db_.estatus_poliza.insert(nombre = 'REVISADA')
    db_.estatus_poliza.insert(nombre = 'APLICADA')

    for cuenta in cc_sat:

        num_cc = cuenta[1]
        len_num_cc = len(num_cc)

        if len_num_cc > 1:
            num_cc_i = num_cc[::-1]
            ultimo_punto = num_cc_i.find(".")
            num_cc = num_cc[:-(ultimo_punto+1)]
            padre_id = int(db_(tabla.num_cc == num_cc).select().first().id)
        else:
            padre_id = None

        add_node(padre_id, str(cuenta[1]), str(cuenta[2]),
                str(cuenta[3]), cuenta[4], cuenta[5])
    
    redirect(URL('index',args=[empresa_id]))
    return


def crear_cc(form):
    if form.record:
        form.vars.num_cc = form.vars.num_cc
    elif (form.vars.num_cc != ''):
        empresa_id=3
        niveles_cc_empresa=db(db.niveles_cc_empresa.empresa_id==empresa_id).select()
        niveles_cc=niveles_cc_empresa[0]
        if form.vars.tipo_cc_id=='1':#Acumulativa
            num_niv=int(niveles_cc['digitos_cc_acum'])
        elif form.vars.tipo_cc_id=='2':#Auxiliar
            num_niv=int(niveles_cc['digitos_cc_aux'])

        num_cc= form.vars.num_cc
        str(num_cc).zfill(num_niv)

        form.vars.num_cc = form.vars.cuenta_padre+'.'+ num_cc
    return

def listar():
    db.cc_empresa.num_cc.represent = lambda value, row: DIV(value if value!='' else '-', _class='num_cc', _id=str(row.id)+'.num_cc')
    form = SQLFORM.smartgrid(db.cc_empresa,
                            onvalidation = crear_cc,
                            linked_tables=['empresa'])
    return dict(form=form)

def actualiza_cc_empresa():
    id, column = request.post_vars.id.split('.')
    value = request.post_vars.value
    db(db.cc_empresa.id == id).update(**{column:value})
    return value

@auth.requires_login()
def crear_cuenta():
    if request.vars.num_cc_padre:
        cc_empresa=db(db.cc_empresa.id==request.vars.num_cc_padre).select(db.cc_empresa.ALL)
    else:
        cc_empresa=db(db.cc_empresa).select(db.cc_empresa.ALL)
    cc_vista=db(db.cc_vista).select(db.cc_vista.ALL)
    cc_naturaleza=db(db.cc_naturaleza).select(db.cc_naturaleza.ALL)

    msg=""

    if request.vars.num_cc:
        empresa_id = 1
        padre_id=int(request.vars.num_cc_padre)
        num_cc=request.vars.num_cc
        descripcion=request.vars.descripcion
        clave_sat=""
        naturaleza_id=int(request.vars.cc_naturaleza_id)
        vista_id = int(request.vars.cc_vista_id)
        msg = 'Cuenta Creada'
        add_node(padre_id, empresa_id, num_cc, descripcion, clave_sat, naturaleza_id, vista_id)
        redirect(URL('index'))

    return dict(cc_empresa=cc_empresa,cc_vista=cc_vista,cc_naturaleza=cc_naturaleza, msg=msg)


def editar_cuenta():
    db.cc_empresa.lft.writable=False
    db.cc_empresa.lft.readable=False
    db.cc_empresa.rgt.writable=False
    db.cc_empresa.rgt.readable=False
    form=crud.update(db.cc_empresa, request.vars.id)
    if request.vars.num_cc:
        redirect(URL('index'))
    return dict(form=form)


def obtener_empresa(usuario_id):
    empresa_id=1
    return empresa_id


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
