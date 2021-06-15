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

        #self.ev est un dictionnaire contenat tous les evenements pouvant etre utiliser dans les sockets
        self.__ev = {
            'new_user': "new_user",
            'trans': "transaction",
            'solde': "solde",
            'hist': "historique",
            'gen':'bloc de genese',
        }
        self.__chemin = PATH
        self.__fichier_public = "/public.pem"
        self.__fichier_privee = "/privee.pem"
        self.__ip_reseau = "" #l'adresse du reseau
        self.__port_user = 44444
        self.__port_miner = 33333
        self.key = ""
        if inscription == True:

            """
                si l'utilisateur n'est pas encore inscri on execute la methode inscription
            """


            self.inscription()
        else:

            """
                Si par contre l'utilisateur est deja inscri, on ouvre le fichier contenant sa cle publique 
                pour mettre cette cle dans la variable self.public
            """

            try:
                with open(self.__chemin + self.__fichier_public , 'r') as pub:
                    publ = pub.read()
                    pub.close()

                self.__public= RSA.importKey(publ)
                self.__public_hash = sha256(self.__public.exportKey()).hexdigest()
            except:
                self.__public_hash = ""
                self.__public= ""




    def inscription(self):
        # on genere d'abord la paure de cle
        self.__key = RSA.generate(1024)

        #on recupere la cle publique dans la variable self.public et le hash dans self.public_hash
        self.__public = self.__key.publickey()
        self.__public_hash = sha256(self.__public.exportKey()).hexdigest()

        #on enregistre les cles dans les fichiers qu'on va creer dans le chemin self.chemin
        with open(self.__chemin + self.__fichier_public, 'w') as pub:
            pub.write(self.__public.exportKey('PEM').decode())
            pub.close()
        with open(self.__chemin + self.__fichier_privee, 'w') as priv:
            priv.write(self.__key.exportKey('PEM').decode())
            priv.close()

        """ 
            on elabore maintenant un paquet de type "new_user" destine au mineur pour qu'il puisse
            l'enregistrer dans le bloc de genese, et l'envoi dans le reseau
        """
        packet = {
            'ev': self.__ev['new_user'],
            'source': self.__public_hash
        }


        if pickle.loads(self.requete(packet))['ACK']== True:
            return True
        else :
            return self.inscription()


    def authentication(self):

        self.bloc_de_genese()
        """
            il s'agira ici de verifier que l'utilisateur en question dispose de la cle privee correspondante

            on va recuperer la cle prive dans le fichier self.fichier_privee contenu dans le chemin entree au depart
            puis pour verifier, on va crypter une chaine de caractere random avec la cle publique et essayer de verifier si
            c'est le meme message qu'on obtient une fois qu'on le decrypte avec la cle privee
        """
        with open(self.__chemin + self.__fichier_privee , 'r') as pk:
            priv = pk.read()
            pk.close()

        private = RSA.importKey(priv)

        test = "".join(random.choice(string.ascii_letters) for i in range(20)).encode()
        test_encrypt = self.__public.encrypt(test)
        if test == private.decrypt(test_encrypt) :
            self.bloc_de_genese()
            if blockchain.verif_genese(self.__public_hash) == True:
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
        envoi = Transaction(self.__public_hash, dest, montant)
        packet = {
            'ev': self.__ev['trans'],
            'transaction': envoi
        }

        return self.requete(pickle.dumps(packet))

    def solde(self):
        """
        permet de consulder le solde
        :return: solde
        """
        packet = {
            'ev': self.__ev['solde'],
            'id': self.__public_hash
        }
        return self.requete(pickle.dumps(packet))

    def historique(self):
        """
        permet d'afficher l'historique
        :return: dictionnaire contenant l'historiqe
        """
        packet = {
            'ev': self.__ev['hist'],
            'id': self.__public_hash
        }

        return self.requete(pickle.dumps(packet))

    def bloc_de_genese(self):
        """
        grace acette methode , on peut mettre a jour le block de genese
        """
        packet = {
            'ev': self.__ev['gen']
        }
        block_de_genese = self.requete(pickle.dumps(packet))
        blockchain.update_genese(pickle.loads(block_de_genese))

    def requete(self, data):
        """
        cette classe permettra le le transfert des messages dans le reseau
        :param data:
        :return:
        """
        try:
            connexion = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            connexion.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except:
            raise ConnexionError()

        connexion.settimeout(10)
        connexion.bind(("", self.__port_user))
        connexion.sendto(data, ('<broadcast>', self.__port_miner))
        msg_recu , addr = connexion.recvfrom(1024)
        return msg_recu
