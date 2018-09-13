from pytrustnfe.nfe import consulta_cadastro
from pytrustnfe.certificado import Certificado
import configparser

cfg = configparser.ConfigParser()
cfg.read('config.ini')
CERT = cfg.get("geral","cert_pfx")
SENHA = cfg.get("geral","cert_pwd")   
HOMOLOG = cfg.getboolean("geral","homologacao")  
UF = "DF"
IE = "0732530600156"
print(SENHA)

arquivo_pfx = open(CERT,"rb").read()
certificado = Certificado(arquivo_pfx, SENHA)
#obj = {'cnpj': '95410163000744', 'estado': 'PR'}
obj = {'cnpj': '03987322000164', 'estado': 'DF'}
resposta = consulta_cadastro(certificado, obj=obj, ambiente=1, estado='53')
print(resposta)
