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

bateaux_dict = {"C":5}
taille_grille  = 10

def placement_bateaux(grille_taille: int, dict_bateaux: dict[str, int]) -> str:
    grille_str = "." * (grille_taille ** 2)  # Représente la grille 10x10 sous forme d'une chaîne de 100 caractères

    def afficher_grille(grid):
        for x in range(grille_taille):
            print(grid[x * grille_taille:(x + 1) * grille_taille])

    # Afficher la grille initiale
    afficher_grille(grille_str)

    for bateau, taille in dict_bateaux.items():
        print(f"\nPlacement du bateau '{bateau}' de taille {taille} :")
        placé = False

        while not placé:
            try:
                # Coordonnées de départ
                x = int(input(f"Entrez l'abscisse (1-{grille_taille}) : ")) - 1
                y = int(input(f"Entrez l'ordonnée (1-{grille_taille}) : ")) - 1
                direction = input("Direction (h pour horizontal, v pour vertical) : ").lower()

                if direction not in ["h", "v"]:
                    print("Direction invalide. Réessayez.")
                    continue

                # Vérification des limites
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
                temp = list(grille_str)
                for i in range(taille):
                    if direction == "h":
                        index = (y * grille_taille + x + i)
                    else: 
                        index = ((y + i) * grille_taille + x)

                    temp[index] = bateau

                grille_str = "".join(temp)
                placé = True  # Le bateau a été placé avec succès

                # Afficher la grille après placement
                afficher_grille(grille_str)

            except ValueError:
                print("Entrée invalide. Réessayez.")

    print("\nGrille finale après placement des bateaux :")
    afficher_grille(grille_str)
    return grille_str

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
            grille = placement_bateaux(taille_grille, bateaux_dict)
            client.sendall(grille.encode("utf-8"))
        elif message_reçu == True:
            client.sendall("OK".encode("utf-8"))
        elif message_reçu == False:
            grille = placement_bateaux(taille_grille, bateaux_dict)
            client.sendall(grille.encode("utf-8"))
        elif message_reçu == "C'est votre tour.": #tire quand c'est son tour
            coordonnées = cible()
            client.sendall(coordonnées.encode("utf-8"))
        elif message_reçu == "Ce n'est pas votre tour." or message_reçu == "En attente que l'autre joueur ait placé ses bateaux...":
            continue
        elif message_reçu == "Fin de la partie. ":
            print("Déconnexion en cours...")
            break