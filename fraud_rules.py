def verificar_regras(transacao, historico):
    cliente = transacao["cliente_id"]

    if cliente not in historico:
        historico[cliente] = []
    anteriores = historico[cliente]

    alertas = []

    # Regra 1: ALTO_VALOR -> valor maior ou igual a 10000
    if transacao["amount"] >= 10000:
        alertas.append("ALTO_VALOR")

    # Regra 2: TEMPO_60s -> 4 transações do cliente em MENOS de 60 segundos
    quantidade = 1  # a transação atual já conta como uma
    for anterior in anteriores:
        segundos = (transacao["data_hora"] - anterior["data_hora"]).total_seconds()
        if 0 <= segundos < 60:      # menor que 60 (exatamente 60 não vale)
            quantidade = quantidade + 1
    if quantidade >= 4:
        alertas.append("TEMPO_60s")

    # Regra 3: GEO_10m -> cidade diferente de uma transação anterior em até 10 minutos (600 s)
    for anterior in anteriores:
        segundos = (transacao["data_hora"] - anterior["data_hora"]).total_seconds()
        if anterior["cidade"] != transacao["cidade"] and 0 <= segundos <= 600:
            alertas.append("GEO_10m")
            break   # basta encontrar uma

    anteriores.append({"data_hora": transacao["data_hora"], "cidade": transacao["cidade"]})
    return alertas
