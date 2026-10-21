import json
from datetime import datetime

from kafka import KafkaConsumer

import database
import fraud_rules

conexao = database.conectar()

consumer = KafkaConsumer(
    "transacoes",
    bootstrap_servers="localhost:9092",
    group_id="fraudes-consumer",
    auto_offset_reset="earliest",
)

numero = 0
historico = []

print("Consumer aguardando mensagens... (Ctrl+C para parar)")

for mensagem in consumer:

    texto = mensagem.value.decode("utf-8")
    transacao = json.loads(texto)

    transacao["hora"] = datetime.fromisoformat(transacao["hora"])

    if database.transacao_existe(conexao, transacao["id_transacao"]):
        print("[IGNORADA] Transação repetida:", transacao["id_transacao"])

    else:
        # Aplica as regras
        alertas = fraud_rules.verificar_regras(transacao, historico)

        anteriores_60s = fraud_rules.buscar_transacoes_60s(transacao, historico)
        anteriores_geo = fraud_rules.buscar_cidades_diferentes(transacao, historico)
        recentes_10m = fraud_rules.buscar_transacoes_10m(transacao, historico)

        # Salva no banco
        database.salvar_transacao(conexao, transacao, alertas)

        if "TEMPO_60s" in alertas:
            for antiga in anteriores_60s:
                database.marcar_suspeita(conexao, antiga["id_transacao"], "TEMPO_60s")
        if "GEO_10m" in alertas:
            for antiga in anteriores_geo:
                database.marcar_suspeita(conexao, antiga["id_transacao"], "GEO_10m")

        historico.append(transacao)

        hora_atual = transacao["hora"].strftime("%H:%M:%S")

        print("=" * 60)
        print("TRANSAÇÃO RECEBIDA")
        print("ID da transação :", transacao["id_transacao"])
        print("ID do cliente   :", transacao["id_cliente"])
        print("Valor           : R$", transacao["valor"])
        print("País            :", transacao["country"])
        print("Cidade          :", transacao["city"])
        print("Hora            :", transacao["hora"])
        print("-" * 60)

        print("ANÁLISE DAS REGRAS")

        # Regra do valor
        if "ALTO_VALOR" in alertas:
            print("ALTO_VALOR : SIM  (valor maior ou igual a R$ 10000)")
        else:
            print("ALTO_VALOR : NÃO  (valor abaixo de R$ 10000)")

        # Regra do tempo
        quantidade = len(anteriores_60s) + 1
        if quantidade > 1:
            primeira = anteriores_60s[0]
            segundos_grupo = int((transacao["hora"] - primeira["hora"]).total_seconds())
            hora_primeira = primeira["hora"].strftime("%H:%M:%S")

        if "TEMPO_60s" in alertas:
            print("TEMPO_60s  : SIM  (" + str(quantidade) + " transações deste cliente em "
                  + str(segundos_grupo) + " segundos, das " + hora_primeira + " às " + hora_atual + ")")
        elif quantidade > 1:
            print("TEMPO_60s  : NÃO  (" + str(quantidade) + " transações deste cliente em "
                  + str(segundos_grupo) + " segundos; precisa de 4)")
        else:
            print("TEMPO_60s  : NÃO  (1 transação deste cliente em 60s; precisa de 4)")

        # Regra da cidade
        if "GEO_10m" in alertas:
            ultima = anteriores_geo[-1]
            segundos_geo = int((transacao["hora"] - ultima["hora"]).total_seconds())
            print("GEO_10m    : SIM  (às " + ultima["hora"].strftime("%H:%M:%S") + " estava em "
                  + ultima["city"] + "; " + str(segundos_geo) + " segundos depois está em "
                  + transacao["city"] + ")")
        elif len(recentes_10m) > 0:
            print("GEO_10m    : NÃO  (todas as transações recentes deste cliente foram em "
                  + transacao["city"] + ")")
        else:
            print("GEO_10m    : NÃO  (nenhuma transação deste cliente nos últimos 10 minutos)")
        print("-" * 60)

        # Resultado
        if len(alertas) == 0:
            print("RESULTADO       : TRANSAÇÃO NORMAL")
        else:
            print("RESULTADO       : *** FRAUDE DETECTADA ***")
            print("TIPO DE FRAUDE  :", ", ".join(alertas))

        print("Salva no banco  : SIM")
        print("=" * 60)
        print()