import pickle
from Exceptions import *
"""
Ce package va permettre aux mineurs de manipuler la blockchain
"""

chemin_liste = "/blockchain/list"  # ce fichier contient la liste des block
chemin_genese = "/blockchain/genese" # ce fichier contient la liste des utilisateurs : c'est le block de genese

#focntion pour ouvrir la liste des block
def open_list_block():
    with open(chemin_liste , 'rb') as list_block :
        pick = pickle.Unpickler(list_block)
        return pick.load()

#focntion pour mettre a jour la liste des blocks
def update_list_block(dictio):
    with open(chemin_liste, "wb") as list_block :
        pick = pickle.Pickler(list_block)
        pick.dump(dictio)

#focntion pour l'ouverture de la liste des utilisateur
def open_genese():
    with open(chemin_liste , 'rb') as list_block :
        pick = pickle.Unpickler(list_block)
        return pick.load()

#focntion pour la mise a jour de la liste des utilisateurs
def update_genese(dictio):
    with open(chemin_liste, "wb") as list_block :
        pick = pickle.Pickler(list_block)
        pick.dump(dictio)

#fonction pour la verification de la presence d'un utilisateur dans le block de genese
def verif_genese(hash):
    genese = open_genese()
    if hash in genese.values() :
        return True
    else:
        return False

#fonction pour la verification de la presence d'un block dans la liste des block
def verif_block(nom):
    liste = open_list_block()
    if nom == liste[len(liste) - 1]:
        return True
    else:
        raise BlockCorrupt

#ajout d'un block
def add_block(nom):

    pass

#mise a jour de la blockchain
def mise_a_jour():
    pass

def block():
    return