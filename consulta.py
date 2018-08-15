import configparser
import csv
import os
import time
import requests.exceptions
from pynfe.processamento.comunicacao import ComunicacaoSefaz
from lxml import etree

def consulta_cad(uf,ie):
    cnpj = ''
    csit = '0'
    cnae = '0'
    cstat = '999'
    con = ComunicacaoSefaz(uf, CERT_PFX, CERT_PWD, HOMOLOGACAO)
    try:
        retorno = con.consultar_cadastro(modelo="nfe",cnpj='',ie=ie)
    except requests.exceptions.ConnectionError:
        return cstat, cnpj, csit, cnae

    root = etree.fromstring(retorno.content)
    try:
        if uf in ['PR','SP','MS']:
           elemento = root[0][0][0][0]
        else:
           elemento = root[1][0][0][0]   
        ns = {'ns':'http://www.portalfiscal.inf.br/nfe'}
        cstat = elemento.xpath("ns:cStat", namespaces=ns)[0].text        
        if cstat in ['111','112']:
            cnpj = elemento.xpath("ns:infCad/ns:CNPJ", namespaces=ns)[0].text
            csit = elemento.xpath("ns:infCad/ns:cSit", namespaces=ns)[0].text
            if uf != 'MS':
                cnae = elemento.xpath("ns:infCad/ns:CNAE", namespaces=ns)[0].text
    except IndexError:
        cstat = '999'

    return cstat, cnpj, csit, cnae

def processar_arq(arquivo,saida):
    arqtxt = open(saida,"w")
    relacao = open(arquivo,"r")
    contador = 0
    for linha in relacao:
        if linha[0:3] == "FIM":
            arqtxt.write(linha)
        else:
            contador = contador + 1
            campos = linha.split(';')
            flag = campos[0]
            codigo = campos[1]
            cnpj = campos[2]
            uf = campos[3]
            ie = campos[4]
            print('consulta:'+str(contador)+' '+uf+' '+ie)
            cstat,cnpj,csit,cnae = consulta_cad(uf,ie.strip())
            ln = flag+';'+codigo+';'+cnpj+';'+uf+';'+ie+';'+cstat+';'+csit+';'+cnae+'\n'
            arqtxt.write(ln)

    relacao.close()
    arqtxt.close()
    data_hora = time.strftime('%Y%m%d%H%M%S')
    os.rename(arquivo,DIR_HIST+data_hora+'-'+os.path.basename(arquivo))

def arq_completo(arquivo):
    print('Verificando arquivo '+ARQ_IN+' ...')
    arqtxt = open(arquivo)
    qt_linhas = 0
    final_ok = False
    for linha in arqtxt:
        qt_linhas += 1
        if linha[0:3] == "FIM":
            final_ok = True
    arqtxt.close()
    return final_ok and qt_linhas > 1

if __name__ == "__main__":
   cfg = configparser.ConfigParser()
   cfg.read('config.ini')
   CERT_PFX = cfg.get("geral","cert_pfx")
   CERT_PWD = cfg.get("geral","cert_pwd")
   HOMOLOGACAO = cfg.getboolean("geral","homologacao")
   ARQ_IN = cfg.get("geral","arq_in")
   ARQ_OUT = cfg.get("geral","arq_out")
   DIR_HIST = cfg.get("geral","dir_hist")

   while True:
       print('Aguardando arquivo '+ARQ_IN+' ')
       if os.path.exists(ARQ_IN):
           if arq_completo(ARQ_IN):
               processar_arq(ARQ_IN,ARQ_OUT)
       for i in range(5):
           time.sleep(1)
           print('.')
