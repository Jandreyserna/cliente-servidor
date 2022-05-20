import zmq
import sys
import hashlib
import os
import pickle

class Cliente:
    
    def __init__(self, url_connect ):
        self.server = url_connect 
        self.opcion = ''
        self.archivo = ''
        self.tamaño = 1024*1024*50
        self.contexto = zmq.Context()
        self.socket_1 = self.contexto.socket(zmq.REQ)

    def menu(self):
        opcion = 0 
        while int(opcion) < 1 or int(opcion) > 2:
            print('_____Bienvenido Cliente_______')
            print('¿Qué desea hacer?')
            print('1. subir un archivo')
            print('2. Descargar un archivo')
            opcion = input('Digite su opcion: ')
            os.system('cls')
        if int(opcion) == 1 :
            self.opcion = input('Digite el nombre del archivo: ')
            self.hashear()
            self.preguntar_server_encargado()
            
    
    def hashear(self):
        tokens = hashlib.sha1()
        tokens.update(self.opcion.encode('utf-8'))
        token = int(tokens.hexdigest(), 16)
        self.token = token


    def preguntar_server_encargado(self):
        arc = open(self.opcion, 'rb')
        self.archivo = arc.read(self.tamaño)
        print(self.server)
        arc.close()
        self.socket_1.connect(self.server)
        self.socket_1.send_multipart(
            [
                'preguntar_encargado'.encode(),
                pickle.dumps(self.token),
                pickle.dumps(self.opcion),
                self.archivo,
                
            ]
        )
        llega = self.socket_1.recv_multipart()
        
        if llega[0].decode() == 'no':
            self.socket_1.disconnect(self.server)
            print(self.token)
            print(llega[0].decode())
            self.server = 'tcp://localhost:' + str(pickle.loads(llega[1]))
            self.socket_1 = self.contexto.socket(zmq.REQ)
            self.preguntar_server_encargado()
        else:
            self.menu()
    
if __name__ == '__main__':
    server_port = sys.argv[1]
    url_connect = 'tcp://localhost:' + str(server_port )
    cliente = Cliente(url_connect )
    cliente.menu()

