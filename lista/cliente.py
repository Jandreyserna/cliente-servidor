import zmq
import sys
import hashlib

class Cliente:
    contexto = zmq.Context()
    def __init__(self, server):
        self.server = server
        self.opcion = ''
        self.socket_1 = self.contexto.socket(zmq.REQ)

    def menu(self):
        opcion = 0 
        while int(opcion) < 1 or int(opcion) > 2:
            print('_____Bienvenido Cliente_______')
            print('¿Qué desea hacer?')
            print('1. subir un archivo')
            print('2. Descargar un archivo')
            opcion = input('Digite su opcion: ')
        if int(opcion) == 1 :
            self.opcion = input('Digite el nombre del archivo: ')
            self.hashear()
    
    def hashear(self):
        tokens = hashlib.sha1()
        tokens.update(self.opcion.encode('utf-8'))
        token = int(tokens.hexdigest(), 16)
        print(token)

    

if __name__ == '__main__':
    server_port = sys.argv[1]
    cliente = Cliente(server_port)
    cliente.menu()

