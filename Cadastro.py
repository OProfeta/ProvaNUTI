import sqlite3
import datetime
import os

mydb = sqlite3.connect("bancoVoos.db", check_same_thread=False)
mycursor = mydb.cursor()

class DataErro(Exception):
    pass

class CidadeErro(Exception):
    pass

class ExisteErro(Exception):
    pass

class MesmaCidadeErro(Exception):
    pass

class HorarioErro(Exception):
    pass

def existe(tabela, iden):

    mycursor.execute(f"SELECT * FROM {tabela} WHERE id = ?", (iden,))
    if len(mycursor.fetchall()) > 0:
        return True
    else:
        return False


def inserirVoo(idAviao, idCidadeOrigem, idCidadeDestino, ano, mes, dia, horario, duracao):
    sql = "INSERT INTO voo (idAviao, idCidadeOrigem, idCidadeDestino, ano, mes, dia, horario, duracao) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    val = (idAviao, idCidadeOrigem, idCidadeDestino, ano, mes, dia, horario, duracao)
    mycursor.execute(sql, val)
    mydb.commit()


def validaData(ano, mes, dia, anoAnt, mesAnt, diaAnt, horario, horarioAnt, duracaoAnt):

    dataPouso = datetime.datetime(anoAnt, mesAnt, diaAnt, hour=horarioAnt)
    duracaoVoo = datetime.timedelta(hours=duracaoAnt)
    dataPouso = dataPouso + duracaoVoo
    dataDecolagem = datetime.datetime(ano, mes, dia, hour=horario)

    return dataPouso < dataDecolagem


def CadastrarVoo(idAviao, idCidadeOrigem, idCidadeDestino, ano, mes, dia, horario, duracao):
    """
    Verifica se o voo eh valido. Caso seja, realiza a entrada do voo no banco.
    Caso nao seja valido, retorna um erro
    """

    if duracao < 1:
        raise HorarioErro("oxi")

    if idCidadeDestino == idCidadeOrigem:
        raise MesmaCidadeErro("Voo nao pode ir de uma cidade para a mesma cidade em um unico voo")

    if existe("aviao", idAviao) and existe("cidade", idCidadeOrigem) and existe("cidade", idCidadeDestino):
        # verificar se esse eh o primeiro voo do aviao
        mycursor.execute("SELECT * FROM voo WHERE idAviao = ?", (idAviao,))
        linhas = mycursor.fetchall()

        if len(linhas) == 0:
            # primeiro voo do aviao
            inserirVoo(idAviao, idCidadeOrigem, idCidadeDestino, ano, mes, dia, horario, duracao)
            return
        else:
            # pegar o ultimo voo
            linha = linhas[-1]

            # verificar se o aviao esta na cidade de origem
            if idCidadeOrigem == linha[3]:

                if validaData(ano, mes, dia, linha[4], linha[5], linha[6], horario, linha[7], linha[8]):
                    inserirVoo(idAviao, idCidadeOrigem, idCidadeDestino, ano, mes, dia, horario, duracao)
                    return
                else:
                    raise DataErro("Voo esta marcado para o passado")
            else :
                raise CidadeErro("Aviao nao esta na cidade de origem")
    else:
        raise ExisteErro("Aviao e/ou Cidade Origem e/ou Cidade Destino nao existe(m)")

def CadastrarAviao(nome):
    """
    Verifica se nao ha um aviao com o mesmo nome no banco.
    """

    mycursor.execute("SELECT * FROM aviao WHERE nome = ?", (nome,))
    linhas = mycursor.fetchall()

    if len(linhas) == 0:
        # nao ha aviao com esse nome
        mycursor.execute("INSERT INTO aviao (nome) VALUES (?)", (nome,))
        mydb.commit()
        return
    else:
        raise ExisteErro("Aviao com o mesmo nome ja cadastrado")

def CadastrarCidade(nome):
    """
    Verifica se nao ha uma cidade com o mesmo nome no banco.
    """

    mycursor.execute("SELECT * FROM cidade WHERE nome = ?", (nome,))
    linhas = mycursor.fetchall()

    if len(linhas) == 0:
        # nao ha cidade com esse nome
        mycursor.execute("INSERT INTO cidade (nome) VALUES (?)", (nome,))
        mydb.commit()
        return
    else:
        raise ExisteErro("Cidade com o mesmo nome ja cadastrada")



def PrepararBanco():
    """
    Caso seja a primeira vez entrando no site, cria as tabelas e insere
    alguns dados de exemplo
    """

    # Cria as tabelas (caso elas nao existam)
    mycursor.execute("CREATE TABLE IF NOT EXISTS cidade (id INTEGER PRIMARY KEY, nome VARCHAR(255))")
    mycursor.execute("CREATE TABLE IF NOT EXISTS aviao (id INTEGER PRIMARY KEY, nome VARCHAR(255))")
    mycursor.execute("CREATE TABLE IF NOT EXISTS voo (id INTEGER PRIMARY KEY,"+
                                                    " idAviao INTEGER REFERENCES aviao(id),"+
                                                    " idCidadeOrigem INTEGER REFERENCES cidade(id),"+
                                                    " idCidadeDestino INTEGER REFERENCES cidade(id),"+
                                                    " ano INTEGER, mes INTEGER, dia INTEGER, horario INTEGER, duracao INTEGER)")

    # se as tabelas cidade e aviao estiverem vazias, criar alguns dados de exemplos
    mycursor.execute("SELECT * FROM aviao")
    linhasAviao = mycursor.fetchall()
    mycursor.execute("SELECT * FROM cidade")
    linhasCidade = mycursor.fetchall()

    if len(linhasAviao) == 0 and len(linhasCidade) == 0:

        for i in range(2):
            sql = "INSERT INTO aviao (nome) VALUES (?)"
            val = ("Aviao{}".format(i+1),)
            mycursor.execute(sql, val)

        for i in range(4):
            sql = "INSERT INTO cidade (nome) VALUES (?)"
            val = ("Cidade{}".format(i+1),)
            mycursor.execute(sql, val)

        mydb.commit()


def TodosOsVoos():
    """
    Retorna todos os voos
    """
    sql = "SELECT * FROM voo"
    mycursor.execute(sql)
    voos = mycursor.fetchall()
    return voos

def TodosOsAvioes():
    """
    Retorna todos os avioes
    """
    sql = "SELECT * FROM aviao"
    mycursor.execute(sql)
    avioes = mycursor.fetchall()
    print(avioes)
    return avioes

def TodasAsCidades():
    """
    Retorna todas as cidades
    """
    sql = "SELECT * FROM cidade"
    mycursor.execute(sql)
    cidades = mycursor.fetchall()
    return cidades

def PegarAviao(idAviao):
    """
    Retorna aviao cujo id = idAviao
    """
    mycursor.execute("SELECT * FROM aviao WHERE id = ?", (idAviao,))
    aviao = mycursor.fetchall()
    return aviao

def PegarCidade(idCidade):
    """
    Retorna Cidade cujo id = idCidade
    """
    mycursor.execute("SELECT * FROM cidade WHERE id = ?", (idCidade,))
    cidade = mycursor.fetchall()
    return cidade

def EditarAviao(idAviao, novoNome):
    """
    Troca o nome do aviao de id = idAviao
    """

    mycursor.execute("SELECT * FROM aviao WHERE nome = ?", (novoNome,))
    linhas = mycursor.fetchall()

    if len(linhas) == 0:
        # nao ha aviao com esse nome
        sql = "UPDATE aviao SET nome = ? WHERE id = ?"
        val = (novoNome, idAviao,)
        mycursor.execute(sql, val)
        mydb.commit()
        return
    else:
        raise ExisteErro("Aviao com o mesmo nome ja cadastrado")

def EditarCidade(idCidade, novoNome):
    """
    Troca o nome do Cidade de id = idCidade
    """

    mycursor.execute("SELECT * FROM cidade WHERE nome = ?", (novoNome,))
    linhas = mycursor.fetchall()

    if len(linhas) == 0:
        # nao ha Cidade com esse nome
        sql = "UPDATE cidade SET nome = ? WHERE id = ?"
        val = (novoNome, idCidade,)
        mycursor.execute(sql, val)
        mydb.commit()
        return
    else:
        raise ExisteErro("Cidade com o mesmo nome ja cadastrada")

