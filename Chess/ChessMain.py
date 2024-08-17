"""
This is main driver file. For handling user input and displaying current GameState. Tạo giao diện
"""
import pygame as p
from Chess import ChessEngine, SmartMoveFinder # gọi code từ file khác lên sử dụng
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512 # 400 is another version. kẻ ô
MOVE_LOG_PANEL_WIDTH = 250
MOVE_lOG_PANEL_HEIGHT = BOARD_HEIGHT
dimension = 8
SQ_SIZE = BOARD_HEIGHT // dimension # size ô vuông
max_FPS = 15 # animation game
Images = {}
'''
Initialize a global dic of images. This will be called from main
'''
def loadImages(): # Load pieces img up
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ'] # List of all roles.
    for piece in pieces: # vòng lặp for gán pieces vào:
        Images[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE)) # gán file ảnh vào từng piece
    #Note: we can access an image by saving 'Imanges['wp']'
'''
The main driver for our code. Handle input and updating graphics.
'''
def main():
    p. init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 14, False, False)
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a move is made
    animate = False #flag var for when we should animate a move
    loadImages() #only do this once, before the while loop
    running = True
    sqSelected = () # no sqaure is selected, keep track of the last click of the user
    playerClicks = [] # keep track of player clicks
    gameOver = False
    playerOne = True # True is player. False is Ai (for white)
    playerTwo = False #Like above (for black)
    AIThinking = False # the time of A.I thinking
    moveFinderProcess = None
    moveUndone = False
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() # (x,y) location of the mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    #print(row)
                    #print(col)
                    if sqSelected == (row, col) or col >= 8: # user clicked the same square twice or clicked the mouse log => deselect user clicked
                        sqSelected = () #deselect
                        playerClicks = [] # clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) #append both 1st and 2nd clicks
                    if len(playerClicks) == 2 and humanTurn: # after 2nd clicks
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = () #reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # to undo press 'z'
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r: # press 'r' to reset
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    moveUndone = True

        #AI move finder:
        if not gameOver and not humanTurn and not moveUndone: # ko phai GameOver hay nguoi choi
            if not AIThinking: # while A.I thinking
                AIThinking = True
                print("A.I thinking ...") # print out
                returnQueue = Queue() # pass data between threads
                moveFinderProcess = Process(target=SmartMoveFinder.findBestMove, args=(gs, validMoves, returnQueue)) # A.I making moves
                moveFinderProcess.start() # call out FBS(...) and start it
                #AIMove = SmartMoveFinder.findBestMove(gs, validMoves) # thực hiện Best Moves: lượt đi tốt nhất

            if not moveFinderProcess.is_alive(): # if A.I done thinking
                print("Done!") # alert
                AIMove = returnQueue.get() # return results
                if AIMove is None: # if no move from A.I
                    AIMove = SmartMoveFinder.findRandomMove(validMoves) # make random moves
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        if gs.checkmate or gs.stalemate:
            gameOver = True
            text = 'Stalemate' if gs.stalemate else 'Black Wins' if gs.whiteToMove else 'White Wins'
            drawEndGameText(screen, text)

        clock.tick(max_FPS)
        p.display.flip()

'''
Responsible for all the graphics within a current game state
'''
def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen) # draw squares on the board
    # add in piece highlighting or move suggestions (later)
    drawPieces(screen, gs.board)
    highlightSquare(screen, gs, validMoves, sqSelected)
    drawMoveLog(screen, gs, moveLogFont)

'''
Draw the squares on the board. top left always white(light).
'''
def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Highlight square selected and moves for piece selected
'''
def highlightSquare(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): # square selected is a piece that can be moved
            #highlight selected square:
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # transparency value
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))





'''
Draw pieces on the board using the current GameState.board
'''
def drawPieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != "--":  # not empty spare
                screen.blit(Images[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
'''
Draw move log
'''
def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_lOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = [] # need modify
    for i in range(0, len(moveLog), 2): # go thru the moveLop twice, and take its number
        moveString = str(i//2 + 1) + ") " + str(moveLog[i]) + " " # start at 1 and += up. EX: 1.F2F5 F5F2 2. F3F4 F4F3 ...
        if i + 1 < len(moveLog): # make sure both b w made a move
            moveString += str(moveLog[i+1]) + "   "
        moveTexts.append(moveString)

    movesPerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, True, p.Color('White'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing
'''
Animating a move
'''
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 # frames to move one square
    framesCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(framesCount + 1):
        r, c =((move.startRow + dR*frame/framesCount, move.startCol + dC*frame/framesCount))
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.enPassant:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(Images[move.pieceCaptured], endSquare)
        #draw moving piece
        if move.pieceMoved != '--':
            screen.blit(Images[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2, BOARD_HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Red"))
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ =="__main__":
    main()