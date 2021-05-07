  
CREATE TABLE consulta_sefaz (    
    cod_uf varchar(2) NOT NULL,
    nro_ie varchar(20) NOT NULL,    
    dta_consulta date NOT NULL,
    retorno VARCHAR(3),   
    csit integer,            
    PRIMARY KEY(cod_uf, nro_ie, dta_consulta)
  );  