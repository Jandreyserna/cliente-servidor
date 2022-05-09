import random
import zmq
import sys
import hashlib
import string

class Servidor:
    contexto = zmq.Context()
    """ primer = '5555' """

    def __init__(self, url_bind, url_connect, puerto, sigt, ant, token):
        self.url_bind = url_bind
        self.url_connect = url_connect
        self.puerto = puerto
        self.sigt = sigt
        self.ant = ant
        self.token = token

    def iniciar(self):
        



if __name__ == '__main__':
    """ creo una cadena de 160 bits """
    letra = ''
    palabra = ''
    for i  in  range(160):
        letra = random.choice(string.ascii_letters)
        palabra += letra

    tokens = hashlib.sha1()
    tokens.update(palabra.encode('utf-8'))
    token = int(tokens.hexdigest(), 16)
    estado = sys.argv[1]
    puerto = sys.argv[2]
    if (estado == 'first'):
        url_bind = 'tcp://*:' + str(puerto)
        url_connect = 'tcp://localhost:' + str(puerto)
        sigt = puerto
        ant = puerto
        server = new Servidor(url_bind, url_connect, puerto, sigt, ant, token)
        server.iniciar()



