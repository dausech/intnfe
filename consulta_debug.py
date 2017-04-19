from pynfe.processamento.comunicacao import ComunicacaoSefaz
import requests
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
UF = "BA"

con = ComunicacaoSefaz(UF, CERT, SENHA, HOMOLOG)  
retorno = con.consultar_cadastro(modelo="nfe",ie="",cnpj="00716869000137")
# print (retorno.text)
arq = open('bahia.htm','w')
arq.write(retorno.text)
arq.close

root = etree.fromstring(retorno.content)
elemento = root[1][0][0][0]
ns = {'ns':'http://www.portalfiscal.inf.br/nfe'}    
cstat = elemento.xpath("ns:cStat", namespaces=ns)[0].text
cnpj = ''
csit = '0'
if cstat in ['111','112']:
    print('tamanho:'+str(len(elemento)))    
    for i in range(len(elemento)-1):
        print('\n\nitem==>'+str(i))
        cnpj = elemento.xpath("ns:infCad/ns:CNPJ", namespaces=ns)[i].text
        print('CNPJ==>'+cnpj)
        ie = elemento.xpath("ns:infCad/ns:IE", namespaces=ns)[i].text
        print('IE==>'+ie)
        cnae = elemento.xpath("ns:infCad/ns:CNAE", namespaces=ns)[i].text
        print('CNAE==>'+cnae)
        rgap = elemento.xpath("ns:infCad/ns:xRegApur", namespaces=ns)[i].text
        print('Regime==>'+rgap)
        csit = elemento.xpath("ns:infCad/ns:cSit", namespaces=ns)[i].text

     