from datetime import datetime, timedelta

from fraud_rules import verificar_regras, buscar_transacoes_60s, buscar_cidades_diferentes, buscar_transacoes_10m

hora_base = datetime(2026, 10, 21, 10, 0, 0)
erros = []


def nova_transacao(cliente, valor, cidade, segundos):
    return {
        "id_transacao": "teste",
        "id_cliente": cliente,
        "valor": valor,
        "country": "BR",
        "city": cidade,
        "hora": hora_base + timedelta(seconds=segundos),
    }


def conferir(nome, obtido, esperado):
    if obtido == esperado:
        print("OK    ", nome)
    else:
        print("ERRO  ", nome, "-> esperado", esperado, "mas veio", obtido)
        erros.append(nome)


print("\n--- Regra 1: ALTO_VALOR ---")

historico = []
alertas = verificar_regras(nova_transacao("A", 10000, "Fortaleza", 0), historico)
conferir("valor 10000 gera ALTO_VALOR", alertas, ["ALTO_VALOR"])

historico = []
alertas = verificar_regras(nova_transacao("A", 9999.99, "Fortaleza", 0), historico)
conferir("valor 9999.99 não gera alerta", alertas, [])

print("\n--- Regra 2: TEMPO_60s (4 transações em menos de 60 segundos) ---")

historico = []
for segundos in [0, 20, 40, 59]:
    transacao = nova_transacao("A", 50, "Fortaleza", segundos)
    alertas = verificar_regras(transacao, historico)
    historico.append(transacao)
conferir("4 transações em 59 s gera TEMPO_60s", alertas, ["TEMPO_60s"])

historico = []
for segundos in [0, 20, 40]:
    transacao = nova_transacao("A", 50, "Fortaleza", segundos)
    alertas = verificar_regras(transacao, historico)
    historico.append(transacao)
conferir("só 3 transações não gera alerta", alertas, [])

historico = []
for segundos in [0, 20, 40, 60]:
    transacao = nova_transacao("A", 50, "Fortaleza", segundos)
    alertas = verificar_regras(transacao, historico)
    historico.append(transacao)
conferir("4 transações em 60 s exatos não gera alerta", alertas, [])

historico = []
for segundos in [0, 10, 20]:
    transacao = nova_transacao("A", 50, "Fortaleza", segundos)
    verificar_regras(transacao, historico)
    historico.append(transacao)
alertas = verificar_regras(nova_transacao("B", 50, "Fortaleza", 30), historico)
conferir("3 do cliente A e 1 do cliente B não gera alerta", alertas, [])

print("\n--- Regra 3: GEO_10m (cidades diferentes em até 10 minutos) ---")

historico = []
primeira = nova_transacao("A", 50, "Fortaleza", 0)
verificar_regras(primeira, historico)
historico.append(primeira)
alertas = verificar_regras(nova_transacao("A", 50, "Recife", 599), historico)
conferir("cidade diferente após 599 s gera GEO_10m", alertas, ["GEO_10m"])

historico = []
primeira = nova_transacao("A", 50, "Fortaleza", 0)
verificar_regras(primeira, historico)
historico.append(primeira)
alertas = verificar_regras(nova_transacao("A", 50, "Recife", 600), historico)
conferir("cidade diferente após 600 s exatos gera GEO_10m", alertas, ["GEO_10m"])

historico = []
primeira = nova_transacao("A", 50, "Fortaleza", 0)
verificar_regras(primeira, historico)
historico.append(primeira)
alertas = verificar_regras(nova_transacao("A", 50, "Recife", 601), historico)
conferir("cidade diferente após 601 s não gera alerta", alertas, [])

historico = []
primeira = nova_transacao("A", 50, "Fortaleza", 0)
verificar_regras(primeira, historico)
historico.append(primeira)
alertas = verificar_regras(nova_transacao("A", 50, "Fortaleza", 60), historico)
conferir("mesma cidade não gera alerta", alertas, [])

historico = []
primeira = nova_transacao("A", 50, "Fortaleza", 0)
verificar_regras(primeira, historico)
historico.append(primeira)
alertas = verificar_regras(nova_transacao("B", 50, "Recife", 60), historico)
conferir("clientes diferentes não geram alerta", alertas, [])

print("\n--- Transação normal e transação com mais de um alerta ---")

historico = []
alertas = verificar_regras(nova_transacao("A", 500, "Fortaleza", 0), historico)
conferir("transação normal não gera alerta", alertas, [])

historico = []
primeira = nova_transacao("A", 50, "Fortaleza", 0)
verificar_regras(primeira, historico)
historico.append(primeira)
alertas = verificar_regras(nova_transacao("A", 15000, "Recife", 120), historico)
conferir("valor alto + cidade diferente gera 2 alertas", alertas, ["ALTO_VALOR", "GEO_10m"])

print("\n--- Transações anteriores que fazem parte da fraude ---")

historico = []
for segundos in [0, 20, 40]:
    transacao = nova_transacao("A", 50, "Fortaleza", segundos)
    historico.append(transacao)
quarta = nova_transacao("A", 50, "Fortaleza", 59)
conferir("TEMPO_60s: as 3 anteriores fazem parte do grupo", len(buscar_transacoes_60s(quarta, historico)), 3)

historico = [nova_transacao("A", 50, "Fortaleza", 0), nova_transacao("A", 50, "Fortaleza", 100)]
nova = nova_transacao("A", 50, "Fortaleza", 130)
conferir("TEMPO_60s: transação de 130 s antes não entra no grupo", len(buscar_transacoes_60s(nova, historico)), 1)

historico = [nova_transacao("A", 50, "Fortaleza", 0), nova_transacao("A", 50, "Fortaleza", 30)]
nova = nova_transacao("A", 50, "Recife", 60)
conferir("GEO_10m: as 2 anteriores em outra cidade entram no grupo", len(buscar_cidades_diferentes(nova, historico)), 2)

historico = [nova_transacao("A", 50, "Recife", 0), nova_transacao("A", 50, "Fortaleza", 30)]
nova = nova_transacao("A", 50, "Fortaleza", 60)
conferir("GEO_10m: anterior na mesma cidade não entra no grupo", len(buscar_cidades_diferentes(nova, historico)), 1)

historico = [nova_transacao("A", 50, "Fortaleza", 0), nova_transacao("B", 50, "Fortaleza", 100), nova_transacao("A", 50, "Fortaleza", 500)]
nova = nova_transacao("A", 50, "Fortaleza", 700)
conferir("análise: só transações do mesmo cliente em até 10 min", len(buscar_transacoes_10m(nova, historico)), 1)

print()
if len(erros) == 0:
    print("Todos os testes passaram.")
else:
    print("Testes que falharam:", erros)