import pickle
import random
import zmq
import sys
import hashlib
import string

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

    def escuchar(self):
        self.socket_1.bind(self.url_bind)
        while True:
            llega = self.socket_1.recv_multipart()
            print(llega[0].decode())
            """ averiguar si es el encargado del limite del token """
            if llega[0].decode() == 'preguntar_limite':
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
                    self.sigt = llega[2]
                    self.socket_1.send_multipart(
                        [
                            'si'.encode(),
                            pickle.dumps(limiteRespuesta),
                            pickle.dumps(siguiente),
                            pickle.dumps(self.puerto),
                        ]
                    )
                elif int(separado[1]) < tokenConsul:
                    self.limite = '(,'+str(tokenConsul)+',&,)'
                    limiteRespuesta = '[,'+separado[1]+','+str(tokenConsul)+',]'
                    anterior = self.ant
                    self.ant = llega[2]
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
            print(self.limite)

    
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
        self.limite = pickle.loads(llega[1])
        self.sigt = pickle.loads(llega[2])
        self.ant = pickle.loads(llega[3])
        print(pickle.loads(llega[1]))
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



