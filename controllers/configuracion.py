# coding: utf8
# intente algo como
def index(): return dict(message="hello from configuracion/reportes.py")
def estado_resultados():
    cc_empresa = db.executesql("SELECT node.num_cc, node.descripcion,(COUNT(parent.descripcion) - 1) AS depth, "\
                   "node.id, node.cc_vista_id "\
                   "FROM cc_empresa AS node , cc_empresa AS parent "\
                   "WHERE node.lft BETWEEN parent.lft AND parent.rgt "\
                   "GROUP BY node.id "\
                   "ORDER BY node.lft;")
    
    return dict(cc_empresa=cc_empresa)
