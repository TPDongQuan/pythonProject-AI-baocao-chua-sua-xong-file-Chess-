"""
This is storing info about current state of chess game. Determining valid moves and keep a move log
"""
'''
Notice: if you have a move, try to find the area(or the function) and use print("...") to check each steps
'''


class GameState():
    def __init__(self):
        """
        This board:
        - 8x8 2nd list, each elements of the list
        - is a 2 character string: 1st charac is for b or w. 2nd is for role and '--' is empty

        Build rows in chess:
            Broad is 8x8 2nd list.
            b or w represents the color of each sites.
            others represents the name of each roles.
            -- : represents the empty space

        """
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)  # locate the white and black king as num on board
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        #self.Defeat = False
        self.enPassantPossible = ()  # coordinates for the square where en passant cap is possible
        self.enPassantPossibleLog = [self.enPassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    '''
    takes a moves a paramenter and executes it (will not work for castling, pawn promottion)
    '''

    def makeMove(self, move): # sửa 1
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.board[move.startRow][move.startCol] = "--"  # đi vào ô trống
        self.moveLog.append(move) # log move
        self.whiteToMove = not self.whiteToMove  # swap player. đồi người chơi
        # update the king's new location if moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        #if move.pieceCaptured == 'wK' or move.pieceCaptured == 'bK':
            #self.Defeat = True
        # IF pawn moves twice, next move can capture enpassant
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.endRow + move.startRow)//2, move.endCol)
        else:
            self.enPassantPossible = ()

        #if en passant move, must update the board to capture the pawn
        if move.enPassant:
            self.board[move.startRow][move.endCol] = '--'

        # if pawn promo change piece:
        if move.pawnPromotion:
            promotedPiece = 'Q'
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece
        '''
        # enpassant move:
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"  # cap the pawn

        # update enpassantPossible var
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:  # only 2 squares ad
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpPassantPossible = ()
        '''

        # castle moves:
        if move.castle:
            if move.endCol - move.startCol == 2:  # kingside castle move
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # move rook
                self.board[move.endRow][move.endCol + 1] = '--'  # empty old square of rook
            else:  # queen side castle move
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # move rook
                self.board[move.endRow][move.endCol - 2] = '--'

        self.enPassantPossibleLog.append(self.enPassantPossible)

        # update castling rights - whenever it is a rock or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    '''
    Undo the last move made
    '''

    def undoMove(self): # sửa 1
        if len(self.moveLog) != 0:  # make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved # put piece on starting square
            self.board[move.endRow][move.endCol] = move.pieceCaptured # put back capture piece
            self.whiteToMove = not self.whiteToMove  # switch turns back

            # update the king's position if needed
            if move.pieceMoved == "wk":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bk":
                self.blackKingLocation = (move.startRow, move.startCol)

            # undo en passant
            if move.enPassant:
                self.board[move.endRow][move.endCol] = '--'  # remove the pawn that added in the wrong square
                self.board[move.startRow][move.endCol] = move.pieceCaptured # put the pawn back on the correct square was captured from

            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]

            #give back castle rights if move took them away
            self.castleRightsLog.pop() # get rid of the new castle rights from the move we are undoing
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

            '''# undo castling rights
            self.castleRightsLog.pop()  # get rid of new castle rights from the move
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            '''

            # undo castle move:
            if move.castle:
                if move.endCol - move.startCol == 2:  # kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # queenside
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'
            self.checkmate = False;
            self.stalemate = False;

        '''
        Update the castle rights given the move
        '''

    def updateCastleRights(self, move): #sua1
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.bks = False

        # if a rook is captured: ...
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False



    '''
    All moves considering checks
    '''

    def getValidMoves(self): # sua 2
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove: # white King in check
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else: # or black king in check
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck: # ktra vị trí check
            if len(self.checks) == 1: # only 1 check, block or move King
                moves = self.getAllPossibleMoves() # only move the piece can block enemy
                check = self.checks[0] # find info
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] # enemy piece causing check
                validSquares = [] # squares that pieces can move to
                # cap enemy, move king, or block
                if pieceChecking[1] == 'N': # if a N check king
                    validSquares = [(checkRow, checkCol)] # attack the N
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) # check[...] directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: #once you get to piece and checks
                            break
                #get rid of any moves that dont block check or move king
                for i in range(len(moves) - 1, -1, -1): #go through backwards when you are removing from a list as iterating
                    if moves[i].pieceMoved[1] != 'K': # move not king, so block or cap
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: # move not block check or cap
                            moves.remove(moves[i])
            else: # double checks (2 attacks), king has to move,
                self.getKingMoves(kingRow, kingCol, moves)

        else: # kING not in check so all moves all fine
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        return moves


        '''
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs,
                                        self.currentCastlingRight.bqs)  # copy current castling rights
        # 1. generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves, allyColor = )
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        # 2. each move, make move
        for i in range(len(moves) - 1, -1, -1):  # when removing from a list go backwards
            self.makeMove(moves[i])
            # 3. generate all opp's moves
            # 4. for each of your opp's moves, see if attack ur king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])  # 5. if they do attack king, not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:  # either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves
        '''

    '''
    Determine if the enemy considering checks
    '''

    def inCheck(self): # sua 1
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])



        '''self.whiteToMove = not self.whiteToMove  # switch to opp turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # square under attack
                return True
        return False
        '''

    '''
    All moves without considering checks
    '''

    def getAllPossibleMoves(self): # sua 1
        moves = []
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of cols in given rows
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (
                        turn == 'b' and not self.whiteToMove):  # separate black turns or white turns
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    '''
    
    Get all the pawn moves for pawn located at row, col and add these moves to list
    '''

    def getPawnMoves(self, r, c, moves):  # make moves for pawns. sua 2:
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            enemyColor = 'b'
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = 'w'
            kingRow, kingCol = self.blackKingLocation

        if self.board[r+moveAmount][c] == "--": # 1 move up
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((r, c), (r + moveAmount, c), self.board))  # lên 1 hàng. (vị trí hiện tại, vị trí sau đó, trên bảng)
                if r == startRow and self.board[r+2*moveAmount][c] == "--":  # Di chuyển 2 bước
                    moves.append(Move((r, c), (r+2*moveAmount, c), self.board))  # lên 2 hàng
        if c - 1 >= 0:  # Tấn công bên trái
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r + moveAmount][c - 1][0] == enemyColor:  # Nếu bên trái có 'b'
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board))
                if (r + moveAmount, c - 1) == self.enPassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c: #king is left of the pawn
                            # inside between king and pawn; outside range between pawn border
                            insideRange = range(kingCol + 1, c-1)
                            outsideRange = range(c+1, 8)
                        else: #king right of the pawn
                            insideRange = range(kingCol - 1, c, -1)
                            outsideRange = range(c-2, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != "--": #some piece beside enpassant pawn blocks
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"): #attacking piece
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, enPassant=True))
        if c + 1 <= 7:  # Tấn công bên phải
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r + moveAmount][c + 1][0] == enemyColor:  # Nếu bên phải có 'b
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board))  # dịch bên phải trên
                if (r + moveAmount, c + 1) == self.enPassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c:  # king is left of the pawn
                            # inside between king and pawn; outside range between pawn border
                            insideRange = range(kingCol + 1, c)
                            outsideRange = range(c + 2, 8)
                        else:  # king right of the pawn
                            insideRange = range(kingCol - 1, c + 1, -1)
                            outsideRange = range(c - 1, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != "--":  # some piece beside enpassant pawn blocks
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):  # attacking piece
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, enPassant=True))
        '''
        if self.whiteToMove:  # White player
            if self.board[r - 1][c] == "--":  # Di chuyển 1 bước
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(
                        Move((r, c), (r - 1, c), self.board))  # lên 1 hàng. (vị trí hiện tại, vị trí sau đó, trên bảng)
                    if r == 6 and self.board[r - 2][c] == "--":  # Di chuyển 2 bước
                        moves.append(Move((r, c), (r - 2, c), self.board))  # lên 2 hàng
            if c - 1 >= 0:  # Tấn công bên trái
                if self.board[r - 1][c - 1][0] == 'b':  # Nếu bên trái có 'b'
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                    elif (r - 1, c - 1) == self.enPassantPossible:
                        moves.append(Move((r, c), (r - 1, c - 1), self.board, enPassant=True))
            if c + 1 <= 7:  # Tấn công bên phải
                if self.board[r - 1][c + 1][0] == 'b':  # Nếu bên phải có 'b
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))  # dịch bên phải trên
                elif (r - 1, c + 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, enPassant=True))

        else:  # black pawn moves
            if self.board[r + 1][c] == "--":  # 1 square move
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":  # 2 square moves
                        moves.append(Move((r, c), (r + 2, c), self.board))
            # captures:
            if c - 1 >= 0:  # capture to left
                if self.board[r + 1][c - 1][0] == 'w':
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, enPassant=True))
            if c + 1 <= 7:  # capture to right
                if self.board[r + 1][c + 1][0] == 'w':
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, enPassant=True))
    '''
    '''
    rook moves function like pawn moves
    '''

    def getKnightMoves(self, r, c, moves): #sua 1
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:  # not an ally piece (empty or enemy piece)
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):  # con Tượng. sua 1
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # 4 diaganols
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece invalid
                            break
                else:  # out of board
                    break

    def getQueenMoves(self, r, c, moves):# sua 1
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getRookMoves(self, r, c, moves): #sua 1
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':  # cant remove queen from pin on rook moves, only on bishop
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # go up, down, left, right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # enemy piece valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # enemy piece valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece invalid (teammates).
                            break
                else:  # off board, no square
                    break

    def getCastleMoves(self, r, c, moves, allyColor): # sửa 1
        inCheck = self.squareUnderAttack(r, c, allyColor)
        if inCheck:
            return # cant castle incheck
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves, allyColor)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves, allyColor)

    def getKingsideCastleMoves(self, r, c, moves, allyColor):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--' and \
                not self.squareUnderAttack(r, c + 1, allyColor) and not self.squareUnderAttack(r, c + 2, allyColor):
            moves.append(Move((r, c), (r, c + 2), self.board, castle=True))

    def getQueensideCastleMoves(self, r, c, moves, allyColor):
        #check if three square between k and r are clear and are not under attacked
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--' and \
                not self.squareUnderAttack(r, c - 1, allyColor) and not self.squareUnderAttack(r, c - 2, allyColor):
            moves.append(Move((r, c), (r, c - 2), self.board, castle=True))

    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: #not an ally piece ( empty or enemy)
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # place king back on ori location
                    if allyColor == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
        self.getCastleMoves(r, c, moves, allyColor)
    '''
    Generate all valid castle moves for the king at r, c and add them to the list of moves
    '''

    def squareUnderAttack(self, r, c, allyColor): #sua 2
        # check outward from square
        enemyColor = 'w' if allyColor == 'b' else 'b'
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor: # no attack
                        break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        #5 possible here in this complex conditional:
                        # 1. orthogonally away from square and piece is a rook
                        # 2. diagonally  ... a bishop
                        # 3. 1 square a away diagonally ... a pawn
                        # 4. any directions and piece is a queen
                        # 5. any directions and 1 square away and piece is a king
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and (
                                        (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            return True
                        else: # enemy piece not applying check:
                            break
                else: # off board
                    break

        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N': #enemy knight attacking king
                    return True

        return False

    def checkForPinsAndChecks(self): # sua 1
        pins = []  # squares where the allied pinned piece is and direction pinned from
        checks = []  # squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # 2nd allied piece, so no pin or check direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 possibilities here in this complex conditional
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():  # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece not applying check
                            break
                else:  # off board
                    break

        # check for knight checks:
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':  # enenmy knight attack king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move(): # sua 1
    # maps keys to values
    # key: value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enPassant=False, castle=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.pawnPromotion = self.pieceMoved[1] == 'p' and (self.endRow == 0 or self.endRow == 7)
        # en passant
        self.enPassant = enPassant
        if self.enPassant:
            self.pieceCaptured = 'bp' if self.pieceMoved == 'wp' else 'wp' # enpassant capture opposite colored pawn
        # Castle move:
        self.castle = castle
        self.isCapture = self.pieceCaptured != '--'
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol  # move ID

    '''
    Overriding the equals method
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        # make like real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    #overriding the str() function
    def __str__(self):
        # castle move
        if self.castle: # "o-o" : kingside castle. "o-o-o": queen side castle
            return "O-O" if self.endCol == 6 else "O-O-O"
        endSquare = self.getRankFile(self.endRow, self.endCol)

        # pawn moves
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare

            #pawn promo

            # piece moves:
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare