import sys

# We encode the knowledge a player has from the game in a dictionary `player` as follows:
# - player["grid"] encodes the grid the player is playing with
# - player["history"] encodes the history of moves player by the player
# - player["boat"] keeps track of the damages on each boat of the player
# - player["nboat"] keeps track of the number of undestroyed boats on the board
# 
# Each boat is represented by one letter :
#
# - the carrier (size 5) is denoted with letter C
# - the battle ship (size 4) is denoted with letter B
# - the destroyer (size 3) is denoted with letter D
# - the submarine (size 3) is denoted with letter S
# - the patrol boat (size 2) is denoted with letter P

# More details now:
# - player["grid"] is a 10x10 string list such that player["grid"][i][j] is:
#   - "." if the cell (i,j) is empty
#   - "x" if the cell contains a boat that has been hit by the other player
#   - "C" (resp "N","D","S","P") if the carrier is at position (i,j) and has not yet been hit. 
# - player["history"] is a 10x10 string list such that player["history"][i][j] is:
#   - "?" if the player has not yet shot at position (i,j)
#   - "M" if the player has shot at position (i,j) and missed
#   - "H" if the player has shot at position (i,j) and hit
# - player["boat"] is a dictionary such that player["boat"][L] is the number of cells not hit for the boat denoted by letter L. For example, at start, player["boat"]["C"] is 5 because the carrier is unhit and has size 5. If the other player hits the carrier once, then player["boat"]["C"] is decreased to 4.

# Here are some general values for the game

boatSizes = {"C":5, "B":4, "D":3, "S":3, "P":2}
gridsize  = 10

# We now give functions to update and built player's datastructures:

def checkGrid(grid):
    """
    Input: `grid` is a string (gridsize × gridsize) list.
    Output: True if it represents a valid grid and False otherwise.
    It checks that every boat are on the board, with the right number of cells and are positionned in one vertical or horizontal block
    
    For example, a grid
        ...C..BBBB
        ...C......
        ...C......
        ...C......
        ...C......
        DDD.....PP
        ..........
        .....S....
        .....S....
        .....S....
    is valid while
        ...C..BBBB
        ..........
        ...C......
        ...C......
        ...C......
        DDDC....PP
        ..........
        .....S....
        .....S....
        .....S....
    is not valid, since the carrier is not contiguous.
    """
    
    
    dBoatPos = {} # Maps Boats names to ordered list of positions
                  # Example: dBoatPos["P"] = [(5,8), (5,9)]
    dPosBoat = {} # Maps positions to name of Boats
                  # Example: dPosBoat[(5,8)] = "P"

    # Check number of rows
    if len(grid) != gridsize:
        return False
        
    # READ THE GRID
    for i,l in enumerate(grid):
        # Check number of columns
        if len(l) != gridsize:
            return False
        # Read the line
        for j,v in enumerate(l):
            # A boat with letter v is on the current cell (i,j)
            if v in boatSizes.keys():
                # First time a boat is seen, we initialise dBoatPos[v] to the empty list
                if v not in dBoatPos:
                    dBoatPos[v] = []
                # Add new position
                dBoatPos[v].append((i,j))
                # Reverse mapping: at cell (i,j), boat v is present
                dPosBoat[(i,j)] = v
                # No boat on the current cell, check that cell contains "." 
            elif v != ".":
                return False
                

        # CHECK THE GRID AND SORT 
        # Check that every boat are placed on the grid
    if dBoatPos.keys() != boatSizes.keys():
        return False

    for v in dBoatPos.keys():
        # Check that the boat has the right size
        if len(dBoatPos[v]) != boatSizes[v]:
            return False
        # Sort the positions
        dBoatPos[v].sort()
        # Check that boat is aligned
        if len(dBoatPos[v]) > 1:
                # Check whether the boat is x-aligned (orientation = 0) or y-aligned (orientation = 1)
                # by comparing the two first cells
            orientation = 0
            if dBoatPos[v][0][0] == dBoatPos[v][1][0]:
                orientation = 0
            elif dBoatPos[v][0][1] == dBoatPos[v][1][1]:
                orientation = 1
            else:
                return False # not aligned

            # Check that the next position 
            for k in range(len(dBoatPos[v])-1):
                if (dBoatPos[v][k][1-orientation]+1 != dBoatPos[v][k+1][1-orientation]) or\
                   (dBoatPos[v][k][orientation] != dBoatPos[v][k+1][orientation]):
                    return False
    return True

def mkGridFromString(s):
    """
    Builds the grid from a string of the form. Returns a (gridsize × gridsize) array. 
        ...C..BBBB
        ...C......
        ...C......
        ...C......
        ...C......
        DDD.....PP
        ..........
        .....S....
        .....S....
        .....S....
    Trailing empty lines are allowed.
    """

    return [[c for c in row] for row in s.strip("\n").split("\n")]

def mkGridFromPos(boatPos):
    """Builds the grid from a dictionnary containing the list of positions of each boat. Example :
    {
      'C': [(0, 3), (1, 3), (2, 3), (3, 3), (4, 3)],
      'B': [(0, 6), (0, 7), (0, 8), (0, 9)],
      'D': [(5, 1), (5, 2), (5, 3)],
      'P': [(5, 8), (5, 9)],
      'S': [(6, 5), (7, 5), (8, 5)]
    }
    /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\
    The function will not complain if two boats sit on the same cell,
    please use checkGrid to check that the grid is correct.
    /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ 

    """
    grid = [["." for i in range(gridsize)] for j in range(gridsize)]
    for v in boatPos:
        for (i,j) in boatPos[v]:
            grid[i][j]=v
    return grid


# Creates a new player from its grid.
def mkPlayer(grid):
    """Input: `grid` is a (gridsize × gridsize) list representing the
    player's grid (ideally created through mkGridFromPos or
    mkGridFromString functions.

    Output: A dictionary describing a player as explained in the
    beginning of the file, initialized with grid `grid`. If the grid is
    not valid, it raises ValueError exception.
    """
    player = {}
    if checkGrid(grid):
        player["grid"] = grid
        player["history"] = [["?" for i in range(gridsize)] for j in range(gridsize)]
        player["boat"] = boatSizes.copy()
        player["nboat"] = len(boatSizes)

        return player
    else:
        raise ValueError

def updateShoot(player, coord):
    """Input: `player` is a dictionary representing a player and
    `coord` a tuple of size 2 representing a cell in the board.
    
    Output: Returns 0 if the shot missed (no boat at position `coord`), 1 if it hits a boat and 2 if it sinks a boat.

    Side effect: Updates player["boat"] if the shot hit.  Raise ValueError is coord is not valid. 
    """
    (i,j) = coord
    if i>=gridsize or j>=gridsize:
        raise ValueError

    v = player["grid"][i][j]
    if v in player["boat"]:
        player["grid"][i][j] = "x" # shot this part of the grid
        player["boat"][v] -= 1
        if player["boat"][v] == 0: # the boat is sunk
            player["nboat"] -= 1
            return 2
        else:
            return 1 # hit but not sunk
    else:
        return 0 # missed

def shootAt(player1, player2, coord):
    """Input: `player1` and `player2` are two dicts representing two
    players. `coord` a tuple of size 2 representing a cell in the
    board.

    Output: Returns 0 if the shot from player1 to player2 missed (no
    boat at position `coord`), 1 if it hits a boat and 2 if it sinks a
    boat.

    Side effect: updates the history of player1 and the boat states of player2.
    """
    (i,j) = coord
    if i>=gridsize or j>=gridsize:
        raise ValueError

    # Shoot at player2 and updates
    r = updateShoot(player2, coord) 

    # Update player1 history
    if r==0:
        player1["history"][i][j] = "M" 
    elif r>0:
        player1["history"][i][j] = "H"
        
    return r
    
def playerStr(player):
    """
    Returns a string representing player grid on screen and history of moves against adversary
    """
    colidx = ' '.join([chr(j) for j in range(65, 65+gridsize)])
    tbl = (len(colidx)+3)

    state = "="*tbl+"\t\t"+"="*tbl+"\n"
    state += "     GRILLE JOUEUR    \t\t    GRILLE ADVERSE  \n"
    state += "="*tbl+"\t\t"+"="*tbl+"\n"
    state += f" |{colidx} \t\t |{colidx}\n"
    state += "-"*tbl+"\t\t"+"-"*tbl+"\n"

    for i in range(gridsize):
        state += f"{i}|"
            
        # Print grid line
        for j in range(gridsize):
            state += player["grid"][i][j]+" "
                    
        state += "\t\t"
        state += f"{i}|"

        # Print history line
        for j in range(gridsize):
            state += player["history"][i][j]+" "
        state += "\n"
    state += "="*tbl+"\t\t"+"="*tbl+"\n"

    return state


def parseCoord(c):
    """
    Parse inputs of the form B7 (returns (1,6) in this case
    """
    if len(c) != 2 or c[0] not in [chr(j) for j in range(65, 65+gridsize)] or int(c[1]) not in range(gridsize):
        raise ValueError
    else:
        return (int(c[1]), ord(c[0])-ord("A"))



def parseArg(args):
    """
    Parse command line arguments and return dictionaries representing players grid. 
    """
    if (len(args) != 3):
        print(f"{args[0]} grille1.txt grille2.txt")
        exit(0)
    else:
        players = []
        for i in range(1,3):
            with open(args[i]) as g:
                grid = mkGridFromString(g.read())
                players.append(mkPlayer(grid))
        return players



def main():
    players = parseArg(sys.argv) # load files for two players
    current_player = 0 # current player is player 0
    
    c = "" # input from user
    
    while(c!="q"): # quit if q
        # print state
        print(f"JOUEUR {current_player}")
        print(playerStr(players[current_player]))
        # end print state

        # q to quit
        while(c != "q"):
            try:
                c=input("Où voulez-vous tirer (ex A0, q pour quitter)?")
                (i,j) = parseCoord(c) # parsing coordinates into usable indices
                break
            except:
                print("Coordonnées non valides.") 
                continue # ask until something valid is given
        
        if c != "q": # the game continues
            # current player shoots the other player at position (i,j)
            r = shootAt(players[current_player], players[1-current_player], (i,j))
            # print the result in a human readable way
            if r == 0:
                print("Raté !")
            elif r == 1:
                print("Touché !")
            elif r==2:
                print("Coulé !")

            # if the other player has no boat anymore, ends the game
            if players[1-current_player]["nboat"] == 0:
                print(f"Joueur {current_player} gagne !")
                break
            else:
                # Otherwise, continue
                input("ENTER TO CONTINUE")
                print("\n\n")
                # change player
                current_player = 1-current_player

if __name__ == '__main__':
    main()
