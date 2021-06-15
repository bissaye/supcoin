from Crypto.PublicKey import RSA
from hashlib import *
import socket
import blockchain
from transaction import *
import string
import random
import pickle
from Exceptions import *
import block
import utilisateur
from threading import Thread

"""
    Cette classe permettra au mineur d'interagir avec l'application
    et de s'aquiter de toutes ses taches
"""


class mineur:
    def __init__(self, id):
        #self.ev est un dictionnaire contenat tous les evenements pouvant etre utiliser dans les sockets
        self.__ev = {
            'new_user': "new_user",
            'trans': "transaction",
            'solde': "solde",
            'hist': "historique",
            'gen':'bloc de genese',

            'up_gen': 'nouveau block de genese',
            'up_block': 'block termine',

            'list_block': 'mise a jour de la liste des blocks',
            'blockchain' : 'information sur un block'
        }
        self.__test = self.test_mineur()
        self.__ip = ""
        self.__port_user = 44444
        self.__port_miner = 33333

        """
            avant tout, il est important de verifier que l'utilisateur est vraiment mineur
            si oui : - il met ses fichiers a jour
                     - ouvre le block encour
                     - puis il ecoute sur le port des mineurs grace a la methode ecoute
            si non, rien ne se passe
        """
        if self.__test == True:
            self.mise_a_jour()
            liste_block = blockchain.open_list_block()
            self.block = block.Block(liste_block[len(liste_block)-1])
            self.ecoute()
        else:
            pass


    """
        cette methode nous permet ed verifier si l'utilisateur courant est mineur ou pas 
        grace a la valeur du booleen contenu dans le fichier test_minuer
    """
    def test_mineur(self):
        try:
            with open('test_mineur', 'rb') as test:
                etat = pickle.loads(test.read())
                if etat == True:
                    return True
                else:
                    return False
        except FileNotFoundError:
            with open('test_mineur', 'wb') as test:
                test.write(pickle.dumps(False))
                return False

    """
        Cette methode permettra au mineur d'ecouter sur le port self.__port_mineur
        les paquet sont differencies dans le reseau par des evenements
        et pour chaque type d'evenement, une suite d'instructions seront executees
    """
    def ecoute(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        client.bind(("", self.__port_miner))

        while True:
            data, addr = client.recvfrom(1024)
            ip, p = addr
            data = pickle.loads(data)
            if data['ev'] == self.__ev['new_user']:
                # si on recoit un paquet avec un evenement de type "new_user", on renvoi au client le retour de la fonction inscription
                client.sendto(pickle.dumps(self.inscription(data['source'])), (ip, self.__port_user))

                #puis on  deploit la mise a jour du block de genese
                packet_mise_a_jour={
                    'ev':self.__ev['up_gen'],
                    'new': data['source'],
                }
                self.update(pickle.dumps(packet_mise_a_jour))

            # cas d'un paquet de type 'trans' : "transaction"
            elif data['ev'] == self.__ev['trans'] :
                client.sendto(pickle.dumps(self.transaction(data['transaction'])), (ip, self.__port_user))

            # cas d'un paquet de type 'solde' : "solde"
            elif data['ev'] == self.__ev['solde'] :
                client.sendto(pickle.dumps(self.solde(data['id'])), (ip, self.__port_user))

            # cas d'un paquet de type 'hist': "historique"
            elif data['ev'] == self.__ev['hist'] :
                client.sendto(pickle.dumps(self.historique(data['id'])), (ip, self.__port_user))

            #cas d'un paquet de type 'gen':'bloc de genese'
            elif data['ev'] == self.__ev['gen'] :
                client.sendto(pickle.dumps(blockchain.open_genese()), (ip, self.__port_user))

            #cas d'un paquet de type
            elif data['ev'] == self.__ev['up_gen'] :
                if data['new'] not in blockchain.open_genese().values():
                    genese = blockchain.open_genese()  # on ouvre le block de genese
                    genese[len(genese)] = data['new']  # on ajoute la nouvelle source
                    blockchain.update_genese(genese)  # et on l'enregistre

            #cas d'un paquet de type 'up_block': 'block termine'
            elif data['ev'] == self.__ev['up_block'] :
                # on verifie si le block en question  n'est pas deja dans la blockchain
                # si non on suit les etapes suivantes:
                if data['new_chain'] not in blockchain.open_list_block().values():

                    #on ouvre le block courant et on tri toutes les transactions qui ne sont pas contenus dans le block recu
                    dictio_actuel = {}
                    self.block.open_block()
                    for i in self.block.dict_file.values():
                        if i not in data['contenu_block']:
                            dictio_actuel[len(dictio_actuel)] = i

                    #on met la blockchain a jour
                    self.block.dict_file = data['contenu_block']
                    self.block.update_block()
                    blockchain.add_block(data['new_chain'],data['contenu_block'])

                    #on ouvre le nouveau block et on y rempli les inforations triees precedemment
                    self.block = block.Block(data['new_queue'])
                    for i in dictio_actuel.values():
                        self.block.add_transaction(Transaction(i['send'], i['recv'], i['amount']))

            #cas d'un paquet de type 'list_block': 'mise a jour de la liste des blocks'
            elif data['ev'] == self.__ev['list_block']:
                client.sendto(pickle.dumps(blockchain.open_genese()), (ip, self.__port_miner))

            #cas d'un paquet de type 'blockchain' : 'information sur un block'
            elif data['ev'] == self.__ev['blockchain']:
                #on verifi si on a le dit block
                if data['nom'] in blockchain.open_list_block().values():
                    #si oui on le renvoi
                    client.sendto(pickle.dumps(blockchain.open_block(data['nom'])), (ip, self.__port_miner))
                else:
                    #si non on se met a jour
                    self.mise_a_jour_liste_block()
                    self.mise_a_jour_blockchain()




    """
        cette methode permet d'inscrir un utilisateur dan le block de genese
    """
    def inscription(self, source):
        self.update(pickle.dumps({'ev': self.__ev['gen']}))   #on s'assure d'abord que le block de genese est a jour
        if blockchain.verif_genese(source) != True :          #on verifie qu'il n'est pas deja dans le block de genese
            genese = blockchain.open_genese()                 #on ouvre le block de genese
            genese[len(genese)] = source                      #on ajoute la nouvelle source
            blockchain.update_genese(genese)                  #et on l'enregistre
            return {'ACK':'ok'}
        else:
            return {'ACK':'error'}




    """
        C'est grace a cette methode qu'on peut in
    """
    def transaction(self, transaction):
        # on verifie d'abord si la transation est valide
        if self.verification(transaction.get_source(), transaction.get_montant()):
            #si la transaction est valide, on essaye d'ajouter la transaction dans le block
            try:
                self.block.add_transaction(transaction)
                return {'ACK': 'ok'}
            except FullBlock:
                #si le block est plein on lance le processus de minage
                self.block.miner()

                #apres le minage, on signale dans le reseau qu'il ya
                packet_block_termine = {
                    'ev': self.__ev['up_block'],
                    'new_chain': self.block.previous_hash,
                    'contenu_block': self.block.open_block(),
                    'new_queue': self.block.get_hash_act()
                }
                self.update(packet_block_termine)

                liste_block = blockchain.open_list_block()
                self.block = block.Block(liste_block[len(liste_block)-1])
                self.block.add_transaction(transaction)
                return {'ACK': 'ok'}
        else:
            return {'ACK': 'error', 'motif':' erreur du reseau'}



    """
         cette methode permettra de claculer le solde d'un utilisateur
    """
    def solde(self, source):
        # on ouvre la liste des blocks
        liste_blocks = blockchain.open_list_block()

        # pour chaque nom contenu dans la liste , on recupere le block correspondant et on li le contenu
        # chaque fois , s'il est un envoyeur , on incremente son solde du montant, dans le cas contraire,
        # on le decremente
        solde = 0
        for i in liste_blocks.values():
            for j in block.Block(hash=i, path="/blockchain").open_block().values():
                if j['send'] == source:
                    solde += j['amount']
                elif j['recv'] == source:
                    solde -= j['amount']
                else:
                    solde = solde

        # on verifie aussi dansle block courant
        for i in self.block.open_block().values():
            if i['send'] == source:
                solde += i['amount']
            elif i['recv'] == source:
                solde -= i['amount']
            else:
                solde = solde

        return {'solde': solde}



    """
        cette methode npermet de connaitre l'historique des transaction d'une source donnee
    """
    def historique(self, source):
        # on ouvre la liste des blocks
        liste_blocks = blockchain.open_list_block()

        # pour chaque nom contenu dans la liste , on recupere le block correspondant et on li le contenu
        # chaque fois , s'il est un envoyeur ou un receveur, onn ajoute la transaction dans la liste des
        # des transactions
        liste_transaction = {}
        for i in liste_blocks.values():
            for j in block.Block(hash=i, path="/blockchain").open_block().values():
                if j['send'] == source:
                    liste_transaction[len(liste_transaction)] = j
                elif j['recv'] == source:
                    liste_transaction[len(liste_transaction)] = j
                else:
                    liste_transaction = liste_transaction


        # on verifie aussi dansle block courant
        for i in self.block.open_block().values():
            if i['send'] == source:
                liste_transaction[len(liste_transaction)] = j
            elif i['recv'] == source:
                liste_transaction[len(liste_transaction)] = j
            else:
                liste_transaction = liste_transaction

        return liste_transaction




    """
        cette methode permet d'envoyer des paquets de mise a jour dans le reseau
        ces paquets sont envoyer uniquements aux mineurs
    """
    def update(self, data):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.settimeout(0.2)
        server.sendto(data, ('<broadcast>', self.__port_miner))



    """
        cette methode permettra de verifier si une source dispose effectivement d'assez d'argent
        pour effectuer une transaction
    """
    def verification(self, source, montant):
        if self.solde(source)['solde'] > montant:
            return True
        else:
            return False


    '''
        grace a cette methode, on pourra mettre a jour tous les fichiers
    '''
    def mise_a_jour(self):

        #d'abord la mise ajour du block de genese
        self.mise_a_jour_gen()

        #puis la liste des blocks
        self.mise_a_jour_liste_block()

        #mise a jour de la blockchain
        self.mise_a_jour_blockchain()


    """
        methode pour la mise a jour du block de genese
    """
    def mise_a_jour_gen(self):
        packet = {
            'ev': self.__ev['gen']
        }
        try:
            connexion = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            connexion.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except:
            return 0

        connexion.settimeout(1)
        connexion.bind(("", self.__port_user))
        connexion.sendto(pickle.dumps(packet), ('<broadcast>', self.__port_miner))
        msg_recu, addr = connexion.recvfrom(1024)

        block_de_genese = pickle.loads(msg_recu)
        blockchain.update_genese(block_de_genese)



    """
    methode pour la mise a jour de la liste des blocks
    """
    def mise_a_jour_liste_block(self):
        packet = {
            'ev': self.__ev['list_block']
        }
        try:
            connexion = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            connexion.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except:
            return 0

        connexion.settimeout(1)
        connexion.bind(("", self.__port_miner))
        connexion.sendto(pickle.dumps(packet), ('<broadcast>', self.__port_miner))
        msg_recu, addr = connexion.recvfrom(1024)

        list_block = pickle.loads(msg_recu)
        blockchain.update_list_block(list_block)

    """
    methode pour la mise a jour de la blockhain
    """
    def mise_a_jour_blockchain(self):

        for block in blockchain.open_list_block().values():
            packet = {
                'ev': self.__ev['blockchain'],
                'nom' : block
            }
            try:
                connexion = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                connexion.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            except:
                return 0

            connexion.settimeout(1)
            connexion.bind(("", self.__port_miner))
            connexion.sendto(pickle.dumps(packet), ('<broadcast>', self.__port_miner))
            msg_recu, addr = connexion.recvfrom(1024)

            blockchain.add_block(block, pickle.loads(msg_recu))
