from math import *
import random
from copy import deepcopy

#color values for 2 players
COLORS = ((1,2),(3,4))
COLORS_REV = (0,2,1,4,3)
SIZE= 16

def normalize(tokens):
    for i in range(len(tokens)):
        tokens[i].sort()

    if len(tokens[1]) and ( not len(tokens[0]) or tokens[0][0] > tokens[1][0]):
        tokens[0], tokens[1] = tokens[1], tokens[0]
    if len(tokens[3]) and ( not len(tokens[2]) or tokens[2][0] > tokens[3][0]):
        tokens[2], tokens[3] = tokens[3], tokens[2]

    return tokens
      
def applyFct(tokens,f):
    return normalize([[f(tokens[i][j]) for j in range(len(tokens[i]))] for i in range(len(tokens))])

def rotateIndex(index):
    fct = (12,8,4,0,13,9,5,1,14,10,6,2,15,11,7,3)
    return fct[index]

def mirrorXIndex(index):
    fct = (12,13,14,15,8,9,10,11,4,5,6,7,0,1,2,3)
    return fct[index]

def mirrorYIndex(index):
    fct = (3,2,1,0,7,6,5,4,11,10,9,8,15,14,13,12)
    return fct[index]

def checkConsistency(tokens, pos):
    for i in range(len(tokens)):
        for j in range(len(tokens[i])):
            if tokens[i][j] == pos:
                return False
        
    return True

def threePcsInARow(tokensSameColor):
    trueCombinations = {(0, 1, 2), (1, 2, 3), (4, 5, 6), (5, 6, 7), (8, 9, 10), (9, 10, 11), (12, 13, 14), (13, 14, 15),(3, 7, 11), (7, 11, 15), (2, 6, 10), (6, 10, 14), (1, 5, 9), (5, 9, 13), (0, 4, 8), (4, 8, 12),(0, 5, 10), (1, 6, 11),(4, 9, 14),(5,10,15),(2,5,8),(7,10,13),(3,6,9),(6,9,12)}
    
    combinations = [(tokensSameColor[i],tokensSameColor[j],tokensSameColor[k]) for i in range(len(tokensSameColor)) for j in range(i+1,len(tokensSameColor)) for k in range(j+1,len(tokensSameColor)) if (tokensSameColor[j]==tokensSameColor[i]+1 and tokensSameColor[k]==tokensSameColor[j]+1) or (tokensSameColor[j]==tokensSameColor[i]+4 and tokensSameColor[k]==tokensSameColor[j]+4) or (tokensSameColor[j]==tokensSameColor[i]+3 and tokensSameColor[k]==tokensSameColor[j]+3) or (tokensSameColor[j]==tokensSameColor[i]+5 and tokensSameColor[k]==tokensSameColor[j]+5)]

    setCombinations = set(combinations)

    return len(setCombinations.intersection(trueCombinations))

def getValidNeighbours(index):
    fct = ((1,4),(0,2,5),(1,3,6),(2,7),(0,5,8),(1,4,6,9),(2,5,7,10),(3,6,11),(4,9,12),(5,8,10,13),(6,9,11,14),(7,10,15),(8,13),(9,12,14),(10,13,15),(11,14))
    return fct[index]

def winHeuristic(tokens, player):
    value=0
    opponent=1-player
    for color in (2*player,2*player+1):
        otherColor = 1-color + 4*player
        cumulation = set(tokens[color])
        for i in tokens[otherColor]:
            cumulation = cumulation.union(set(getValidNeighbours(i)))
        for opColor in (2*opponent,2*opponent+1): 
            cumulation = cumulation - set(tokens[opColor])

        value += threePcsInARow(sorted(list(cumulation)))

    return value

def winHeuristic2(tokens, player):
    fct = (0,1,1,0,1,4,4,1,1,4,4,1,0,1,1,0)
    value=0
    for color in (2*player,2*player+1):
        for i in tokens[color]:
            value += fct[i]

    return value

def winHeuristic3(tokens, player):
    value=0
    for color in (2*player,2*player+1):
        value += threePcsInARow(tokens[color])

    return value

def winHeuristic4(tokens,player):
    opponent=1-player
    opponentNeighbours = {n for i in tokens[2*opponent]+tokens[2*opponent+1] for n in getValidNeighbours(i)}
    opponentNeighbours -= set([i for color in tokens for i in color])
    return len(opponentNeighbours)    

def winHeuristicPlayer0(tokens):
    size = len([i for color in tokens for i in color])
    if size > 10:
        return -2*winHeuristic4(tokens,0)+2*winHeuristic4(tokens,1)-4*winHeuristic3(tokens,0)+0.5*winHeuristic2(tokens,1)
    else:
        return winHeuristic2(tokens,1)

def winHeuristicPlayer1(tokens):
    size = len([i for color in tokens for i in color])
    if size > 10:
        return -2*winHeuristic4(tokens,1)+2*winHeuristic4(tokens,0)-4*winHeuristic3(tokens,1)+0.5*winHeuristic2(tokens,0)
    else:
        return winHeuristic2(tokens,0)


def winHeuristicMC(tokens, player):
    MCiter = (16-len([i for color in tokens for i in color]))*2

    wins = [0,0]
    state = GameState(deepcopy(tokens))
    for iter in range(MCiter):
        while True:
            moves = state.GetMoves(player)
            if state.GetWinRequirement(player):
                wins[player] += 1
                break
            if moves == []:
                break
            state = GameState(random.choice(moves))
            player=1-player

    return wins[player]

class GameState:
    """ A state of the game, i.e. the game board. These are the only functions which are
        absolutely necessary to implement UCT in any 2-player complete information deterministic 
        zero-sum game, although they can be enhanced and made quicker, for example by using a 
        GetRandomMove() function to generate a random move during rollout.
        By convention the players are numbered 1 and 2.
    """
    def __init__(self, tokens=array.array('b',  [0 for i in range(16) ])):
            self.tokens = tokens
        
    def GetMoves(self, player):
        """ Get all possible moves from this state.
        """
        opponent = 1-player

        turnMoves=[]

        if self.tokens.count(0)==16:
            moves=[[0,0]]   #first move only
        else:
            #First turn a token from opponent
            for color in COLORS[opponent]:
                positions = [i for i in range(16) if b[i]==color]
                for currentPos in positions:
                    
                    for neighbour in getValidNeighbours(currentPos):
                        if not self.tokens[neighbour]:
                            moves.append([currentPos, neighbour])

        #Now insert new token of own color
        for move in moves:
            for color in COLORS[player]:
                for newPos in range(16):
                    if not self.tokens[newPos]:
                        move.append([newPos, color])

        return moves
                
    
    def GetWinRequirement(self, player):
        """ Get the game result from the viewpoint of player. 
        """
        ret = False
        for color in (2*player,2*player+1):
            if threePcsInARow(self.tokens[color]):
                return True

        return False
     

    def rotate(self):
        return applyFct(self.tokens,rotateIndex)

    def mirrorX(self):
        return applyFct(self.tokens,mirrorXIndex)

    def mirrorY(self):
        return applyFct(self.tokens,mirrorYIndex)

    def numTokens(self):
        return len([i for color in self.tokens for i in color])

    def __str__(self):
        field = [" " for i in range(16)]
        for i in self.tokens[0]:
            field[i]="a"
        for i in self.tokens[1]:
            field[i]="e" 
        for i in self.tokens[2]:
            field[i]="x"
        for i in self.tokens[3]:
            field[i]="+"

        s=""

        for i in range(len(field)):
            if i != 0 and i % 4  == 0:
                s += "|\n"

            s += "|" + field[i]

        s += "|"

        return s

    def __repr__(self):
            return str(self.tokens)

    def __hash__(self):
            return hash(str(self.tokens))

    def __eq__(self, other):
        return self.tokens == other.tokens
            
class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """
    def __init__(self, player, state,  parent = None):
        self.state = state
        self.parentNode = parent # "None" for the root node
        self.childNodes = []
        self.childTransforms = []
        self.player = player
            
    def AddChild(self, node, transform):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        self.childNodes.append(node)
        self.childTransforms.append(transform)

    def deleteChildrenUpExceptWinner(self, winner):
        index = None
        for i in range(len(self.childNodes)):
            if self.childNodes[i].winner == winner:
                index = i
                break

        if not index == None:
            del self.childNodes[:index]
            del self.childTransforms[:index]
            del self.childNodes[index+1:]
            del self.childTransforms[index+1:] 
    
    def __repr__(self):
        return "[Player: " + str(self.player) + str(self.state)+"]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
             s += c.TreeToString(indent+1)
        return s

    def IndentString(self,indent):
        s = "\n"
        for i in range (1,indent+1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
             s += str(c) + "\n"
        return s


stateToNode = {}


def getNodeFromDict(state):
    global stateToNode

    if state in stateToNode:
        return stateToNode[state], None

    rotatedState = deepcopy(state)

    #print(str(rotatedState))
    #print("-------------------")

    for i in range(3):
        rotatedState = GameState(rotatedState.rotate())
        #print(str(rotatedState), "\n")
        if rotatedState in stateToNode:
            return stateToNode[rotatedState], "rot"+str(i+1)

    rotatedState = GameState(state.mirrorX())
    #print(str(rotatedState), "\n")
    if rotatedState in stateToNode:
        return stateToNode[rotatedState], "mirror"

    for i in range(3):
        rotatedState = GameState(rotatedState.rotate())
       # print(str(rotatedState), "\n")
        if rotatedState in stateToNode:
            return stateToNode[rotatedState], "mirror+rot"+str(i+1)

    #print("-------------------")
    #print("-------------------")

    return None, None



generated = 0
pruned = 0
duplicate = 0
depth = 16

def searchBloxxRec(node):
    global stateToNode
    global generated
    global pruned, duplicate
    global depth

    generated+=1
    
    if generated % 10000 == 0:
        print("Ratio:",pruned*1.0/generated*1.0, "Depth:",depth)

    if node.state.GetWinRequirement(node.player):
        node.winner = node.player
        return node.winner

    moves = node.state.GetMoves(node.player)

    if moves == []:
        if node.state.GetWinRequirement(0):
            node.winner = 0
        elif node.state.GetWinRequirement(1):   
            node.winner = 1
        else:     
            node.winner = 2 #draw   
        return node.winner 

    if node.player==0:
        moves.sort(key=winHeuristicPlayer0)
    if node.player==1:
        moves.sort(key=winHeuristicPlayer1)


    generated +=len(moves)

    """
    if len(moves) > 10:
        print("Player:", node.player)
        print(str(node.state))
        print("------------------------")
        print("------------------------")               
        for move in moves:
            print(str(GameState(move)))
            print("Value:",winHeuristicPlayer0(move))
            print("------------------")
        print("\n\n")
    """

    childWinners = set()

    cnt = 0
    for move in moves:
        newState = GameState(move)
        child, transform = getNodeFromDict(newState)
        if child == None:
            child = Node(1-node.player, newState, node)
#            if newState.numTokens() < 14:
            stateToNode[newState] = child
            node.AddChild(child, None)
            childWinners.add(searchBloxxRec(child))
            depth = min(depth, newState.numTokens())
        elif not child.parentNode == node:
            node.AddChild(child, transform)
            childWinners.add(child.winner)
        if node.player in childWinners:
            node.winner = node.player
            pruned += len(moves)-cnt
            node.deleteChildrenUpExceptWinner(node.winner)
            return node.winner
        cnt+=1

    if 2 in childWinners:
        node.winner = 2
        node.deleteChildrenUpExceptWinner(node.winner)
    else:
        node.winner = 1-node.player

    return node.winner


def searchBloxx():
    global stateToNode

    counter = 0
    rootState = GameState()
    root = Node(0, rootState)
    stateToNode[rootState] = root
    winner = searchBloxxRec(root)
    print(winner)

