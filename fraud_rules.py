def buscar_transacoes_60s(transacao, historico):
    encontradas = []
    for antiga in historico:
        if antiga["id_cliente"] == transacao["id_cliente"]:
            segundos = (transacao["hora"] - antiga["hora"]).total_seconds()
            if segundos < 60:
                encontradas.append(antiga)
    return encontradas


def buscar_cidades_diferentes(transacao, historico):
    encontradas = []
    for antiga in historico:
        if antiga["id_cliente"] == transacao["id_cliente"]:
            segundos = (transacao["hora"] - antiga["hora"]).total_seconds()
            if antiga["city"] != transacao["city"] and segundos <= 600:
                encontradas.append(antiga)
    return encontradas


def buscar_transacoes_10m(transacao, historico):
    encontradas = []
    for antiga in historico:
        if antiga["id_cliente"] == transacao["id_cliente"]:
            segundos = (transacao["hora"] - antiga["hora"]).total_seconds()
            if segundos <= 600:
                encontradas.append(antiga)
    return encontradas


def verificar_regras(transacao, historico):
    alertas = []

    # Regra do valor
    if transacao["valor"] >= 10000:
        alertas.append("ALTO_VALOR")

    # Regra do tempo
    anteriores_60s = buscar_transacoes_60s(transacao, historico)
    if len(anteriores_60s) + 1 >= 4:
        alertas.append("TEMPO_60s")

    # Regra da cidade
    anteriores_geo = buscar_cidades_diferentes(transacao, historico)
    if len(anteriores_geo) > 0:
        alertas.append("GEO_10m")

    return alertas