#!/usr/bin/python3
"""
Matteo Klimczak
Romane Lassalle
Dimitri Loyer
Yasmine Sassi
"""

from bataille_navale import shootAt, mkGridFromString, updateShoot
from socket import *
from threading import *
from time import sleep # pour mettre un délais d'attente afin de laisser le temps au serveur d'envoyer les messages
import json  # Ajout pour sérialisation/désérialisation des grilles

adresse_serveur = ("127.0.0.1", 12345)
tour_joueur = 1
lock = Lock() # permet la synchronisation entre les clients
clients = []
grilles_des_joueurs =  {}

def resultat_tir(joueur, coord_tir, client_actuel, client_adverse):
    global grilles_des_joueurs
    x, y = coord_tir
    grille_adversaire = list(grilles_des_joueurs[3 - joueur])  # Convertir la chaîne en liste
    index = y * 10 + x

    if grille_adversaire[index] == ".":
        # Raté
        client_actuel.sendall("Raté...".encode("utf-8"))
        client_adverse.sendall(f"L'adversaire a raté son tir.".encode("utf-8"))
        sleep(1)
    elif grille_adversaire[index] != "X":
        # Touché
        bateau_touche = grille_adversaire[index]
        grille_adversaire[index] = "X"  # Marquer le tir
        grilles_des_joueurs[3 - joueur] = ''.join(grille_adversaire)  # Mettre à jour la grille dans le dictionnaire
        client_actuel.sendall("Touché !".encode("utf-8"))
        sleep(1)
        client_adverse.sendall(f"Votre bateau '{bateau_touche}' a été touché !".encode("utf-8"))
        sleep(1)

    grille_mise_a_jour = ''.join(grille_adversaire)
    client_adverse.sendall(grille_mise_a_jour.encode("utf-8"))

     # Vérification si tous les bateaux de l'adversaire sont coulés
    if all(cell in [".", "X"] for cell in grille_adversaire):
        sleep(1)
        client_actuel.sendall("Tout les bateaux de votre adversaire ont été coulé.".encode("utf-8"))
        sleep(1)
        client_adverse.sendall("Tout vos bateaux ont été coulé.".encode("utf-8"))
        sleep(0.5)
        client_actuel.sendall("Vous avez gagné !".encode("utf-8"))
        sleep(0.5)
        client_adverse.sendall("Vous avez perdu !".encode("utf-8"))
        return True  # Fin de partie

    return False  # Partie continue

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
    grilles_des_joueurs[joueur] = grille_recue

    print("La grille du joueur {:d} a été sauvegardée.".format(joueur))
    if len(grilles_des_joueurs) == 2:
        client_du_serveur.send("Tous les bateaux ont été placés, la partie va commencer !".encode("utf-8"))
        sleep(1)
        autre_client.send("Tous les bateaux ont été placés, la partie va commencer !".encode("utf-8"))
        sleep(1)

    # Boucle principale du jeu
    while True:
        if len(clients) == 2:
            autre_client = clients[1 - (joueur - 1)]

        with lock:
            if tour_joueur != joueur:
                sleep(3)
                client_du_serveur.send("Ce n'est pas votre tour.".encode("utf-8"))
                sleep(1)
                if autre_client:
                    autre_client.send("C'est votre tour.".encode("utf-8"))
                    sleep(1)

        coord_tir = client_du_serveur.recv(1024).decode()
        coord_tir_tuple = None
        # Validation et conversion des coordonnées
        if coord_tir != "Le bateau a coulé !":
            print("Le serveur a bien reçu les coordonnées de tir : {}".format(coord_tir))
            try:
                x, y = map(int, coord_tir.split(","))
                coord_tir_tuple = (x, y)
            except ValueError:
                print("Erreur : Coordonnées de tir invalides reçues.")
                client_du_serveur.send("Coordonnées invalides.".encode("utf-8"))
                continue
        else:
            autre_client.send("Vous avez coulé un bateau !".encode("utf-8"))
            sleep(1)

        if coord_tir_tuple:
            partie_termine = resultat_tir(joueur, coord_tir_tuple, client_du_serveur, autre_client)
        else:
            continue  # Si coord_tir_tuple est None, on recommence

        if partie_termine:
            sleep(5)
            break

        with lock:
            tour_joueur = 3 - joueur

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