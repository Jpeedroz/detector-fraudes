import json
import random
import time
import uuid
from datetime import datetime

from kafka import KafkaProducer

CIDADES = ["Fortaleza", "Recife", "Salvador", "Natal", "Teresina",
           "São Luís", "Belém", "Manaus", "Maceió", "João Pessoa"]

clientes = []
cidades_dos_clientes = []
for i in range(100):
    clientes.append(str(uuid.uuid4()))
    cidades_dos_clientes.append(random.choice(CIDADES))


def criar_transacao(id_cliente, valor, city):
    transacao = {
        "id_transacao": str(uuid.uuid4()),
        "id_cliente": id_cliente,
        "valor": valor,
        "country": "BR",
        "city": city,
        "hora": datetime.now().isoformat(timespec="seconds"),
    }
    return transacao


def enviar(transacao, situacao):
    texto = json.dumps(transacao)
    producer.send("transacoes", texto.encode("utf-8"))
    producer.flush()

    print("=" * 60)
    print("TRANSAÇÃO ENVIADA")
    print("ID da transação :", transacao["id_transacao"])
    print("ID do cliente   :", transacao["id_cliente"])
    print("Valor           : R$", transacao["valor"])
    print("País            :", transacao["country"])
    print("Cidade          :", transacao["city"])
    print("Hora            :", transacao["hora"].replace("T", " "))
    print("-" * 60)
    print("SITUAÇÃO        :", situacao)
    print("=" * 60)
    print()


producer = KafkaProducer(bootstrap_servers="localhost:9092")

print("Producer iniciado. Uma transação a cada 3 segundos. Ctrl+C para parar.")
print()

recentes = []

while True:
    sorteio = random.randint(1, 100)

    if sorteio <= 30:
        tipo = random.randint(1, 3)
        cliente = str(uuid.uuid4())
        cidade = random.choice(CIDADES)

        if tipo == 1:
            # Fraude de valor
            print(">>> SITUAÇÃO PLANEJADA: ALTO_VALOR (valor de R$ 10000 ou mais)")
            print()
            valor = round(random.uniform(10000, 20000), 2)
            enviar(criar_transacao(cliente, valor, cidade), "valor alto (ALTO_VALOR)")

        elif tipo == 2:
            # Fraude de tempo
            print(">>> SITUAÇÃO PLANEJADA: TEMPO_60s (4 transações do mesmo cliente em menos de 60 segundos)")
            print()
            for vez in range(1, 5):
                valor = round(random.uniform(10, 9999), 2)
                enviar(criar_transacao(cliente, valor, cidade),
                    str(vez) + " / 4 transações (TEMPO_60s)")
                if vez < 4:
                    time.sleep(3)

        else:
            # Fraude de cidade
            print(">>> SITUAÇÃO PLANEJADA: GEO_10m (mesmo cliente em cidades diferentes em menos de 10 minutos)")
            print()
            valor = round(random.uniform(10, 9999), 2)
            enviar(criar_transacao(cliente, valor, cidade), "1ª cidade (GEO_10m)")
            time.sleep(3)

            outra_cidade = random.choice(CIDADES)
            while outra_cidade == cidade:
                outra_cidade = random.choice(CIDADES)
            valor = round(random.uniform(10, 9999), 2)
            enviar(criar_transacao(cliente, valor, outra_cidade), "2ª cidade (GEO_10m)")

    else:
        # Transação normal
        posicao = random.randint(0, 99)
        while clientes[posicao] in recentes:
            posicao = random.randint(0, 99)
        cliente = clientes[posicao]
        cidade = cidades_dos_clientes[posicao]

        recentes.append(cliente)
        if len(recentes) > 25:
            recentes.pop(0)

        valor = round(random.uniform(10, 9999), 2)
        enviar(criar_transacao(cliente, valor, cidade), "transação normal")

    print()
    time.sleep(3)