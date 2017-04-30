# coding: utf-8
''' Responsavel pela manipulaçao do banco de dados '''

from os import path
from sqlite3 import connect
from sqlite3 import IntegrityError
from settings import _ARQUIVO_BANCO_
from usuario import Usuario
from repos import Repos


def verifica_banco():
    ''' Checa se o banco de dados já foi criado caso nao tenha cria.'''

    if not path.isfile(_ARQUIVO_BANCO_):
        conn = connect(_ARQUIVO_BANCO_)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE usuario (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                login TEXT NOT NULL UNIQUE
            );
        ''')

        cursor.execute('''
            CREATE TABLE repos (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                nota REAL NOT NULL,
                id_usuario INTEGER NOT NULL,
                FOREIGN KEY(id_usuario) REFERENCES usuario(id) ON DELETE CASCADE,
                UNIQUE (nome, id_usuario)
            );
        ''')
        conn.close()


def register_user(usuario):
    ''' Armazena nota no banco de dados'''

    try:
        conn = connect(_ARQUIVO_BANCO_)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usuario (login)
            VALUES ("%s")''' % (usuario.get_login())
                      )
        conn.commit()
        return True
    except IntegrityError:
        return False
    finally:
        conn.close()


def registra_repos(repos):
    ''' Registra o repositorio no banco de dados '''
    try:
        conn = connect(_ARQUIVO_BANCO_)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO repos (nome, nota, id_usuario)
            VALUES ( '%s', '%f', '%d')''' % (
                repos.get_nome(), repos.get_nota(), repos.get_usuario()
            )
                      )
        conn.commit()
    except IntegrityError:
        return False
    finally:
        conn.close()


def atualiza_repos(repos):
    ''' atualiza o repositorio no banco de dados '''
    try:
        conn = connect(_ARQUIVO_BANCO_)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE repos 
            SET nome='%s', nota='%f'
            WHERE id_usuario='%d' ''' % (
                repos.get_nome(), repos.get_nota(), repos.get_usuario()
            )
                      )
        conn.commit()
    except IntegrityError:
        return False
    finally:
        conn.close()


def deleta_usuario(login):
    ''' Deleta um usuario do banco de dados '''

    try:
        con = connect(_ARQUIVO_BANCO_)
        cursor = con.cursor()

        # adicionando suporte chaves estrangeiras.
        cursor.execute("PRAGMA foreign_keys = on")
        cursor.execute(
            'DELETE  FROM usuario WHERE login = "%s"' % (login)
        )

        con.commit()
        return True
    except IntegrityError:
        print 'Uusuario n~ao deletado'
        return False
    finally:
        con.close()


def consulta_usuario_login(login):
    ''' Retorna a consulta de uma usuario, caso exista '''

    usuario = None
    con = connect(_ARQUIVO_BANCO_)
    cursor = con.cursor()
    cursor.execute('SELECT * from usuario WHERE login = "%s"' % (login))

    for row in cursor.fetchall():
        usuario = Usuario(row[0], row[1])
    con.close()
    return usuario


def consulta_usuario(cod):
    ''' Retorna a consulta de uma usuario, caso exista '''
    usuario = None
    con = connect(_ARQUIVO_BANCO_)
    cursor = con.cursor()
    cursor.execute('SELECT * from usuario WHERE id = "%s"' % (cod))

    for row in cursor.fetchall():
        usuario = Usuario(row[0], row[1])
    con.close()
    return usuario


def nota_total_usuario(id_usuario):
    ''' Retorna todas notas armazenadas no banco '''
    nota = 0
    con = connect(_ARQUIVO_BANCO_)
    cursor = con.cursor()
    cursor.execute(
        'SELECT (sum(nota) / count(nota)) FROM repos WHERE id_usuario = "%d"' % (id_usuario))

    for row in cursor.fetchall():
        nota = round(row[0], 2)

    con.close()
    return nota


def get_list_users():
    ''' Retorna todas notas armazenadas no banco '''
    usuario_list = []
    con = connect(_ARQUIVO_BANCO_)
    cursor = con.cursor()
    cursor.execute('SELECT * from usuario')

    for row in cursor.fetchall():
        usuario_list.append(Usuario(cod=row[0], login=row[1]))

    con.close()
    return usuario_list


def get_list_repos():
    ''' Retorna todas notas armazenadas no banco '''
    repos_list = []
    con = connect(_ARQUIVO_BANCO_)
    cursor = con.cursor()
    cursor.execute('SELECT * from repos')

    for row in cursor.fetchall():
        repos_list.append(
            Repos(nome=row[1], nota=row[2], usuario=row[3])
        )

    con.close()
    return repos_list
