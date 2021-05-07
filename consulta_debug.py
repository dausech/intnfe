from pynfe.processamento.comunicacao import ComunicacaoSefaz
import requests
import requests.exceptions
import logging
import configparser
from lxml import etree
#import psycopg2
import datetime 


# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client    
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

cfg = configparser.ConfigParser()
cfg.read('config.ini')
CERT = cfg.get("geral","cert_pfx")
SENHA = cfg.get("geral","cert_pwd")   
HOMOLOG = cfg.getboolean("geral","homologacao")  

def get_connection():
    try:
        connection = psycopg2.connect(user = "nfeadm",
                                      password = "P3nnNfe$",
                                      host = "10.1.15.109",
                                      port = "5432",
                                      database = "nfe")
        
        return connection
    except:
        print('Erro conectando ao BD.')                                   
        return None

def get_cursor(connection):
    try:
        cursor = connection.cursor()
        return cursor                           
    except:
        print('Erro conectando ao BD.')                                   
        return None

def consulta_db(uf, ie, data):        
    sql = "select retorno from consulta_sefaz where cod_uf = %s and nro_ie = %s and dta_consulta = %s"    
    cursor.execute(sql, (uf,ie,data,))
    rs = cursor.fetchone()
    return (rs[0] if rs else None)

def grava_db(uf,ie, data, retorno):    
    sql = "insert into consulta_sefaz (cod_uf, nro_ie, dta_consulta, retorno) values (%s, %s, %s, %s)"
    cursor.execute(sql, (uf, ie, data, retorno,))
    connection.commit()
    
def trata_retorno(retorno):
    root = etree.fromstring(retorno.content)
    try:
        if uf in ['PR','SP','MS']:
           elemento = root[0][0][0][0]
        else:
           elemento = root[1][0][0][0]   
        ns = {'ns':'http://www.portalfiscal.inf.br/nfe'}    
        cstat = elemento.xpath("ns:cStat", namespaces=ns)[0].text
        print("CSTAT:", cstat)
        cnpj = ''
        csit = '0'
        if cstat in ['111','112']:    
            cnpj = elemento.xpath("ns:infCad/ns:CNPJ", namespaces=ns)[0].text
            print('CNPJ==>'+cnpj)
            ie = elemento.xpath("ns:infCad/ns:IE", namespaces=ns)[0].text
            print('IE==>'+ie)
 #           cnae = elemento.xpath("ns:infCad/ns:CNAE", namespaces=ns)[0].text
 #           print('CNAE==>'+cnae)
 #           rgap = elemento.xpath("ns:infCad/ns:xRegApur", namespaces=ns)[0].text
 #           print('Regime==>'+str(rgap))
            csit = elemento.xpath("ns:infCad/ns:cSit", namespaces=ns)[0].text
            #grava_db(uf, ie, hoje, cstat)
    except IndexError:
        print('Retorno com erro...')    
    
def consulta_sefaz(uf, ie, cnpj):
    con = ComunicacaoSefaz(uf, CERT, SENHA, HOMOLOG)  
    try:
        retorno = con.consulta_cadastro(modelo="nfe",cnpj=cnpj)           
        arq = open('retorno'+uf+ie+'.htm','w')
        arq.write(retorno.text)
        arq.close()   
        trata_retorno(retorno)
    except requests.exceptions.RequestException as e:
        print("Erro ao conectar: ", e)


# PR 9057048856     SC 256167990     SP;283103922115  MS;283021098 PR;9061784435  RS 0962574082  DF;0732530600156
#uf = "GO"
#ie = "105164070"
#uf = "MS"
#ie = "283435720"
uf = "MG"
ie = "3442021270020"
#uf = "MT"
#ie = "137265824"
#uf = "BA"
#ie = "130901367"
cnpj = ""
#cnpj = '13731542000186'
#uf = "SP"
#ie = "647790314110"
#uf = 'PR'
#cnpj = '79265617000199'
#ie = "9057048856"


hoje = datetime.date.today()
#connection = get_connection()
#cursor = get_cursor(connection)
#ret_db = consulta_db(uf, ie, hoje)
#print('Retorno db:', ret_db)
#if ret_db is None:
consulta_sefaz(uf, ie, cnpj)
     
#python -Bc "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
#python -Bc "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"     