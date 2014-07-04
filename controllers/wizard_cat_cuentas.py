# coding: utf8
# intente algo como

import csv
    
def index(): 
    cc_uno=cat_cuentas_nivel_uno(0)
    cc_dos=cat_cuentas_nivel_dos(0)
    cc_tres=cat_cuentas_nivel_tres(0)
    return dict(cc_uno=cc_uno, cc_dos=cc_dos, cc_tres=cc_tres)

def wiz_cc():
    empresa_id=int(request.vars.empresa_id)
    cc_preconf=int(request.vars.cc_preconf)
    cc_conf=int(request.vars.cc_conf)
    dig_acum=int(request.vars.dig_acum)
    dig_aux=int(request.vars.dig_aux)
    cc_uno=cat_cuentas_nivel_uno(empresa_id)
    cc_dos=cat_cuentas_nivel_dos(empresa_id)
    cc_tres=cat_cuentas_nivel_tres(empresa_id)
    
    if cc_preconf>=1:
        cat_cuentas=cc_uno
    if cc_preconf>=2:
        cat_cuentas=cat_cuentas+cc_dos
    if cc_preconf>=3:
        cat_cuentas=cat_cuentas+cc_tres
    
    db(db.cc_empresa).delete()
    #db(db.sqlite_sequence.name=='cc_empresa').delete()
    db.executesql('delete from sqlite_sequence where name="cc_empresa";')
    #delete from sqlite_sequence where name='your_table';
    db(db.niveles_cc_empresa.empresa_id==empresa_id).delete()
    db.niveles_cc_empresa.insert(empresa_id=empresa_id, niveles=cc_conf+cc_preconf, digitos_cc_acum=dig_acum, digitos_cc_aux=dig_aux)

    campos_cc=['empresa_id','cuenta_padre', 'num_cc','descripcion','nivel','tipo_naturaleza_id', 'tipo_cc_id']

    for cuenta in cat_cuentas:
        dict_cc= dict(zip(campos_cc, cuenta))
        insert_cc=db[db.cc_empresa].insert(**dict_cc)

    mensaje="Catálogo creado"    
    return XML(mensaje)
    
def cat_cuentas_nivel_uno(empresa_id):    
    nivel_uno=[]
    with open('applications/general_ledger/private/cc_nivel_uno.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:        
            row[0]=str(empresa_id)
            nivel_uno.append(row)
    return nivel_uno

def cat_cuentas_nivel_dos(empresa_id):
    nivel_dos=[]
    with open('applications/general_ledger/private/cc_nivel_dos.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:        
            row[0]=str(empresa_id)
            nivel_dos.append(row)
    return nivel_dos

def cat_cuentas_nivel_tres(empresa_id):
    nivel_tres=[]
    with open('applications/general_ledger/private/cc_nivel_tres.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:        
            row[0]=str(empresa_id)
            nivel_tres.append(row)
        return nivel_tres
