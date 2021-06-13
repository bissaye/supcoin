from Crypto.PublicKey import RSA
from hashlib import *
import socket
import blockchain
from transaction import *
import string
import random
import pickle
from Exceptions import *

"""
    cette classe contient toutes les methodes qui permettrons aux utilisateurs 
    d'interagir avec l'application
"""

class Utilisateur:
    def __init__(self,PATH ,inscription=None):
        """

        :param PATH: chemin vers les fichiers contenant les cles
        :param inscription: booleen permettant de determiner si l'utilisateur est inscrit ou pas
        """
        self.chemin = PATH
        self.fichier_public = "/public.pem"
        self.fichier_privee = "/privee.pem"

        if inscription == True:

            """
                si l'utilisateur n'est pas encore inscri, on genere un paire de cle
                puis on execute la methode inscription
            """

            self.key = RSA.generate(1024)
            self.inscription()
        else:

            """
                Si par contre l'utilisateur est deja inscri, on ouvre le fichier contenant sa cle publique 
                pour mettre cette cle dans la variable self.public
            """

            try:
                with open(self.chemin+self.fichier_public , 'r') as pub:
                    publ = pub.read()
                    pub.close()

                self.public= RSA.importKey(publ)
                self.public_hash = sha256(self.public.exportKey()).hexdigest()
            except:
                self.public_hash = ""
                self.public=""

        #self.ev est un dictionnaire contenat tous les evenements pouvant etre utiliser dans les sockets
        self.ev = {
            'trans': "transaction",
            'solde': "solde",
            'hist': "historique",
            'new_user': "new_user"
        }

        # l'adresse du reseau
        self.ip_reseau = ""

    def inscription(self):

        #on recupere la cle publique dans la variable self.public et le hash dans self.public_hash
        self.public = self.key.publickey()
        self.public_hash = sha256(self.public.exportKey()).hexdigest()

        #on enregistre les cles dans les fichiers qu'on va creer dans le chemin self.chemin
        with open(self.chemin+self.fichier_public, 'w') as pub:
            pub.write(self.public.exportKey('PEM').decode())
            pub.close()
        with open(self.chemin+self.fichier_privee, 'w') as priv:
            priv.write(self.key.exportKey('PEM').decode())
            priv.close()

        """
            on elabore maintenant un paquet de type "new_user" destine au mineur pour qu'il puisse
            l'enregistrer dans le bloc de genese, et l'envoi dans le reseau
        """
        packet = {
            'ev': self.ev['new_user'],
            'source': self.public_hash
        }

        try:
            connexion = socket.socket(socket.AF_INET,  socket.SOCK_STREAM)
            connexion.connect((self.ip_reseau, 12000))
        except:
            raise ConnexionError()

        connexion.send(pickle.dumps(packet))
        msg_recu = pickle.loads(connexion.recv(1024))
        return msg_recu


    def authentication(self):
        """
            il s'agira ici de verifier que l'utilisateur en question dispose de la cle privee correspondante

            on va recuperer la cle prive dans le fichier self.fichier_privee contenu dans le chemin entree au depart
            puis pour verifier, on va crypter une chaine de caractere random avec la cle publique et essayer de verifier si
            c'est le meme message qu'on obtient une fois qu'on le decrypte avec la cle privee
        """
        with open(self.chemin+self.fichier_privee , 'r') as pk:
            priv = pk.read()
            pk.close()

        private = RSA.importKey(priv)

        test = "".join(random.choice(string.ascii_letters) for i in range(20)).encode()
        test_encrypt = self.public.encrypt(test)
        if test == private.decrypt(test_encrypt) :
            if blockchain.verif_genese(self.public_hash) == True:
                return True
            else:
                return False
        else:
            return False





    def envoyer(self, dest, montant):
        """
        c'est grace a cette methode que l'utilisateur va pouvoir effectuer des transactions
        il va pour cela creer un objet de type transaction, puis constituer un paquet avec l'evenement "trans",
        puis l'envoyer via la socket dans le reseau

        :param dest: hash_public du destinataire
        :param montant: montant de la transaction
        :return: un dictionnaire de la forme {AKC:'OK ou error',  motif: ' trans effectuee ou erreur montant, destinatire ...' }
        """
        envoi = Transaction(self.public_hash, dest, montant)
        packet = {
            'ev': self.ev['trans'],
            'transaction': envoi
        }
        try:
            connexion = socket.socket(socket.AF_INET,  socket.SOCK_STREAM)
            connexion.connect((self.ip_reseau, 12000))
        except:
            raise ConnexionError()

        connexion.send(pickle.dumps(packet))
        msg_recu = pickle.loads(connexion.recv(1024))
        return msg_recu

    def solde(self):
        """
        permet de consulder le solde
        :return: solde
        """
        packet = {
            'ev': self.ev['solde'],
            'id': self.public_hash
        }
        try:
            connexion = socket.socket(socket.AF_INET,  socket.SOCK_STREAM)
            connexion.connect((self.ip_reseau, 12000))
        except:
            raise ConnexionError()

        connexion.send(pickle.dumps(packet))
        msg_recu = pickle.loads(connexion.recv(1024))
        return msg_recu

    def historique(self):
        """
        permet d'afficher l'historique
        :return: dictionnaire contenant l'historiqe
        """
        packet = {
            'ev': self.ev['hist'],
            'id': self.public_hash
        }
        try:
            connexion = socket.socket(socket.AF_INET,  socket.SOCK_STREAM)
            connexion.connect((self.ip_reseau, 12000))
        except:
            raise ConnexionError()

        connexion.send(pickle.dumps(packet))
        msg_recu = pickle.loads(connexion.recv(1024))
        return msg_recu



