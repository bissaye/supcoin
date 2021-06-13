from transaction import *
import json
import socket
from Exceptions import  *
import pickle


def envoyer(dest, montant):
    envoi = Transaction("sdfgdfgd", dest, montant)
    packet = {
        'ev': 'transaction',
        'transaction': envoi
    }
    try:
        connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connexion.connect(('localhost', 12000))
        print("demarrage de la connexion")
    except:
        print("erreur connexion")
        raise ConnexionError()


    connexion.send(pickle.dumps(packet))
    print("envoi reussi")
    print(f'message recu : {connexion.recv(512).decode()}')

envoyer("sdsd", 121221)