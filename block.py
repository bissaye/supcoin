from transaction import *
import os
import pickle
from Exceptions import *
import hashlib
import itertools
from blockchain import *
import datetime

"""
Cette classe nous permet au mineur :
    - de creer des blocs
    - de creer des files d'attentes
    - d'ajouter des transactions dans une file d'attente
    - d'ajouter des transactions dans un bloc
    - de verifier le nombre de transaction par bloc
    - de miner
"""
class Block:
    def __init__(self, hash):
        self.cle = ""                # la cle qui permet de verouiller un bloc
        self.cota = 10               # cette variable defini le nombre de transactions permises par blocs
        self.previous_hash = hash    # cette variable est le hash du bloc precedent et par consequent le titre du bloc actuel
        self.path = "/c"             # chemin vers le bloc
        self.dict_file = {}          # dictionnaire qui va nous permettre de traiter les données du bloc
        self.hash_act = ""           # le hash du bloc actuel, c'est lui qu'on devra calculer
        self.alp = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                    'u','v', 'w', 'x', 'y', 'z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R',
                    'S','T','U','V','W','X','y','Z','1', '2', '3', '4', '5', '6', '7', '8', '9', '0', ',', '.', '/','<',
                    ">","?",'"', "'", ':', ';', '[', '{', '}', ']', "\/", "|", "*", "-", "+", "/", "+", "_", ")", "(",
                    "&", "^","%","$", "#", "@", "!", "`", "~"]
                                     # cet alphabet va nous servir pour le calcul de la cle


    #verification de la validite de la cle
    def verification_cle(self, cle):
        if hashlib.sha256((self.hash_act + cle).encode()).hexdigest()[:3] == "000":
            return True
        else:
            return False
    #mise a jour du  bloc
    def mise_a_jour(self):
        pass

    #creation de file d'attente
    def new_queue(self):
        pass
    #creation d'un nouveau bloc
    def nouveau(self):
        pass

    """
        cette fonction nous permet d'ouvrir le bloc et d'extirper les données sous forme de dictionnaire 
        dans notre variable self.dict_file
        
        on renvoi une erreur de type BlocknotFound si le block n'existe pas
    """
    def open_block(self):
        if os.path.exists(self.path):
            with open(self.path, 'rb') as block:
                pickl = pickle.Unpickler(block)
                self.dict_file = pickl.load()
        else:
            raise BlockNotFound(self.path)


    """
        cette fonction nous permet d'ouvrir le bloc et d'ecraser les données qui sont à l'interieur pour
        les remplacer par les données contenues dans notre variable self.dict_file

    """
    def update_block(self):
        with open(self.path, 'wb') as block:
            pickl = pickle.Pickler(block)
            pickl.dump(self.dict_file)

    """
        cette fonction nous permet d'ajouter une nouvelle transaction
    """
    def add_transaction(self, transaction:Transaction):
        # on ouvre tout d'abord le bloc, et on lance la mise a jour s'il n'y a pas de bloc
        try:
            self.open_block()
        except BlockNotFound:
            self.mise_a_jour()

        # verifi maintenant que le bloc n'est pas plein, si oui on lance le minage et sinon  on ajoute la tranaction
        try:
            if len(self.dict_file) == self.cota:
                raise FullBlock()
            else:
                self.dict_file[str(len(self.dict_file))] = {"send": transaction.get_source(), "recv": transaction.get_dest(), "amount": int(transaction.get_montant()),"date-time": str(datetime.datetime.now())}
                self.update_block()
        except FullBlock:
            self.miner()
            self.new_queue()


    """
        Cette fonction permet au mineur de faire le minage comme suit:
        - on calcul d'abord le hash actuel du bloc "self.hash_act"
        - on parcoure toutes les combinaisons de lettres possibles de notre alphabet telle que
          nous obtenions un mot "cle" tel que hash( self.hash_act + cle) == un hash commencant par "000"
    """
    def miner(self):
        # ouverture du bloc
        self.open_block()

        #calcul du hash actuel
        self.hash_act = hashlib.sha256(str(self.dict_file ).encode()).hexdigest()

        # variable de control dont la valeur est False tant que la cle n'est pas trouvee
        trouve = False

        # on entre dans la boucle pour la recherche de la cle
        while not trouve:
            for i in range(0, len(self.alp[0])):
                for test in itertools.combinations_with_replacement(self.alp[0], i):
                    # print("".join(test))  #pour afficher les essais
                    if self.verification_cle("".join(test)):
                        self.cle = "".join(test)
                        self.compteur = 1
                        break
                if self.compteur != 0:
                    trouve = True
                    break

        # on verifie une fois de plus si la cle est bonne ,dans le cas contraire on reprend le minage
        if self.verification_cle(self.cle):
            self.fin()
            return self.cle
        else:
            return self.miner()


    """
        cette  fonction permet de verouiller le bloc en mettant comme derniere entree dans sont dictionnaire:
        - le hash du bloc actuel
        - et la cle
        
        cette fonction appelle auusi la blcochain qui va ajouter le bloc
        
        on ouvre en suite un nouveau bloc ou un recupere un dans la fille d'attente 
    """
    def fin(self):
        if self.verification_cle(self.cle):
            self.open_block()
            self.dict_file[str(len(self.dict_file))] = {"hash": self.hash_act, "cle": self.cle, "date-time": str(datetime.datetime.now())}
            self.update_block()
            add_block(self.previous_hash)
            return True
        else:
            return False