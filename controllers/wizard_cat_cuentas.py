# coding: utf8
# intente algo como

import csv
    
def index(): 
    cc_uno=cat_cuentas_nivel_uno(0)
    cc_dos=cat_cuentas_nivel_dos(0)
    cc_tres=cat_cuentas_nivel_tres(0)
    return dict(cc_uno=cc_uno, cc_dos=cc_dos, cc_tres=cc_tres)

def form_confirmar(empresa_id,cc_preconf, cc_conf, dig_acum, dig_aux):
    cadena_url="crear_cuentas?empresa_id="+str(empresa_id)+"&cc_preconf="+str(cc_preconf)+"&cc_conf="+str(cc_conf)+"&dig_acum="+str(dig_acum)+"&dig_aux="+str(dig_aux)
    confirmar = (DIV(
                     DIV (
                         (DIV (XML('Confirma que desea crear el catálogo de cuentas con: <br>'), _class="cell")),
                    _class="fila_form"
                    ),
                     DIV (
                         (DIV (XML('Niveles preconfigurados: '),_class="cell")),
                         (DIV (XML(cc_preconf), _class="cell")),
                    _class="fila_form"
                    ),
                     DIV (
                         (DIV (XML('Niveles a configurar: '),_class="cell")),
                         (DIV (XML(cc_conf), _class="cell")),
                    _class="fila_form"
                    ),
                     DIV (
                         (DIV (XML('Dígitos en los niveles de cuentas mayores y acumulativas: '),_class="cell")),
                         (DIV (XML(dig_acum), _class="cell")),
                    _class="fila_form"
                    ),
                    DIV (
                         (DIV (XML('Dígitos en los niveles de cuentas de detalle: '),_class="cell")),
                         (DIV (XML(dig_aux), _class="cell")),
                    _class="fila_form"
                    ),
                    DIV (
                         (DIV ( A(INPUT ( _type="button",_name="cancelar", _id="cancelar", _value="Cancelar"), callback=URL('wizard_cat_cuentas','index')),_class="cell")),
                         (DIV ( A(INPUT ( _type="button",_name="confirmar", _id="confirmar", _value="Confirmar"), callback=URL('wizard_cat_cuentas',cadena_url)),_class="cell")),
                         _class="fila_form"
                         ),
                    _class="table"
                    )
                 )
    return confirmar
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
    db.executesql('delete from sqlite_sequence where name="cc_empresa";')
    db(db.niveles_cc_empresa.empresa_id==empresa_id).delete()
    db.niveles_cc_empresa.insert(empresa_id=empresa_id, niveles=cc_conf+cc_preconf, digitos_cc_acum=dig_acum, digitos_cc_aux=dig_aux)
    campos_cc=['empresa_id','cuenta_padre', 'num_cc','descripcion','nivel','tipo_naturaleza_id', 'tipo_cc_id']
    for cuenta in cat_cuentas:
        dict_cc= dict(zip(campos_cc, cuenta))
        insert_cc=db[db.cc_empresa].insert(**dict_cc)
    #redirect(URL('default','index'))
    return

def crear_cuentas():
    empresa_id=int(request.vars.empresa_id)
    cc_preconf=int(request.vars.cc_preconf)
    cc_conf=int(request.vars.cc_conf)
    dig_acum=int(request.vars.dig_acum)
    dig_aux=int(request.vars.dig_aux)
    confirmar= form_confirmar(empresa_id,cc_preconf, cc_conf, dig_acum, dig_aux)
    return XML(confirmar)
    
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
