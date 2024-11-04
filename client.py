#!/usr/bin/python3
"""
Matteo Klimczak
Romane Lassalle
Dimitri Loyer
Yasmine Sassi
"""

from socket import *

IP = "127.0.0.1"
PORT = 12345

def cible():
    """Fonction pour définir la position sur laquelle on souhaite tirer"""
    x = int(input("Entrez la coordonnée x du tir (0-9): "))
    y = int(input("Entrez la coordonnée y du tir (0-9): "))

    return f"{x},{y}"

with socket(AF_INET, SOCK_STREAM) as client: #Connexion au serveur de jeu
    client.connect((IP, PORT))
    print("Connecté au serveur.\n")

    while True:
        message_reçu = client.recv(1024).decode("utf-8")
        print(message_reçu)

        if message_reçu == "C'est votre tour.": #tire quand c'est son tour
            coordonnées = cible()
            client.sendall(coordonnées.encode("utf-8"))
        elif message_reçu == "Ce n'est pas votre tour.":
            continue
        elif message_reçu == "Fin de la partie. ":
            print("Déconnexion en cours...")
            break