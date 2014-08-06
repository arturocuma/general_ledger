# coding: utf8
# try something like
def index(): return dict(message="hello from reportes.py")

def sumas():
    categories = db((db.cc_empresa.empresa_id==1)).select(db.cc_empresa.ALL, db.asiento.ALL, left=db.asiento.on(db.cc_empresa.id==db.asiento.cc_empresa_id), orderby=db.cc_empresa.lft)

    rgt = []
    tree = []
    for cat in categories:
        if len(rgt) > 0:
            if rgt[-1] > cat.cc_empresa.rgt:
                # open UL
                pass
            while rgt[-1] < cat.cc_empresa.rgt:
                rgt.pop()
                if len(rgt) == 0:
                    break
        branch = UL(_class="branch")
        p=branch
        for i in range(len(rgt)):
            child = UL(_class="branch_leaf")
            p.append(LI(child, _class="leaf"))
            p=child
        p.append(LI(A(cat.cc_empresa.num_cc+' '+cat.cc_empresa.descripcion+(str(cat.asiento.debe) if cat.asiento.debe else '0.0')+(str(cat.asiento.haber) if cat.asiento.haber else '0.0'), _href='/'+cat.cc_empresa.num_cc), _class="leaf",))
        tree.append(branch)   
        rgt.append(cat.cc_empresa.rgt)
    seed = DIV(_class="root")
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

    return dict(message=seed)
