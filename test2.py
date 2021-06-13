import socket
import transaction
import pickle

hote = ''
port = 12000
connexion_principale = socket.socket(socket.AF_INET,
socket.SOCK_STREAM)
connexion_principale.bind((hote, port))
connexion_principale.listen(5)
print("Le serveur écoute à présent sur le port {}".format(port))
connexion_avec_client, infos_connexion = connexion_principale.accept()

msg_recu = pickle.loads(connexion_avec_client.recv(1024))
# L'instruction ci-dessous peut lever une exception si lemessage
# Réceptionné comporte des accents
print(msg_recu['ev'])
print(msg_recu)

if msg_recu['ev'] == "transaction":
    connexion_avec_client.send(b"ok")
    print("envoi de ok")
else:
    connexion_avec_client.send(b"erroe")
    print("envoi de error")

print("Fermeture de la connexion")
connexion_avec_client.close()
connexion_principale.close()