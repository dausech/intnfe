from pynfe.processamento.comunicacao import ComunicacaoSefaz
import requests
import requests.exceptions
import logging
import configparser
from lxml import etree

# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client

def trata_retorno(retorno):
    root = etree.fromstring(retorno.content)
    try:
        if UF in ['PR','SP','MS']:
           elemento = root[0][0][0][0]
        else:
           elemento = root[1][0][0][0]   
        ns = {'ns':'http://www.portalfiscal.inf.br/nfe'}    
        cstat = elemento.xpath("ns:cStat", namespaces=ns)[0].text
        cnpj = ''
        csit = '0'
        if cstat in ['111','112']:    
            cnpj = elemento.xpath("ns:infCad/ns:CNPJ", namespaces=ns)[0].text
            print('CNPJ==>'+cnpj)
            ie = elemento.xpath("ns:infCad/ns:IE", namespaces=ns)[0].text
            print('IE==>'+ie)
            cnae = elemento.xpath("ns:infCad/ns:CNAE", namespaces=ns)[0].text
            print('CNAE==>'+cnae)
            rgap = elemento.xpath("ns:infCad/ns:xRegApur", namespaces=ns)[0].text
            print('Regime==>'+str(rgap))
            csit = elemento.xpath("ns:infCad/ns:cSit", namespaces=ns)[0].text
    except IndexError:
        print('Retorno com erro...')    
    
    
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
UF = "MS"
IE = "283916710"

# PR 9057048856     SC 256167990     SP;283103922115  MS;283021098 PR;9061784435  RS 0962574082  DF;0732530600156
con = ComunicacaoSefaz(UF, CERT, SENHA, HOMOLOG)  
try:
    retorno = con.consultar_cadastro(modelo="nfe",ie=IE,cnpj='')    
    trata_retorno(retorno)
    arq = open('retorno'+UF+IE+'.htm','w')
    arq.write(retorno.text)
    arq.close
except requests.exceptions.RequestException as e:
    print("Erro ao conectar: ", e)


     