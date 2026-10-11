# Detector de Fraudes

Sistema que identifica transações bancárias suspeitas utilizando Python, Apache Kafka e PostgreSQL. Tudo isso em tempo real!

## Tecnologias

- Python
- Apache Kafka
- PostgreSQL
- Docker Compose

## Regras de detecção

- **ALTO_VALOR:** transações com valor igual ou superior a R$ 10.000,00.
- **TEMPO_60s:** quatro ou mais transações do mesmo cliente em menos de 60 segundos.
- **GEO_10m:** duas transações do mesmo cliente em cidades diferentes dentro de 10 minutos.

## Estrutura do projeto

- `producer.py`: gera e envia transações para o Kafka.
- `consumer.py`: recebe e processa as transações.
- `fraud_rules.py`: contém as regras de detecção.
- `database.py`: gerencia a conexão com o banco de dados.
- `schema.sql`: define as tabelas do banco.
- `docker-compose.yml`: configura os serviços.
- `requirements.txt`: lista as dependências Python.
- `test_fraud_rules.py`: contém os testes das regras.

## Funcionamento

O produtor gera transações a cada 3 segundos e as envia ao Kafka. O consumidor recebe as mensagens, verifica as regras de fraude, exibe os resultados no terminal e armazena as transações no PostgreSQL.

## Como executar

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU-USUARIO/detector-fraudes.git
cd detector-fraudes
```

### 2. Criar e ativar o ambiente virtual

```bash
python -m venv .venv
```

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 4. Iniciar os serviços

```bash
docker compose up -d
```

### 5. Configurar o banco de dados

Execute o arquivo `schema.sql` no PostgreSQL para criar as tabelas necessárias, conforme as configurações do projeto.

### 6. Executar os testes

```bash
python -m unittest test_fraud_rules.py
```

### 7. Iniciar o consumidor

Em um terminal:

```bash
python consumer.py
```

### 8. Iniciar o produtor

Em outro terminal:

```bash
python producer.py
```



