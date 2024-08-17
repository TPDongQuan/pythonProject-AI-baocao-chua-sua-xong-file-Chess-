import random

'''
Greedy Algorithm with MinMax
'''
pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
# Locate where the knight is and see if its in better position (for AI).
# Tao những nước đi logic cho từng quân cờ ở 2 bên b w
# ưu tiên tính theo điểm để A.I ưu tiên sử dụng trên bàn cờ (
# cao nhất hiện tại là 4(có thể cụ thể nữa tùy theo sự tính toán của mình trong từng ô và theo từng con cờ) - ưu tiên đi đến nhất
# Để thực hiện di chuyển thông minh hơn, tấn công và phòng thủ vào những vị trí có điểm thấp hơn.

knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queenScores =  [[1, 1, 1, 3, 1, 1, 1, 1],
                [1, 2, 3, 3, 3, 1, 1, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 1, 2, 3, 3, 1, 1, 1],
                [1, 1, 1, 3, 1, 1, 1, 1]]

rookScores =   [[4, 3, 4, 4, 4, 4, 3, 4],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [1, 1, 2, 3, 3, 2, 1, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 1, 2, 2, 2, 2, 1, 1],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [4, 3, 4, 4, 4, 4, 3, 4]]

whitePawnScores =  [[8, 8, 8, 8, 8, 8, 8, 8], # we want it to try make to the end of board
                    [8, 8, 8, 8, 8, 8, 8, 8],
                    [5, 6, 6, 7, 7, 6, 6, 5],
                    [2, 3, 3, 5, 5, 3, 3, 2],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 1, 2, 3, 3, 2, 1, 1],
                    [1, 1, 1, 0, 0, 1, 1, 1],
                    [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScores =  [[0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 1, 1, 0, 0, 1, 1, 1],
                    [1, 1, 2, 3, 3, 2, 1, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [2, 3, 3, 5, 5, 3, 3, 2],
                    [5, 6, 6, 7, 7, 6, 6, 5],
                    [8, 8, 8, 8, 8, 8, 8, 8],
                    [8, 8, 8, 8, 8, 8, 8, 8]]

piecePositionScores = {"N": knightScores, "Q": queenScores, "B": bishopScores, "R": rookScores, "bp": blackPawnScores,
                       "wp": whitePawnScores} # make A.I cosider and choose in all of these scores
CHECKMATE = 1000 # winning score. -Check mate = -1000
STALEMATE = 0
DEPTH = 3 # có thể test A.I DEPTH = 4 và 5 để thấy sự khác biệt trong cùng 1 tình huống.
          # This is root depth = 4, A.I can reach.
          # Lowest depth = 0.

'''
Picks and return a random move.
'''

def findRandomMove(validMoves): #sua 1
    return validMoves[random.randint(0, len(validMoves)-1)]


'''
Find best move, min max without recursion: 
'''

def findBestMoveMinMaxNoRecursion(gs, validMoves): # sua 1. MinMax algorithm with no recursion (Greedy algorithm). max depth = 2.

    # Bad: can only 2 for loop, very nasty, do the same things

    turnMultiplier = 1 if gs.whiteToMove else -1 # Decide which turns it is.
    opponentMinMaxScore = CHECKMATE # A.I checkmate, the largest score for A.I (A.I wins).
    bestPlayerMove = None # best Move of player
    random.shuffle(validMoves) # random shuffle player move

    for playerMove in validMoves: # in player move. Aim = minimize A.I move and make best move
        gs.makeMove(playerMove) # we make move
        opponentsMoves = gs.getValidMoves() #A.I make move.
        #Find opp maxscore after we make move
        if gs.stalemate: # stalemate
            opponentMaxScore = STALEMATE # stalemate
        elif gs.checkmate: # or checkmate
            opponentMaxScore = -CHECKMATE # set A.I checkmate to lowest value. A.I losing
        else: # so no opponent moves
            opponentMaxScore = -CHECKMATE
            for opponentsMove in opponentsMoves: # in A.I moves. Aim: minimize player move and make best move
                gs. makeMove(opponentsMove) # make move
                gs.getValidMoves()
                if gs.checkmate: # if checkmate
                    score = CHECKMATE # make A.I move to checkmate us. A.I winning
                elif gs.stalemate: # stalemate
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board) # if not above. make A.I best movement
                if score > opponentMaxScore: # if A.I move > A.I max score
                    opponentMaxScore = score # take it is new A.I max score move ( is the A.I best movement)
                gs.undoMove()
        if opponentMaxScore < opponentMinMaxScore: # if A.I new max score < A.I checkmate. This compare comtinue until A.I max score = A.I checkmate (A.I wins)
            opponentMinMaxScore = opponentMaxScore # minimize A.I checkmate and choose it the best move for A.I.
            bestPlayerMove = playerMove # best move for player
        gs.undoMove()
    return bestPlayerMove

'''
Helper method to make first recursive call
'''
def findBestMove(gs, validMoves, returnQueue): # sua 1. Calling out the method we use
    '''
    Check which method is faster: using counter
    Counter: counting how many times each method (recursion) called.
        if counter high => generate so many moves. if counter low => generate less moves
    => To see how many alpha-beta cutting off
    '''
    global nextMove, counter
    nextMove = None # set None when cannot find the method will use random moves.
    random.shuffle(validMoves)
    counter = 0
    #findMoveMinMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    #findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1) # alpha is -CHECKMATE and beta is CHECKMATE
    print(counter)
    returnQueue.put(nextMove)

'''
MinMax algorithm đệ quy (Recursively): MinMax algorithm. similar above, but can do in higher depths
'''

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove, counter # global -> local can change
    counter += 1
    if depth == 0: # recursion check if depth = 0.
        return scoreMaterial(gs.board) # make the score for next move

    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False) #
            if score > maxScore: #
                maxScore = score #
                if depth == DEPTH: #
                    nextMove = move #
            gs.undoMove()
        return maxScore

    else: # black turn or recursion false
        minScore = CHECKMATE # worst for black, need decrease
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score #-> (temporary score).
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore

'''
findMoveNegaMax : combine minMax functions. Always look for maximum and multiply it (= -1) on black turns
'''
def findMoveNegaMax(gs, validMoves, depth, turnMultiplier): #sua 1. Simplify of MinMax algorithm (but have negative sign)

    '''
    turnMultiplier = +1 or -1 so -turnMultiplier = -(+1) or -(-1)
    maxScore = -Checkmate worst for white
    Finding the highest score(white), when depth == 0:
            score(white) = -(-maxScore(black)) = +score(white)
                score > maxScore (-1000)
                new maxScore = score
                Turn back to depth == 4
                A.I make that score the next move
                This Recursion keep happening each turn in the same side, until:
                score(1000) > new maxScore(...)
                new maxScore = score = 1000
                => white win
        if A.I black :
            maxScore = -Checkmate good for black
            Finding the highest score(black), when depth == 0:
                score(black) = -(+maxScore(white)) = -score(black)
                new maxScore = score
                Turn back to depth == 4
                A.I make that score the next move
                This Recursion keep happening each turn in the same side, until:
                score(-1000) < new maxScore(-...)
                new maxScore = score = -1000
                => black win
    '''
    global nextMove, counter
    counter += 1
    if depth == 0: #only run in recursion to depth == 0:
        # When recursion: turnMultiplier -> -turnMultiplier
        return turnMultiplier * scoreBoard(gs) # make the highest score for each side.
    maxScore = -CHECKMATE # worst temporary score. Use to compare

    for move in validMoves:
        gs.makeMove(move) # A.I make move
        nextMoves = gs.getValidMoves() # prepare A.I next move
        score = -findMoveNegaMax(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier): #sua 1. simplify of MinMax Alpha - Beta. Negative max -max

    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs) # 1 or -1 depends b or w.

    maxScore = -CHECKMATE # max score for both sides
    for move in validMoves:
        gs.makeMove(move) # make move
        nextMoves = gs.getValidMoves() # var for next move
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier) # alpha = -beta and beta = -alpha
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move 
                print(move, score)
        gs.undoMove()
        if maxScore > alpha: # pruning happens. Check if our new maxscore > aplha.
            alpha = maxScore # alpha is new maxscore
        if alpha >= beta: # break out of for function, stop looking => return -CheckMate
            break
    return maxScore

'''
A positive score is good for white, a negative score is good for black
'''
def scoreBoard(gs): #sua 1. Prioritized scores for each role
    #if game end so no need scoreBoard
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE # black wins.
        else:
            return CHECKMATE # white wins.
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--": # make sure not a blank
                #now score it positionally based on type of piece
                piecePositionScore = 0
                if square[1] != "K": # K no table
                    if square[1] == "p": # because 2 types of "p" ( b and w)
                        piecePositionScore = piecePositionScores[square][row][col]
                    else:
                        piecePositionScore = piecePositionScores[square[1]][row][col]

                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePositionScore * .1 # play more material than position
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePositionScore * .1
    return score

'''
Score the board based on material.
'''
def scoreMaterial(board): # selection pieces depend on scores from pieceScore
    score = 0 # even equal movement
    for row in board:
        for square in row:
            if square[0] == 'w': # square[0] first letter is color.
                score += pieceScore[square[1]] # add score for white. based on letter 2 each type of piece
            elif square[0] == 'b': # the same
                score -= pieceScore[square[1]] # always substact score for black

    return score