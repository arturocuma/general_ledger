# coding: utf8
# try something like
import csv

def index():
    #nodo_id = add_node('','','1','ACTIVO','','')
    #nodo_id = add_node('1','','1.1','ACTIVO CIRCULANTE','','')
    #nodo_id = add_node('1.1','','1.1.1','BANCO','','')
    #nodo_id = add_node('1.1.1','','1.1.1.1','CAJA','','')
    #nodo_id = add_node('1.1.1.1','','1.1.1.1.1','CHICA','','')
    #nodo_id = add_node('','','2','PASIVO','','')
    #nodo_id = add_node('2','','2.1','PASIVO CIRCULANTE','','')
    #nodo_id = add_node('1.1.1.1','','1.1.1.1.2','GENERAL','','')
    #nodo_id = add_node('1','','1.2','NO CIRCULANTE','','')

    #print delete_node('1.1.1.1')
    """
    XXX = db.executesql('SELECT replace(substr(quote(zeroblob(((COUNT(parent.descripcion) - 1) + 1) / 2)), 3, (COUNT(parent.descripcion) - 1) ), "0", "  ") || node.num_cc || node.descripcion AS descripcion \
                                    FROM cc_empresa AS node, cc_empresa AS parent \
                                    WHERE node.lft BETWEEN parent.lft AND parent.rgt \
                                    GROUP BY node.num_cc \
                                    ORDER BY node.lft;')
    for x in XXX:
        print x[0]
    """
    cc_empresa = ul_list()
    return dict(cc_empresa=cc_empresa)


def anidar_lista(lista,cat,indice_ant, indice, cont):
    if isinstance(lista, list):
        p=len(lista)-1
    else:
        p=0
        
    if cont<indice:
        if p>0:
            anidar_lista(lista[p],cat, indice_ant,indice, cont+1)
    else:
        if indice > indice_ant:
            lista = UL(LI(SPAN(I(_class="icon-minus-sign"),cat[0]+' '+cat[1]+' '+str(cat[2]))))
            return lista
        else :
            lista=LI(SPAN(I(_class="icon-minus-sign"),cat[0]+' '+cat[1]+' '+str(cat[2])))
            return lista
            
def ul_list():
    categories = db.executesql("SELECT node.num_cc, node.descripcion, (COUNT(parent.descripcion) - 1) AS depth "\
                   "FROM cc_empresa AS node, cc_empresa AS parent "\
                   "WHERE node.lft BETWEEN parent.lft AND parent.rgt "\
                   "GROUP BY node.num_cc "\
                   "ORDER BY node.lft;")

   
    seed = DIV(_class="tree well")
    child = UL()
    seed.append(UL())
    n=0
    cadena='<div class="tree well"><ul>'
    for cat in categories:
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
        cadena+='<span icon-minus-sign>'+cat[0]+' '+cat[1]+'</span>'    
        n=cat[2]
    cadena+=cadena+'</li></ul></div>'
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

    #print seed
    return seed

def ancestors(num_cc, *fields):
    tabla = db['cc_empresa']
    node = db(tabla.num_cc == num_cc).select().first()
    return db( (tabla.lft <= node.lft) & (tabla.rgt >= node.rgt) ).select(tabla.ALL, orderby=tabla.lft, *fields)

def descendants(num_cc, *fields):
    tabla = db['cc_empresa']
    node = db(tabla.num_cc == num_cc).select().first()
    return db( (tabla.lft >= node.lft) & (tabla.rgt <= node.rgt) ).select(tabla.ALL, orderby=tabla.lft, *fields)


def add_node(padre_id=None, empresa_id=None, num_cc=None, descripcion=None, clave_sat=None, cc_naturaleza_id=None, cc_vista_id=None):
    tabla = db['cc_empresa']
    print padre_id

    if padre_id:
        if isinstance(padre_id, int):
            padre = db(tabla.id == padre_id).select().first()
        else:
            padre = db(tabla.num_cc == padre_id).select().first()

        db(tabla.rgt >= padre.rgt).update(rgt=tabla.rgt+2)
        db(tabla.lft >= padre.rgt).update(lft=tabla.lft+2)
        node_id = tabla.insert(empresa_id=empresa_id, num_cc=num_cc, descripcion=descripcion, clave_sat=clave_sat,cc_naturaleza_id=cc_naturaleza_id, cc_vista_id=cc_vista_id, lft=padre.rgt, rgt=padre.rgt+1)
    else:
        top = db(tabla.lft > 0).select(orderby=tabla.rgt).last()
        if top:
            node_id = tabla.insert(empresa_id=empresa_id, num_cc=num_cc, descripcion=descripcion, clave_sat=clave_sat, cc_naturaleza_id=cc_naturaleza_id, cc_vista_id=cc_vista_id, lft=top.rgt+1, rgt=top.rgt+2)
        else:
            node_id = tabla.insert(empresa_id=empresa_id, num_cc=num_cc, descripcion=descripcion, clave_sat=clave_sat, cc_naturaleza_id=cc_naturaleza_id, cc_vista_id=cc_vista_id, lft=1, rgt=2)
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

def cat_cuentas_sat(empresa_id):
    cc_sat=[]
    with open('applications/general_ledger/private/cuentas_sat.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            row[0]=str(empresa_id)
            cc_sat.append(row)
    return cc_sat

def wiz_cc():
    tabla = db['cc_empresa']
    #empresa_id=int(request.vars.empresa_id)
    empresa_id=1
    cc_sat=cat_cuentas_sat(empresa_id)

    db(db.cc_empresa).delete()
    db.executesql('delete from sqlite_sequence where name="cc_empresa";')

    campos_cc=['empresa_id','num_cc','descripcion','clave_sat','cc_naturaleza_id', 'cc_vista_id','nivel', 'lft','rgt']
    for cuenta in cc_sat:
        num_cc=cuenta[1]
        print num_cc
        len_num_cc=len(num_cc)
        if len_num_cc>1:
            num_cc_i=num_cc[::-1]
            ultimo_punto = num_cc_i.find(".")
            num_cc = num_cc[:-(ultimo_punto+1)]
            padre = db(tabla.num_cc == num_cc).select().first()
            padre_id=padre.id
            padre_id=int(padre_id)
        else:
            padre_id=None


        add_node(padre_id, cuenta[0], str(cuenta[1]), str(cuenta[2]),str(cuenta[3]), cuenta[4], cuenta[5])
    return

    db(db.cc_empresa).delete()
    db.executesql('delete from sqlite_sequence where name="cc_empresa";')

    campos_cc=['empresa_id','num_cc','descripcion','clave_sat','cc_naturaleza_id', 'cc_vista_id','nivel', 'lft','rgt']
    for cuenta in cc_sat:
        num_cc=cuenta[1]
        print num_cc
        len_num_cc=len(num_cc)
        if len_num_cc>1:
            num_cc_i=num_cc[::-1]
            ultimo_punto = num_cc_i.find(".")
            num_cc = num_cc[:-(ultimo_punto+1)]
            padre = db(tabla.num_cc == num_cc).select().first()
            padre_id=padre.id
            padre_id=int(padre_id)
        else:
            padre_id=None


        add_node(padre_id, cuenta[0], str(cuenta[1]), str(cuenta[2]),str(cuenta[3]), cuenta[4], cuenta[5])
    return

def crear_cc(form):
    if form.record:
        form.vars.num_cc = form.vars.num_cc
    elif (form.vars.num_cc != ''):
        empresa_id=1
        niveles_cc_empresa=db(db.niveles_cc_empresa.empresa_id==empresa_id).select()
        niveles_cc=niveles_cc_empresa[0]
        if form.vars.tipo_cc_id=='1':#Acumulativa
            num_niv=int(niveles_cc['digitos_cc_acum'])
        elif form.vars.tipo_cc_id=='2':#Auxiliar
            num_niv=int(niveles_cc['digitos_cc_aux'])

        num_cc= form.vars.num_cc
        str(num_cc).zfill(num_niv)

        form.vars.num_cc = form.vars.cuenta_padre+'.'+ num_cc
        print form.vars
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

def crear_cuenta():
    cc_empresa=db(db.cc_empresa).select(db.cc_empresa.ALL)
    cc_vista=db(db.cc_vista).select(db.cc_vista.ALL)
    cc_naturaleza=db(db.cc_naturaleza).select(db.cc_naturaleza.ALL)

    msg="Nada"

    if request.vars.num_cc:
        empresa_id = 1
        padre_id=int(request.vars.num_cc_padre)
        num_cc=request.vars.num_cc
        descripcion=request.vars.descripcion
        clave_sat=""
        naturaleza_id=request.vars.cc_naturaleza_id
        vista_id = request.vars.cc_vista_id
        msg = 'Cuenta Creada'

        #add_node(padre_id, empresa_id, num_cc, descripcion, clave_sat, naturaleza_id, vista_id)

    return dict(cc_empresa=cc_empresa,cc_vista=cc_vista,cc_naturaleza=cc_naturaleza, msg=msg)
