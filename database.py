import psycopg2

def conectar():
    return psycopg2.connect(
        host="localhost", port=5433, dbname="fraudes", user="postgres", password="postgres"
    )


def transacao_existe(conexao, id_transacao):
    """True se a transação já está no banco (acontece se o Kafka reenviar a mensagem)."""
    cursor = conexao.cursor()
    cursor.execute("SELECT 1 FROM transacoes WHERE id_transacao = %s", (id_transacao,))
    existe = cursor.fetchone() is not None
    cursor.close()
    return existe


def salvar_transacao(conexao, transacao, alertas):
    
    if len(alertas) > 0:
        status = "SUSPEITA"
    else:
        status = "NORMAL"

    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO transacoes (id_transacao, cliente_id, amount, cidade, data_hora, status) "
        "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id_transacao) DO NOTHING",
        (transacao["id_transacao"], transacao["cliente_id"], transacao["amount"],
         transacao["cidade"], transacao["data_hora"], status),
    )
    for regra in alertas:
        cursor.execute(
            "INSERT INTO alertas_fraude (id_transacao, regra) VALUES (%s, %s) "
            "ON CONFLICT (id_transacao, regra) DO NOTHING",
            (transacao["id_transacao"], regra),
        )
    conexao.commit()   # confirma tudo de uma vez
    cursor.close()
