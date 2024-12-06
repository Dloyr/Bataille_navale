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
bateaux_dict = {"C":5, "B":4, "D":3, "S":3, "P":2}
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
                x = int(input(f"Entrez la valeur de x (0, {grille_taille - 1}) : ")) 
                y = int(input(f"Entrez la valeur de y (0, {grille_taille - 1}) : "))
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

def mettre_a_jour_bateaux(bateaux: dict, bateau_touche: str):
    """
    Met à jour le dictionnaire des bateaux en fonction du bateau qui a été touché.
    Si le bateau a coulé, il est retiré du dictionnaire.
    """
    if bateau_touche in bateaux:
        bateaux[bateau_touche] -= 1  # On diminue la taille restante du bateau
        
        # Si la taille du bateau devient 0, il a coulé
        if bateaux[bateau_touche] == 0:
            print(f"Le bateau {bateau_touche} a coulé !")
            del bateaux[bateau_touche]  # Supprimer le bateau du dictionnaire

    return bateaux

with socket(AF_INET, SOCK_STREAM) as client:  # Connexion au serveur de jeu
    client.connect((IP, PORT))
    print("Connecté au serveur.\n")

    joueur = {
        "grid": None,
        "history": [["." for _ in range(taille_grille)] for _ in range(taille_grille)]
    }

    while True:
        message_reçu = client.recv(1024).decode("utf-8")
        print(message_reçu)

        if "Vous pouvez placer vos bateaux." in message_reçu:
            # Placement des bateaux et envoi de la grille au serveur
            grille_double = placement_bateaux(taille_grille, bateaux_dict)

            joueur["grid"] = grille_double
            grille_envoyee = "".join(["".join(row) for row in grille_double])
            client.sendall(grille_envoyee.encode("utf-8"))

        elif "C'est votre tour." in message_reçu:
            # Affiche la grille actuelle avant de jouer
            print("\nVotre grille actuelle :")
            print(playerStr(joueur))

            try:
                coord_char_int = input("Sur quelle cellule souhaitez-vous tirer : ")
                coordonnées = parseCoord(coord_char_int)

                # Validation des coordonnées
                if not (0 <= coordonnées[0] < taille_grille and 0 <= coordonnées[1] < taille_grille):
                    raise ValueError("Coordonnées hors limites.")

                # Envoi des coordonnées au serveur
                str_coord = f"{coordonnées[1]},{coordonnées[0]}"
                client.sendall(str_coord.encode("utf-8"))

                # Réception de la réponse du serveur
                réponse = client.recv(1024).decode("utf-8")
                print(réponse)

                ligne, colonne = coordonnées
                if réponse == "Touché !":
                    joueur["history"][ligne][colonne] = "H"
                elif réponse == "Raté...":
                    joueur["history"][ligne][colonne] = "M"

            except ValueError as e:
                print(f"Erreur : {e}. Réessayez.")
                continue

        elif "Ce n'est pas votre tour." in message_reçu:
            print("En attente que l'adversaire joue...")
            sleep(3)

        elif "gagné" in message_reçu or "perdu" in message_reçu:
            print("Fin de la partie. Déconnexion en cours...")
            sleep(5)
            break

        elif "Votre bateau" in message_reçu:
            for c in message_reçu:
                if c in ["C", "B", "D", "S", "P"]:
                    bateau_touche = c
            bateaux_dict = mettre_a_jour_bateaux(bateaux_dict, bateau_touche)
            if bateau_touche not in bateaux_dict:
                sleep(1)
                client.sendall("Le bateau a coulé !".encode("utf-8"))
                sleep(1)
            
            # Mise à jour de la grille après réception
            grille_mise_a_jour = client.recv(1024).decode("utf-8")
            joueur["grid"] = [
                [grille_mise_a_jour[y * taille_grille + x] for x in range(taille_grille)] for y in range(taille_grille)
            ]
