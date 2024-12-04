#!/usr/bin/python3
"""
Matteo Klimczak
Romane Lassalle
Dimitri Loyer
Yasmine Sassi
"""

from bataille_navale import playerStr
from socket import *
from time import sleep
IP = "127.0.0.1"
PORT = 12345

bateaux_dict = {"C":5}
taille_grille  = 10

def placement_bateaux(grille_taille: int, dict_bateaux: dict[str, int]) -> list:
    grille_str = "." * (grille_taille ** 2)  # grille originale du joueur sous forme de chaine
    grille_double = [["." for _ in range(grille_taille)] for _ in range(grille_taille)]

    def afficher_grille(grid):
        for x in range(grille_taille):
            print("".join(grid[x * grille_taille:(x + 1) * grille_taille]))

    # Afficher la grille initiale
    afficher_grille(grille_str)

    for bateau, taille in dict_bateaux.items():
        print(f"\nPlacement du bateau '{bateau}' de taille {taille} :")
        placé = False

        while not placé:
            try:
                x = int(input(f"Entrez l'abscisse (1-{grille_taille}) : ")) - 1
                y = int(input(f"Entrez l'ordonnée (1-{grille_taille}) : ")) - 1
                direction = input("Direction (h pour horizontal, v pour vertical) : ").lower()

                if direction not in ["h", "v"]:
                    print("Direction invalide. Réessayez.")
                    continue

                if direction == "h" and x + taille > grille_taille:
                    print("Le bateau dépasse à droite. Réessayez.")
                    continue
                if direction == "v" and y + taille > grille_taille:
                    print("Le bateau dépasse en bas. Réessayez.")
                    continue

                # Vérification des collisions
                collision = False
                for i in range(taille):
                    index = (y * grille_taille + x + i) if direction == "h" else ((y + i) * grille_taille + x)
                    if grille_str[index] != ".":
                        collision = True
                        break

                if collision:
                    print("Collision détectée. Réessayez.")
                    continue

                # Placement du bateau
                for i in range(taille):
                    if direction == "h":
                        index = (y * grille_taille + x + i)
                    else:
                        index = ((y + i) * grille_taille + x)

                    # met a jour la chaine de caractère et la grille double
                    grille_double[index // grille_taille][index % grille_taille] = bateau

                grille_str = "".join(["".join(rang) for rang in grille_double])
                placé = True

                afficher_grille(grille_str)

            except ValueError:
                print("Entrée invalide. Réessayez.")

    print("\nGrille finale après placement des bateaux :")
    afficher_grille(grille_str)
    return grille_double

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

        if "Vous pouvez placer vos bateaux." in message_reçu:
            grille_double = placement_bateaux(taille_grille, bateaux_dict)
            # créer un joueur pour garder une trace de ce qu'il sait passer sur sa grille et permettre l'affichage des deux grilles en même temps
            player = {
                "grid": grille_double,
                "history": [["." for _ in range(taille_grille)] for _ in range(taille_grille)]
            }
            client.sendall("".join(["".join(rang) for rang in grille_double]).encode("utf-8"))
        elif message_reçu == "C'est votre tour.": #tire quand c'est son tour:
            sleep(1)
            print(playerStr(player))
            coordonnées = cible()
            client.sendall(coordonnées.encode("utf-8"))
        elif message_reçu == "Ce n'est pas votre tour.":
            print("En attente que l'adversaire joue...")
            sleep(300)
        elif message_reçu == "Fin de la partie. ":
            print("Déconnexion en cours...")
            break