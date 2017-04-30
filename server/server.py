# coding: utf-8
''' Api restfull responsavel por fornecer opçoes de
    validaçao de repositorios git hub
'''

from json import dumps, loads
from fnmatch import filter as filtro
from os import popen, system, walk
from shutil import rmtree

from flask import send_from_directory
from flask import Flask

from flask_cors import CORS

from git_utils import git_clone

from usuario import Usuario
from repos import Repos
import banco
import settings


# Servidor HTTP
app = Flask(__name__)
CORS(app)

TEMPLATE_DIR = './templates/'

# Comando a ser executado pelo pylint.
__COMANDO_PYLINT__ = 'pylint --load-plugins=x -f x  --persistent=n --files-output=y {0}'


def registra(nota, url_repos):
    ''' Registra no banco '''

    # Obtem login e nome do repos
    url = url_repos.split('/')
    login = url[-2]
    nome_repos = url[-1]

    # Cadastra ou atualiza nota do usuario.
    banco.register_user(Usuario(login=login))
    print 'imprimindo login do usuario ', login

    # Busca informaçoes do usuario no banco e cadastra repositorio.
    usuario = banco.consulta_usuario_login(login)
    repos = Repos(nome=nome_repos, nota=nota, usuario=usuario.get_cod())

    # if 'Servidor_proxyHTTP' in repos.get_nome():
    #     print '\n\nAumentando minha nota'
    #     repos.set_nota(10)

    if not banco.registra_repos(repos):
        print 'repositorio registrado!'
        if banco.atualiza_repos(repos):
            print 'repositorio atualizado!'


def file_dir(diretorio, ext='py'):
    ''' Retorna uma lista com todos arquivos .py encontrados no
            diretorio e seus subdiretorios(recursivo)
    '''
    results = []
    for root, dirs, files in walk(diretorio):
        for file_ in filtro(files, '*.{}'.format(ext)):
            results.append(root + '/' + file_)

    return results


def formata_json(text):
    ''' Formata objeto JSON '''
    text = text.replace('%', '').replace('=', 'na')
    sep = text.find('{')
    nota = float(text[:sep - 1].split('_')[6].split('/')[0])
    json_arq = loads(text[sep:])
    json_arq['nota'] = nota
    json_arq['statements'] = int(json_arq['statements'].split('_')[0])
    json_arq['err'] = False

    return json_arq


def remove_tmp():
    ''' Remove diretorio e arq temp. '''
    try:
        system('rm *.x')
    except OSError:
        pass
    finally:
        try:
            rmtree('temp')
        except OSError:
            pass


@app.route('/')
def hello_world():
    '''
        Ajuda do programa
    '''
    print TEMPLATE_DIR + 'ajuda.html'
    return send_from_directory(TEMPLATE_DIR, 'ajuda.html')


@app.route('/analysis/<path:url_repos>', methods=['GET'])
def analise(url_repos):
    ''' Retorna a analise do codigo com informaçoes dos erros,
        warnings, etc. encontrado.
    '''

    try:
        # Remove arquivo temporario.
        remove_tmp()

        # Clona repositorio git para pasta especificada.
        git_clone(url_repos, 'temp')
        files_list = ' '.join(file_dir('temp'))

        # Executa comando pylint.
        popen(__COMANDO_PYLINT__.format(files_list)).read()

        text = open('pylint_global.x').read()
        result_js = formata_json(text)

        # Realiza leitura dos erros
        conteudo = ''
        files_list_pylint = file_dir('.', 'x')
        files_list_pylint.remove(u'./pylint_global.x')

        for arq_file in files_list_pylint:
            with open(arq_file) as arq:
                conteudo += arq.read()

        result_js['errors'] = loads(conteudo)

        result_js['files'] = files_list

        # Registra no banco de dados.
        registra(result_js['nota'], url_repos)

        return dumps(result_js)

    except Exception:
        return dumps({'err': True})


@app.route('/ranking', methods=['POST', 'GET'])
def list_all():
    ''' Retorna um json com a lista de todos elementos
            inseridos no banco de dados.
    '''

    lista = banco.get_list_users()

    usuario_list = [
        (
            {
                'id': x.get_cod(),
                'login': x.get_login(),
                'nota': banco.nota_total_usuario(x.get_cod())
            }
        ) for x in lista
    ]

    usuario_list.sort(key=lambda user: user['nota'], reverse=True)

    return dumps(usuario_list)


@app.route('/ranking/repos', methods=['POST', 'GET'])
def list_repos():
    ''' Retorna um json com a lista de todos elementos
            inseridos no banco de dados.
    '''

    lista = banco.get_list_repos()
    lista.sort(key=lambda nota: nota.get_nota(), reverse=True)

    # Cria uma lista com dados do repositorios armazenados no banco.
    repos_list = [
        (
            {
                'nome': repos.get_nome(),
                'nota': repos.get_nota(),

                # Retorna um dict com informaçoes do usuario
                'usuario': (
                    lambda user=banco.consulta_usuario(repos.get_usuario()): (
                        {
                            'id': user.get_cod(),
                            'login': user.get_login()
                        }
                    )
                )()
            }
        ) for repos in lista
    ]

    return dumps(repos_list, indent=4)


@app.route('/del/<string:login>', methods=['DELETE'])
def del_usuario(login):
    ''' Deleta um usuario '''

    return dumps(
        {
            'resultado': True if banco.deleta_usuario(login) else False
        }
    )

if __name__ == '__main__':
    banco.verifica_banco()
    app.run(debug=True, port=settings.PORTA)
