import configparser
import csv
import os
import time
from pynfe.processamento.comunicacao import ComunicacaoSefaz
from lxml import etree
                  
def consulta_cad(uf,ie):
    cstat = '999'  
    cnpj = ''
    csit = '0'
    cnae = 'NAORETO'    
    apur = 'NAORETO'
    try:
        con = ComunicacaoSefaz(uf, CERT_PFX, CERT_PWD, HOMOLOGACAO)
        retorno = con.consultar_cadastro(modelo="nfe",cnpj='',ie=ie)     
        root = etree.fromstring(retorno.content)
        elemento = root[1][0][0][0]
        ns = {'ns':'http://www.portalfiscal.inf.br/nfe'}    
        cstat = elemento.xpath("ns:cStat", namespaces=ns)[0].text        
        if cstat in ['111','112']:
            cnpj = elemento.xpath("ns:infCad/ns:CNPJ", namespaces=ns)[0].text       
            csit = elemento.xpath("ns:infCad/ns:cSit", namespaces=ns)[0].text
            try:
                cnae = elemento.xpath("ns:infCad/ns:CNAE", namespaces=ns)[0].text
            except IndexError:
                cnae = 'NAORETO'
            try:        
                apur = elemento.xpath("ns:infCad/ns:xRegApur", namespaces=ns)[0].text
            except IndexError:
                apur = 'NAORETO'
    except Exception:
        print('Sem resposta do servidor da Sefaz:'+uf)
                                
    return {'cstat':cstat, 'cnpj':cnpj, 'csit': csit, 'cnae':str(cnae), 'apur':str(apur)}

def processar_arq(arquivo,saida):  
    arqtxt = open(saida,"w")
    relacao = open(arquivo,"r")    
    x = 0
    for linha in relacao:
        x += 1                 
        campos = linha.split(';')        
        uf = campos[0]
        cnpj = campos[1]
        ie = campos[2]
        rt = consulta_cad(uf,ie.strip())
        ln = uf+';'+cnpj+';'+ie+';'+rt['cstat']+';'+rt['csit']+';'+rt['cnae']+';'+rt['apur']+'\n'
        print('Linha: '+str(x)+'  -> '+ln)                    
        arqtxt.write(ln)
                               
    relacao.close()
    arqtxt.close()
    #data_hora = time.strftime('%Y%m%d%H%M%S')
    #os.rename(arquivo,DIR_HIST+data_hora+'-'+os.path.basename(arquivo))
                                                                                               
if __name__ == "__main__":
   cfg = configparser.ConfigParser()
   cfg.read('config.ini')
   CERT_PFX = cfg.get("geral","cert_pfx")
   CERT_PWD = cfg.get("geral","cert_pwd")   
   HOMOLOGACAO = cfg.getboolean("geral","homologacao")  
   ARQ_IN = "in/clientes.txt"
   ARQ_OUT = "in/clientes_ret.txt"
   DIR_HIST = cfg.get("geral","dir_hist")  
   
   if os.path.exists(ARQ_IN):
       processar_arq(ARQ_IN,ARQ_OUT)
    