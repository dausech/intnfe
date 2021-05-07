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
    razao = ''    
    fantasia = ''
    cidade = ''
    estado = ''
    bairro = ''
    logradouro = ''
    numero = ''
    cep = ''
    try:
        con = ComunicacaoSefaz(uf, CERT_PFX, CERT_PWD, HOMOLOGACAO)
        retorno = con.consultar_cadastro(modelo="nfe",cnpj='',ie=ie)     
        arqlog = open('./log/retorno_'+ie+'.xml','w')
        arqlog.write(retorno.text)
        arqlog.close()
        root = etree.fromstring(retorno.content)
        elemento = root[0][0][0][0]
        ns = {'ns':'http://www.portalfiscal.inf.br/nfe'}    
        cstat = elemento.xpath("ns:cStat", namespaces=ns)[0].text        
        if cstat in ['111','112']:
            cnpj = elemento.xpath("ns:infCad/ns:CNPJ", namespaces=ns)[0].text       
            csit = elemento.xpath("ns:infCad/ns:cSit", namespaces=ns)[0].text
            try:
                razao = elemento.xpath("ns:infCad/ns:xNome", namespaces=ns)[0].text                
                estado = elemento.xpath("ns:infCad/ns:UF", namespaces=ns)[0].text
                cidade = elemento.xpath("ns:infCad/ns:ender/ns:xMun", namespaces=ns)[0].text                
                logradouro = elemento.xpath("ns:infCad/ns:ender/ns:xLgr", namespaces=ns)[0].text
                numero = elemento.xpath("ns:infCad/ns:ender/ns:nro", namespaces=ns)[0].text
                bairro = elemento.xpath("ns:infCad/ns:ender/ns:xBairro", namespaces=ns)[0].text
                cep = elemento.xpath("ns:infCad/ns:ender/ns:CEP", namespaces=ns)[0].text
                fantasia = elemento.xpath("ns:infCad/ns:xFant", namespaces=ns)[0].text
            except IndexError:
                pass
    except Exception:
        print('Sem resposta do servidor da Sefaz:'+uf)
                                
    return {'cstat':cstat, 
            'cnpj':cnpj, 
            'csit': csit, 
            'razao':razao, 
            'fantasia':fantasia, 
            'cidade': cidade, 
            'uf':estado,
            'bairro':bairro,
            'cep':str(cep),  
            'logradouro':logradouro,
            'numero':str(numero)}

def processar_arq(cnaes_alvo):  
    relacao = open("in/ativos1.txt","r")  
    arqtxt = open("in/ativos_varejistas.csv","w")
    contador = 0
    for linha in relacao:
        contador += 1                
        campos = linha.split(';')        
        ie = campos[0]
        cnpj = campos[1]
        cnae = campos[5].strip()    
        if cnae in cnaes_alvo:        
            rt = consulta_cad('PR',ie.strip())
            ln = cnpj+';'+ie+';'+cnae+';'+rt['cstat']+';'+rt['csit']+';'+rt['razao']+';'+rt['fantasia']+';'+rt['cidade']+';'+rt['uf']+';'+rt['bairro']+';'+rt['cep']+';'+rt['logradouro']+';'+rt['numero']+';\n' 
            arqtxt.write(ln)
            print("processando ", str(contador), ln)        
            time.sleep(1)
    arqtxt.close()        
    relacao.close()
                                                                                               
if __name__ == "__main__":
    cfg = configparser.ConfigParser()
    cfg.read('config.ini')
    CERT_PFX = cfg.get("geral","cert_pfx")
    CERT_PWD = cfg.get("geral","cert_pwd")   
    HOMOLOGACAO = cfg.getboolean("geral","homologacao")  
    CNAES_ALVO = cfg.get("geral","cnae").split(',')    
    linhas_reproc = []
    passo = 1
    print("iniciando...", CNAES_ALVO)                     
    processar_arq(CNAES_ALVO)
       
       