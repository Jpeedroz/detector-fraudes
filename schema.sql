CREATE TABLE IF NOT EXISTS transacoes (
    id_transacao VARCHAR(50) PRIMARY KEY,   
    cliente_id VARCHAR(20) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    cidade VARCHAR(80) NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    status VARCHAR(10) NOT NULL    
);

CREATE TABLE IF NOT EXISTS alertas_fraude (
    id SERIAL PRIMARY KEY,
    id_transacao VARCHAR(50) NOT NULL REFERENCES transacoes (id_transacao),
    regra VARCHAR(20) NOT NULL, 
    UNIQUE (id_transacao, regra)
);
