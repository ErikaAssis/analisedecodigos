# coding: utf-8
''' Esta classe usada para representar um usuario '''


class Usuario(object):
    ''' Classe que representa o usuario'''

    def __init__(self, cod=None, login=None):
        self.__login = login
        self.__cod = cod

    def set_cod(self, cod):
        ''' Modifica o cod '''
        self.__cod = cod

    def get_cod(self):
        ''' retorna o codigo '''
        return self.__cod

    def set_login(self, login):
        ''' Modifica login '''
        self.__login = login

    def get_login(self):
        ''' Retorna login '''
        return self.__login
