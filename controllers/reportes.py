# coding: utf8
# try something like
def index(): return dict(message="hello from reportes.py")

def sumas():
    query = (db.cc_empresa.id>0) & (db.cc_empresa.empresa_id==db.empresa.id) & (db.empresa.id==1)
    return dict(message=query)
