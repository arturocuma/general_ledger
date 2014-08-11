"""
from gluon.tools import Auth

class CargaEmpresas(object):

    def __init__(self, db):
        self.db = db
        auth = Auth(db)
        self.user_id = auth.user['id']

    def get_modelos(self):
        return self.user_id
"""


"""
#auth.user['id']
lista = db(
            db.mi_empresa.empresa_id == db.empresa.id
        ).select(
            db.empresa.razon_social
        )

dbs = []

for i in lista:
    dbs.append(DAL(
        'sqlite://{}.sqlite'.format(i.razon_social),
        pool_size=1,
        check_reserved=['all']
        ))

print dbs
"""
