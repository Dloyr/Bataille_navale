#!/usr/bin/python3
"""
Matteo Klimczak
Romane Lassalle
Dimitri Loyer
Yasmine Sassi
"""

from socket import *
from threading import *
from time import sleep # pour mettre un délais d'attente afin de laisser le temps au serveur d'envoyer les messages

adresse_serveur = ("127.0.0.1", 12345)
tour_joueur = 1
lock = Lock() # permet la synchronisation entre les clients
clients = []
grilles_des_joueurs =  {}

def gestion_client(client_du_serveur, joueur):
    """
    Permet au serveur de gérer le bon déroulement de la partie

        Arguments:
        -client_du_serveur: Représente l'un des joueurs du serveur
        -joueur: le numéro du joueur

    """
    global tour_joueur
    autre_client = None
#================================================INITIALISATION DE LA PARTIE================================================
    print("Un joueur s'est connecté en tant que joueur n°{}".format(joueur))
    if len(clients) == 2:
        autre_client = clients[1 - (joueur - 1)] 

    if joueur == 1:
        client_du_serveur.send("Bienvenue, ! En attente d'un second joueur...".encode("utf-8"))
    else:
        client_du_serveur.send("Bienvenue dans la Bataille Navale !".encode("utf-8"))
        sleep(1)
        client_du_serveur.send("Vous pouvez placer vos bateaux.".encode("utf-8"))
        if autre_client:
            autre_client.send("Un joueur a été trouvé !".encode("utf-8"))
            sleep(1)
            autre_client.send("Vous pouvez placer vos bateaux.".encode("utf-8"))

    grille = client_du_serveur.recv(1024).decode()
    grilles_des_joueurs[joueur] = grille

    print("La grille du joueur {:d} a été sauvegardé.".format(joueur))
    if not grille:
        return

    if len(grilles_des_joueurs) == 2:
        client_du_serveur.send("Tout les bateaux ont été placé, la partie va commencer !".encode("utf-8"))
        autre_client.send("Tout les bateaux ont été placé, la partie va commencer !".encode("utf-8"))
        sleep(1)
    else:
        sleep(300)
#================================================DEBUT DE LA PARTIE================================================
    while True:
        if len(clients) == 2:
            autre_client = clients[1 - (joueur - 1)] 
        else:
            None

        with lock: # permet la syncrhonisation de la variable entre les clients
            if tour_joueur != joueur: # verifie si le tour du joueur correspond à son numéro
                client_du_serveur.send("Ce n'est pas votre tour.".encode("utf-8"))
                if autre_client:
                    sleep(1)
                    autre_client.send("C'est votre tour.".encode("utf-8"))

#================================================TRAITEMENT ET RÉPONSE DES ACTIONS EN JEU================================================
        
        with lock:
            tour_joueur = 3 - joueur #permet de changer le tour

    client_du_serveur.close()



serveur = socket(AF_INET, SOCK_STREAM) # Configuration du serveur (IPv4 et TCP)
serveur.bind(adresse_serveur) #Ouverture du serveur
print("== LE SERVEUR EST CONNECTÉ ==")
print()

serveur.listen(2) # Analyse des connexions au serveur
print("Recherche de clients en cours...")
print()

for joueur in [1, 2]:
    client_du_serveur, adresse = serveur.accept()
    clients.append(client_du_serveur)
    Thread(target=gestion_client, args=(client_du_serveur, joueur)).start()