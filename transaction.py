import os
"""
Permet de creer des transaction
"""
class Transaction :

    def __init__(self, source, dest , montant):
        self.__source = source
        self.__dest = dest
        self.__montant = int(montant)
    def get_source(self):
        return self.__source

    def get_dest(self):
        return self.__dest

    def get_montant(self):
        return self.__montant

    def __str__(self):
        return f"source: {self.__source}\ndestinataire: {self.__dest}\nmontant: {self.__montant}"