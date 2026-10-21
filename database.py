import psycopg2


def conectar():
    conexao = psycopg2.connect(
        host="localhost",
        port=5433,
        dbname="fraudes",
        user="postgres",
        password="postgres",
    )
    return conexao


def transacao_existe(conexao, id_transacao):
    cursor = conexao.cursor()
    cursor.execute("SELECT id_transacao FROM transacoes WHERE id_transacao = %s", (id_transacao,))
    resultado = cursor.fetchone()
    cursor.close()

    if resultado is None:
        return False
    else:
        return True


def salvar_transacao(conexao, transacao, alertas):
    if len(alertas) > 0:
        status = "SUSPEITA"
    else:
        status = "NORMAL"

    cursor = conexao.cursor()

    cursor.execute(
        "INSERT INTO transacoes (id_transacao, id_cliente, valor, country, city, hora, status) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (transacao["id_transacao"], transacao["id_cliente"], transacao["valor"],
         transacao["country"], transacao["city"], transacao["hora"], status),
    )

    for regra in alertas:
        cursor.execute(
            "INSERT INTO alertas_fraude (id_transacao, regra) VALUES (%s, %s)",
            (transacao["id_transacao"], regra),
        )

    conexao.commit()
    cursor.close()


def marcar_suspeita(conexao, id_transacao, regra):
    cursor = conexao.cursor()

    cursor.execute("UPDATE transacoes SET status = 'SUSPEITA' WHERE id_transacao = %s", (id_transacao,))

    cursor.execute(
        "INSERT INTO alertas_fraude (id_transacao, regra) VALUES (%s, %s) "
        "ON CONFLICT (id_transacao, regra) DO NOTHING",
        (id_transacao, regra),
    )

    conexao.commit()
    cursor.close()
