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
grille_joueurs = { # création d'une grille pour chaque joueurs, pour l'exmple
    1: [["?"] * 10 for _ in range(10)],
    2: [["?"] * 10 for _ in range(10)]
}

# On place un navire de 3 cases en (2,2), (2,3), (2,4) sur chaques grilles
grille_joueurs[1][2][2] = grille_joueurs[1][2][3] = grille_joueurs[1][2][4] = "A"
grille_joueurs[2][3][5] = grille_joueurs[2][2][5] = grille_joueurs[2][1][5] = "A"

tour_joueur = 1
lock = Lock() # permet la synchronisation entre les clients
clients = []

def resultat_tir(joueur, x, y):
    """
    Fonction pour transférer le resultat d'un tir

        Arguments:
            -joueur: le numéro du joueur actuel
            -x: l'axe des abscisses
            -y: l'axe des ordonnées

        Retourne:
            -Coulé !: Si toute les parties du navire sont touchées
            -Touché !: Si une partie du navire est touchée
            -Raté...: Si aucun navires n'a été touché par le tir
    """
    grille_du_tour = grille_joueurs[3 - joueur] # définit la grille à utiliser suivant le tour du joueur
    if grille_du_tour[x][y] == "A":
        grille_du_tour[x][y] = "X" #change le A par X si le joueur touche le navire
        navire_coule = True
        for ligne in grille_du_tour: #Vérifie si des cellules A sont encore présentes
            for cellule in ligne:
                if cellule == "A":
                    navire_coule = False
                    break
            if not navire_coule:
                break

        if navire_coule:
            return "Coulé !"
        else:
            return "Touché !"
    else:
        return "Raté..."

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
        client_du_serveur.send("Bienvenue ! La partie va commencer.".encode("utf-8"))
        if autre_client:
            autre_client.send("La partie va commencer !".encode("utf-8"))

#================================================MISE EN PLACE DES TOURS DE JEU================================================
    while True:
        if len(clients) == 2:
            autre_client = clients[1 - (joueur - 1)] 
        else:
            None

        with lock: # permet la syncrhonisation de la variable entre les clients
            if tour_joueur != joueur: # verifie si le tour du joueur correspond à son numéro
                sleep(1)
                client_du_serveur.send("Ce n'est pas votre tour.".encode("utf-8"))
                if autre_client:
                    sleep(1)
                    autre_client.send("C'est votre tour.".encode("utf-8"))

#================================================TRAITEMENT ET RÉPONSE DES ACTIONS EN JEU================================================
        donnée = client_du_serveur.recv(1024).decode()
        if not donnée:
            break

        x, y = map(int, donnée.split(','))
        resultat_tour = resultat_tir(joueur, x, y)
        client_du_serveur.send(resultat_tour.encode("utf-8"))

        if autre_client:
            message = ""
            if resultat_tour == "Raté...":
                message = "Votre adversaire à raté un navire !"
            elif resultat_tour == "Touché !":
                message = "Votre  adversaire a touché un navire !"
            elif resultat_tour == "Coulé !":
                autre_client.send("Votre adversaire à coulé un navire!".encode("utf-8"))
                sleep(1)
                client_du_serveur.send("Vous avez gagné !".encode("utf-8"))
                sleep(1)
                autre_client.send("Vous avez perdu !".encode("utf-8"))
                sleep(1)
                autre_client.send("Fin de la partie. ".encode("utf-8"))
                client_du_serveur.send("Fin de la partie. ".encode("utf-8"))
                break
            autre_client.send(message.encode("utf-8"))


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