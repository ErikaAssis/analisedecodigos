# coding: utf-8
''' Esta classe usada para representar um usuario '''


class Repos(object):
    ''' Classe que representa o usuario'''

    def __init__(self, cod=None, nome=None, nota=None, usuario=None):
        ''' Inicializa as variaveis '''
        self.__cod = cod
        self.__nome = nome
        self.__nota = nota
        self.__usuario = usuario

    def set_cod(self, cod):
        ''' Modifica o codigo '''
        self.__cod = cod

    def get_cod(self):
        ''' retorna o codigo '''
        return self.__cod

    def set_nome(self, nome):
        ''' Modifica o nome '''
        self.__nome = nome

    def get_nome(self):
        ''' Retorna o nome '''
        return self.__nome

    def set_nota(self, nota):
        ''' Modifica nota '''
        self.__nota = nota

    def get_nota(self):
        ''' Retorna nota '''
        return self.__nota

    def set_usuario(self, usuario):
        ''' Modifica usuario '''
        self.__usuario = usuario

    def get_usuario(self):
        ''' Retorna o usuario '''
        return self.__usuario
