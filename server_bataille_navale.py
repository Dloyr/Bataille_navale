#!/usr/bin/python3
"""
Matteo Klimczak
Romane Lassalle
Dimitri Loyer
Yasmine Sassi
"""

from bataille_navale import shootAt, mkGridFromString
from socket import *
from threading import *
from time import sleep # pour mettre un délais d'attente afin de laisser le temps au serveur d'envoyer les messages
import json  # Ajout pour sérialisation/désérialisation des grilles

adresse_serveur = ("127.0.0.1", 12345)
tour_joueur = 1
lock = Lock() # permet la synchronisation entre les clients
clients = []
grilles_des_joueurs =  {}

def ajuster_grille(grille):
    """
    Cette fonction prend une grille (liste de listes) et la redimensionne à 10x10.
    Si la grille a moins de 10 lignes ou colonnes, elle sera complétée avec des ".".
    Si elle a plus de lignes ou de colonnes, elle sera tronquée.
    """
    # Compléter ou tronquer les lignes à 10 caractères
    grille = [ligne[:10] for ligne in grille]  # Tronque les lignes trop longues
    grille = [ligne + ['.'] * (10 - len(ligne)) for ligne in grille]  # Complète les lignes trop courtes

    # Compléter ou tronquer le nombre de lignes à 10
    if len(grille) < 10:
        grille.extend([['.'] * 10] * (10 - len(grille)))  # Ajoute des lignes vides
    else:
        grille = grille[:10]  # Tronque les lignes excédentaires

    return grille

def gestion_client(client_du_serveur, joueur):
    global tour_joueur
    autre_client = None

    print("Un joueur s'est connecté en tant que joueur n°{}".format(joueur))
    if len(clients) == 2:
        autre_client = clients[1 - (joueur - 1)]

    # Initialisation des messages pour chaque joueur
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

    # Réception et sauvegarde de la grille
    grille_recue = client_du_serveur.recv(1024).decode()
    grille = mkGridFromString(grille_recue)
    grille = ajuster_grille(grille)

    # Initialisation des bateaux
    bateaux = {}
    for y in range(len(grille)):
        ligne = grille[y]
        for x in range(len(ligne)):
            cell = ligne[x]
            if cell != ".":
                if cell not in bateaux:
                    bateaux[cell] = {"positions": [], "hits": []}
                bateaux[cell]["positions"].append((y, x))

    grilles_des_joueurs[joueur] = {
        "grid": grille,
        "history": [["." for _ in range(10)] for _ in range(10)],
        "boat": bateaux
    }

    print("La grille du joueur {:d} a été sauvegardée.".format(joueur))
    if len(grilles_des_joueurs) == 2:
        client_du_serveur.send("Tous les bateaux ont été placés, la partie va commencer !".encode("utf-8"))
        autre_client.send("Tous les bateaux ont été placés, la partie va commencer !".encode("utf-8"))
        sleep(1)

    # Boucle principale du jeu
    while True:
        if len(clients) == 2:
            autre_client = clients[1 - (joueur - 1)]

        with lock:
            if tour_joueur != joueur:
                client_du_serveur.send("Ce n'est pas votre tour.".encode("utf-8"))
                if autre_client:
                    sleep(1)
                    autre_client.send("C'est votre tour.".encode("utf-8"))

        coord_tir = client_du_serveur.recv(1024).decode()
        print("Le serveur a bien reçu les coordonnées de tir : {}".format(coord_tir))

        # Validation et conversion des coordonnées
        try:
            x, y = map(int, coord_tir.split(","))
            coord_tir_tuple = (x, y)
        except ValueError:
            print("Erreur : Coordonnées de tir invalides reçues.")
            client_du_serveur.send("Coordonnées invalides.".encode("utf-8"))
            continue

        # Appel à la fonction `shootAt`
        resultat_tour = shootAt(
            grilles_des_joueurs[joueur],  # Le joueur qui tire
            grilles_des_joueurs[3 - joueur],  # L'adversaire
            coord_tir_tuple
        )

        # Envoi du résultat au client
        if resultat_tour == 0:
            client_du_serveur.send("Raté !".encode("utf-8"))
        elif resultat_tour == 1:
            client_du_serveur.send("Touché !".encode("utf-8"))
        elif resultat_tour == 2:
            client_du_serveur.send("Coulé !".encode("utf-8"))

        with lock:
            tour_joueur = 3 - joueur

    client_du_serveur.close()
""" 
Bug fin de partie
        # Fin de partie si tous les bateaux sont coulés
        if all(cell == "." for row in grilles_des_joueurs[3 - joueur]["grid"] for cell in row):
            client_du_serveur.send("Vous avez gagné !".encode("utf-8"))
            autre_client.send("Vous avez perdu !".encode("utf-8"))
            break
"""




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