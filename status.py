import configparser
from lxml import etree
from pynfe.processamento.comunicacao import ComunicacaoSefaz
                                        
def status(modelo):
    try:
        con = ComunicacaoSefaz(UF, CERT, SENHA, homologacao)
        xml = con.status_servico(modelo)        
        return xml 
    except SSLError:
        print('Erro comunicando com Servidor')
        return None    

def mostra(ret):        
    root = etree.fromstring(ret.content)        
    elemento = root[1][0][0]                    
    ns = {'ns':'http://www.portalfiscal.inf.br/nfe'}    
    cstat = elemento.xpath('ns:cStat', namespaces=ns)[0].text
    tpamb = elemento.xpath('ns:tpAmb', namespaces=ns)[0].text
    veraplic = elemento.xpath('ns:verAplic', namespaces=ns)[0].text
    xmotivo = elemento.xpath('ns:xMotivo', namespaces=ns)[0].text
    cuf = elemento.xpath('ns:cUF', namespaces=ns)[0].text
    dhrecbto = elemento.xpath('ns:dhRecbto', namespaces=ns)[0].text    
    print(cuf)
    print(tpamb)
    print(veraplic)
    print(cstat)
    print(xmotivo)
    print(dhrecbto)

if __name__ == '__main__':
    cfg = configparser.ConfigParser()
    cfg.read('config.ini')
    CERT = cfg.get("geral","cert_pfx")
    SENHA = cfg.get("geral","cert_pwd")  
    UF = 'pr'
    homologacao = False
    
    ret_nfe = status('nfe')
    ret_nfce = status('nfce')
    if ret_nfe is not None:
        print('\nStatus da Sefaz - NF-e:')
        mostra(ret_nfe)
                                            
    if ret_nfce is not None:
        print('\nStatus da Sefaz - NFC-e:')
        mostra(ret_nfce)

