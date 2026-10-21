# Detector de Fraudes com Apache Kafka

Sistema desenvolvido em Python que simula transações bancárias, processa mensagens com Apache Kafka, identifica possíveis fraudes e armazena todas as transações no PostgreSQL

## Tecnologias

- Python 3.10+
- Apache Kafka 3.8
- PostgreSQL 16
- Docker Compose
- `kafka-python` e `psycopg2-binary`

## Arquitetura

```text
Producer → Kafka → Consumer → PostgreSQL   
```

- **Producer:** gera uma transação a cada 3 segundos e envia ao Kafka.
- **Kafka:** recebe e disponibiliza as mensagens para o Consumer.
- **Consumer:** aplica as regras de detecção, salva os dados e exibe os resultados.
- **PostgreSQL:** armazena todas as transações e os alertas identificados.

## Regras de detecção

| Alerta       | Condição                                                               |
| ------------ | ---------------------------------------------------------------------- |
| `ALTO_VALOR` | Transação com valor ≥ 10.000                                           |
| `TEMPO_60s`  | 4 ou mais transações do mesmo cliente em menos de 60 segundos          |
| `GEO_10m`    | Transações do mesmo cliente em cidades diferentes dentro de 10 minutos |

## Como executar

**Pré-requisitos:** Python, Docker Desktop em execução e Git Bash no Windows.

### 1. Instalar as dependências

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

No Linux/macOS, use `source .venv/bin/activate`.

### 2. Executar os testes

```bash
python test_fraud_rules.py
```

Os testes das regras não precisam do Docker.

### 3. Iniciar os serviços

```bash
docker compose down -v
docker compose up -d
```

**Atenção:** `docker compose down -v` remove os volumes e apaga os dados persistidos nesses volumes.

### 4. Criar o tópico Kafka

Aguarde aproximadamente 15 segundos após iniciar os serviços.

```bash
MSYS_NO_PATHCONV=1 docker exec kafka /opt/kafka/bin/kafka-topics.sh --create --if-not-exists --topic transacoes --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

No Linux/macOS, remova `MSYS_NO_PATHCONV=1`.

### 5. Executar o Consumer

No primeiro terminal:

```bash
source .venv/Scripts/activate
python consumer.py
```

### 6. Executar o Producer

No segundo terminal:

```bash
source .venv/Scripts/activate
python producer.py
```

O Producer começará a gerar transações, e o Consumer exibirá os resultados do processamento.

Para interromper a execução, pressione `Ctrl + C` nos terminais e execute:

```bash
docker compose stop
```

## Consultar os resultados

As tabelas são criadas automaticamente pelo `schema.sql` quando o PostgreSQL é inicializado.

**Consultar transações por status:**

```bash
docker exec postgres_fraudes psql -U postgres -d fraudes -c "SELECT status, COUNT(*) FROM transacoes GROUP BY status;"
```

**Consultar alertas por regra:**

```bash
docker exec postgres_fraudes psql -U postgres -d fraudes -c "SELECT regra, COUNT(*) FROM alertas_fraude GROUP BY regra;"
```

### Acesso pelo pgAdmin

| Configuração | Valor       |
| ------------ | ----------- |
| Host         | `localhost` |
| Porta        | `5433`      |
| Banco        | `fraudes`   |
| Usuário      | `postgres`  |
| Senha        | `postgres`  |
