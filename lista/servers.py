import pickle
import random
import zmq
import sys
import hashlib
import string
import os
import shutil

class Servidor:
    contexto = zmq.Context()

    def __init__(self, url_bind, url_connect, puerto, token, limite, sigt, ant):
        self.url_bind = url_bind
        self.url_connect = url_connect
        self.puerto = puerto
        self.sigt = sigt
        self.ant = ant
        self.token = token
        self.limite = limite
        self.socket_1 = self.contexto.socket(zmq.REP)
        self.socket_2 = self.contexto.socket(zmq.REQ)

    def crear_file(self, token):
        directory = os.getcwd()
        directory += '/'+str(token) 
        os.mkdir(directory)
    
    def añadir_server(self, llega):
        tokenConsul = pickle.loads(llega[1])
        separado = self.limite.split(',')
        print(self.limite)
        operador = separado[2]
        print(operador)
        if str(operador) != '&':
            if tokenConsul < int(separado[2]) and tokenConsul > int(separado[1]):
                if self.token == separado[2]: 
                    """Cuando   """
                    self.limite = '(,'+str(tokenConsul)+','+self.token+',]'
                    limiteRespuesta = separado[0]+','+separado[1]+','+str(tokenConsul)+']'
                    anterior = self.ant
                    self.ant = pickle.loads(llega[2])
                    self.socket_1.send_multipart(
                        [
                            'si'.encode(),
                            pickle.dumps(limiteRespuesta),
                            pickle.dumps(self.puerto),
                            pickle.dumps(anterior),
                        ]
                    )
                elif self.token > tokenConsul:
                    self.limite = '(,'+str(tokenConsul)+','+separado[2]+','+separado[3]
                    limiteRespuesta = separado[0]+','+separado[1]+','+str(tokenConsul)+',]'
                    anterior = self.ant
                    self.ant = pickle.loads(llega[2])
                    self.socket_1.send_multipart(
                        [
                            'si'.encode(),
                            pickle.dumps(limiteRespuesta),
                            pickle.dumps(self.puerto),
                            pickle.dumps(anterior),
                        ]
                    )
                            
                else:
                    self.limite = separado[0]+','+separado[1]+','+str(tokenConsul)+',)'
                    limiteRespuesta = '[,'+str(tokenConsul)+','+separado[2]+','+separado[3]
                    siguiente = self.sigt
                    self.sigt = pickle.loads(llega[2])
                    self.socket_1.send_multipart(
                        [
                            'si'.encode(),
                            pickle.dumps(limiteRespuesta),
                            pickle.dumps(siguiente),
                            pickle.dumps(self.puerto),
                        ]
                    )
            elif tokenConsul < int(separado[2]):
                self.socket_1.send_multipart(
                    [
                        'no'.encode(),
                        pickle.dumps(self.ant),
                    ]
                )
            else:
                self.socket_1.send_multipart(
                    [
                        'no'.encode(),
                        pickle.dumps(self.sigt),
                    ]
                )
        elif tokenConsul > self.token:
            self.limite = '[,'+separado[1]+','+str(tokenConsul)+',)'
            limiteRespuesta = '[,'+str(tokenConsul)+',&,)'
            siguiente = self.sigt
            self.sigt = pickle.loads(llega[2])
            self.socket_1.send_multipart(
                [
                    'si'.encode(),
                    pickle.dumps(limiteRespuesta),
                    pickle.dumps(siguiente),
                    pickle.dumps(self.puerto),
                ]
            )
        elif int(separado[1]) < tokenConsul:
            print(self.ant)
            self.limite = '(,'+str(tokenConsul)+',&,)'
            limiteRespuesta = '[,'+separado[1]+','+str(tokenConsul)+',]'
            anterior = self.ant
            self.ant = pickle.loads(llega[2])
            self.socket_1.send_multipart(
                [
                    'si'.encode(),
                    pickle.dumps(limiteRespuesta),
                    pickle.dumps(self.puerto),
                    pickle.dumps(anterior),                        
                ]
            )
        else:
            self.socket_1.send_multipart(
                [
                    'no'.encode(),
                    pickle.dumps(self.ant),
                ]
            )
        

    def escuchar(self):
        self.socket_1.bind(self.url_bind)
        ''' llamar la funcion de crear carpeta '''
        self.crear_file(self.token)
        while True:
            print('inicio dede aca')
            llega = self.socket_1.recv_multipart()
            print('llegue aca')
            print(llega[0].decode())
            """ averiguar si es el encargado del limite del token """
            if llega[0].decode() == 'preguntar_limite':
                self.añadir_server(llega)
                print(self.limite)
            elif llega[0].decode() == 'preguntar_encargado':
                """ averiguar que server es encargado del token enviado """
                tokenPregunta = pickle.loads(llega[1])
                limite = self.limite.split(',')
                if limite[2] != '&':
                    if tokenPregunta <= int(limite[2]) and tokenPregunta >= int(limite[1]):
                        if llega[4].decode() != 'descargar':
                            self.subir_archivo(llega)
                        else:
                            self.bajar_archivo(llega)
                        self.socket_1.send_multipart(
                            [
                                'si'.encode(),
                                pickle.dumps(self.puerto)
                            ]
                        )
                    elif tokenPregunta < int(limite[1]):
                        print('entre a la segunda opcion')
                        self.socket_1.send_multipart(
                            [
                                'no'.encode(),
                                pickle.dumps(self.ant)
                            ]
                        )
                    else:
                        print('entre a la tercera opcion')
                        self.socket_1.send_multipart(
                            [
                                'no'.encode(),
                                pickle.dumps(self.sigt)
                            ]
                        )
                elif int(limite[1]) <= tokenPregunta:
                    print('si la devuelvo')
                    if llega[4].decode() != 'descargar':
                        self.subir_archivo(llega)
                    else:
                        self.bajar_archivo(llega)
                    
                    self.socket_1.send_multipart(
                            [
                                'si'.encode(),
                                pickle.dumps(self.puerto)
                            ]
                        )
                else:
                    print('entre ultima opcion')
                    self.socket_1.send_multipart(
                            [
                                'no'.encode(),
                                pickle.dumps(self.ant)
                            ]
                        )
    
    def subir_archivo(self, llega):
        nameArchivo = pickle.loads(llega[1])
        arc = open(os.getcwd() + '/' + str(self.token) + '/' + str(nameArchivo) ,'wb')
        arc.write(llega[3])
        arc.close()
    
    def bajar_archivo(self, llega):
        shutil.copy( str(self.token) + '/' + str(pickle.loads(llega[1])), 'descargas/'+pickle.loads(llega[2]))
    
    def preguntar(self):
        self.socket_2 = self.contexto.socket(zmq.REQ)
        self.socket_2.connect(self.url_connect)
        self.socket_2.send_multipart(
            [
                'preguntar_limite'.encode(),
                pickle.dumps(self.token),
                pickle.dumps(self.puerto)
            ]
        )
        llega = self.socket_2.recv_multipart()
        self.socket_2.disconnect(self.url_connect)
        if llega[0] == 'no':
            self.url_connect = 'tcp://localhost:' + str(pickle.loads(llega[1]))
            self.preguntar()
        else:
            self.limite = pickle.loads(llega[1])
            self.sigt = pickle.loads(llega[2])
            self.ant = pickle.loads(llega[3])
            self.escuchar()




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
        limite = '[,0,&,)'
        server = Servidor(url_bind, url_connect, puerto, token, limite, sigt, ant)
        server.escuchar()
    else:
        url_bind = 'tcp://*:' + str(puerto)
        url_connect = 'tcp://localhost:' + str(estado)
        server = Servidor(url_bind, url_connect, puerto, token, '', 0, 0)
        server.preguntar()



