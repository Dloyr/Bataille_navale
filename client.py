#!/usr/bin/python3
"""
Matteo Klimczak
Romane Lassalle
Dimitri Loyer
Yasmine Sassi
"""

from bataille_navale import playerStr, parseCoord, shootAt
from socket import *
from time import sleep

IP = "127.0.0.1"
PORT = 12345

bateaux_dict = {"C": 5}
taille_grille = 10


def placement_bateaux(grille_taille: int, dict_bateaux: dict[str, int]) -> list:
    grille_str = ["." for _ in range(grille_taille * grille_taille)]
    grille_double = [["." for _ in range(grille_taille)] for _ in range(grille_taille)]

    def afficher_grille(grille):
        print("\n".join("".join(grille[y * grille_taille:(y + 1) * grille_taille]) for y in range(grille_taille)))

    print("Grille initiale :")
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

                if (direction == "h" and x + taille > grille_taille) or \
                   (direction == "v" and y + taille > grille_taille):
                    print("Le bateau dépasse les limites. Réessayez.")
                    continue

                # Vérification des collisions
                collision = any(
                    grille_double[y + (i if direction == "v" else 0)][x + (i if direction == "h" else 0)] != "."
                    for i in range(taille)
                )

                if collision:
                    print("Collision détectée. Réessayez.")
                    continue

                # Placement du bateau
                for i in range(taille):
                    nx = x + (i if direction == "h" else 0)
                    ny = y + (i if direction == "v" else 0)
                    grille_str[ny * grille_taille + nx] = bateau
                    grille_double[ny][nx] = bateau

                afficher_grille(grille_str)
                placé = True
            except (ValueError, IndexError):
                print("Entrée invalide. Réessayez.")

    print("Placement terminé. Voici votre grille finale :")
    afficher_grille(grille_str)
    return grille_double


with socket(AF_INET, SOCK_STREAM) as client:  # Connexion au serveur de jeu
    client.connect((IP, PORT))
    print("Connecté au serveur.\n")

    player = {
        "grid": None,
        "history": [["." for _ in range(taille_grille)] for _ in range(taille_grille)]
    }

    while True:
        message_reçu = client.recv(1024).decode("utf-8")
        print(message_reçu)

        if "Vous pouvez placer vos bateaux." in message_reçu:
            # Placement des bateaux et envoi de la grille au serveur
            grille_double = placement_bateaux(taille_grille, bateaux_dict)

            player["grid"] = grille_double
            grille_envoyee = "".join(["".join(row) for row in grille_double])
            client.sendall(grille_envoyee.encode("utf-8"))

        elif message_reçu == "C'est votre tour.":
            sleep(1)
            print(playerStr(player))

            try:
                coord_char_int = input("Sur quelle cellule souhaitez-vous tirer : ")
                coordonnées = parseCoord(coord_char_int)

                # Validation des coordonnées
                if not (0 <= coordonnées[0] < taille_grille and 0 <= coordonnées[1] < taille_grille):
                    raise ValueError("Coordonnées hors limites.")

                str_coord = f"{coordonnées[0]},{coordonnées[1]}"
                client.sendall(str_coord.encode("utf-8"))

                colonne = ord(coord_char_int[0].upper()) - ord("A")
                ligne = int(coord_char_int[1])
                tuple_coord = (colonne, ligne)
                print(f"Tir effectué à : {tuple_coord}")

            except ValueError as e:
                print(f"Erreur : {e}. Réessayez.")
                continue

        elif message_reçu == "Ce n'est pas votre tour.":
            print("En attente que l'adversaire joue...")
            sleep(3)

        elif "gagné" in message_reçu or "perdu" in message_reçu:
            print(message_reçu)
            print("Déconnexion en cours...")
            break

        elif message_reçu == "Fin de la partie.":
            print("Partie terminée.")
            break
