
from datetime import datetime, timedelta

from fraud_rules import verificar_regras

HORA_BASE = datetime(2026, 10, 9, 10, 0, 0)   
erros = []                                     


def criar_transacao(cliente, amount, cidade, segundos):
    hora = HORA_BASE + timedelta(seconds=segundos)
    return {
        "id_transacao": "teste",
        "cliente_id": cliente,
        "amount": amount,
        "cidade": cidade,
        "data_hora": hora,
    }


def conferir(nome, obtido, esperado):
    if obtido == esperado:
        print("OK    ", nome)
    else:
        print("ERRO  ", nome, "-> esperado", esperado, "mas veio", obtido)
        erros.append(nome)


# ---------------------------------------------------------------------------
print("\n--- ALTO_VALOR (a partir de 10000) ---")

historico = {}
alertas = verificar_regras(criar_transacao("A", 9999.99, "Fortaleza", 0), historico)
conferir("9999.99 não gera alerta", alertas, [])

historico = {}
alertas = verificar_regras(criar_transacao("A", 10000, "Fortaleza", 0), historico)
conferir("10000 gera ALTO_VALOR", alertas, ["ALTO_VALOR"])

# ---------------------------------------------------------------------------
print("\n--- TEMPO_60s (4 transações em MENOS de 60 segundos) ---")

historico = {}
for segundos in [0, 20, 40]:
    alertas = verificar_regras(criar_transacao("A", 50, "Fortaleza", segundos), historico)
conferir("só 3 transações: não alerta", alertas, [])

historico = {}
for segundos in [0, 20, 40, 59]:
    alertas = verificar_regras(criar_transacao("A", 50, "Fortaleza", segundos), historico)
conferir("4 transações em 59 s: alerta", alertas, ["TEMPO_60s"])

historico = {}
for segundos in [0, 20, 40, 60]:
    alertas = verificar_regras(criar_transacao("A", 50, "Fortaleza", segundos), historico)
conferir("4 transações em 60 s exatos: NÃO alerta", alertas, [])

# ---------------------------------------------------------------------------
print("\n--- GEO_10m (cidade diferente em até 10 minutos = 600 s) ---")

historico = {}
verificar_regras(criar_transacao("A", 50, "Fortaleza", 0), historico)
alertas = verificar_regras(criar_transacao("A", 50, "Recife", 599), historico)
conferir("cidade diferente após 599 s: alerta", alertas, ["GEO_10m"])

historico = {}
verificar_regras(criar_transacao("A", 50, "Fortaleza", 0), historico)
alertas = verificar_regras(criar_transacao("A", 50, "Recife", 600), historico)
conferir("cidade diferente após 600 s exatos: alerta", alertas, ["GEO_10m"])

historico = {}
verificar_regras(criar_transacao("A", 50, "Fortaleza", 0), historico)
alertas = verificar_regras(criar_transacao("A", 50, "Recife", 601), historico)
conferir("cidade diferente após 601 s: NÃO alerta", alertas, [])

historico = {}
verificar_regras(criar_transacao("A", 50, "Fortaleza", 0), historico)
alertas = verificar_regras(criar_transacao("A", 50, "Fortaleza", 60), historico)
conferir("mesma cidade: não alerta", alertas, [])

historico = {}
verificar_regras(criar_transacao("A", 50, "Fortaleza", 0), historico)
alertas = verificar_regras(criar_transacao("B", 50, "Recife", 60), historico)
conferir("clientes diferentes: não alerta", alertas, [])

# ---------------------------------------------------------------------------
print("\n--- Duas regras na mesma transação ---")

historico = {}
verificar_regras(criar_transacao("A", 50, "Fortaleza", 0), historico)
alertas = verificar_regras(criar_transacao("A", 15000, "Recife", 120), historico)
conferir("valor alto + cidade diferente", alertas, ["ALTO_VALOR", "GEO_10m"])

# ---------------------------------------------------------------------------
print()
if len(erros) == 0:
    print("Todos os testes passaram.")
else:
    print("Testes que falharam:", erros)