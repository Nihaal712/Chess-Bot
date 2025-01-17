"""
This class is responsible for storing all the information about  the current chess game.
It will also be responsible for determining valid moves at the current state.
It will also keep the move log.
"""
import numpy as np
from Chess import ChessMain

class GameState():
    def __init__(self):
        # Create the initial board setup using numpy array
        self.board = np.array([
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],  # Black major pieces
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],  # Black pawns
            ["--", "--", "--", "--", "--", "--", "--", "--"],   # Empty squares
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],  # White pawns
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]   # White major pieces
        ])
        self.MoveFunction={"p":self.GetPawnMoves, "R":self.GetRookMoves, "N":self.GetKnightMoves,
                           "B":self.GetBishopMoves,"Q":self.GetQueenMoves,"K":self.GetKingMoves}
        self.WhiteToMove=True
        self.MoveLog=[]
        self.WhiteKingLocation=(7,4)
        self.BlackKingLocation = (0, 4)
        self.CheckMate = False
        self.StaleMate = False
        self.EnpassantPossible = ()  # coordinates for the square where en passant capture is possible
        self.CurrentCastlingRight = CastleRights(True, True, True, True)
        self.CastleRightsLog = [CastleRights(self.CurrentCastlingRight.wks, self.CurrentCastlingRight.bks,
                                             self.CurrentCastlingRight.wqs, self.CurrentCastlingRight.bqs)]

    def MakeMove(self,move):
        self.board[move.StartRow,move.StartCol]= "--"
        self.board[move.EndRow,move.EndCol] = move.PieceMoved
        self.MoveLog.append(move)
        self.WhiteToMove= not self.WhiteToMove
        # Update kings position if moved
        if move.PieceMoved =='wK':
            self.WhiteKingLocation= (move.EndRow,move.EndCol)
        elif move.PieceMoved == "bK":
            self.BlackKingLocation = (move.EndRow, move.EndCol)
        #pawn promotion
        if move.IsPawnPromotion:
            self.board[move.EndRow,move.EndCol] = move.PieceMoved[0] + 'Q'
        # Check if the move is an en passant move
        if move.IsEnpassantMove:
            # Capture the pawn
            self.board[move.StartRow,move.EndCol] = '--'  # The captured pawn is removed
        # Update enpassantPossible if a pawn moves two squares forward
        if move.PieceMoved[1] == 'p' and abs(move.StartRow - move.EndRow) == 2:  # Only on 2-square pawn advances
            # Set en passant possibility at the intermediate square
            self.EnpassantPossible = ((move.StartRow + move.EndRow) // 2, move.StartCol)
        else:
            # Reset en passant possibility if no two-square pawn move occurred
            self.EnpassantPossible = ()

        # Handle castling moves
        if move.IsCastleMove:
            if move.EndCol - move.StartCol == 2:  # Kingside castle move
                # Move the rook involved in kingside castling
                self.board[move.EndRow,move.EndCol - 1] = self.board[move.EndRow,move.EndCol + 1]  # Move rook to the correct square
                self.board[move.EndRow,move.EndCol + 1] = '--'  # Erase old rook position
            else:  # Queenside castle move
                # Move the rook involved in queenside castling
                self.board[move.EndRow,move.EndCol + 1] = self.board[move.EndRow,move.EndCol - 2]  # Move rook to the correct square
                self.board[move.EndRow][move.EndCol - 2] = '--'  # Erase old rook position
        # update castling rights whenever it is a cook ama kine move
        self.UpdateCastleRights(move)
        self.CastleRightsLog.append(CastleRights(self.CurrentCastlingRight.wks, self.CurrentCastlingRight.bks,
                                                         self.CurrentCastlingRight.wqs, self.CurrentCastlingRight.bqs))

    def UndoMove(self):
        if self.MoveLog !=0 :
            move=self.MoveLog.pop()
            self.board[move.StartRow, move.StartCol] =move.PieceMoved
            self.board[move.EndRow, move.EndCol] =move.PieceCaptured
            self.WhiteToMove = not self.WhiteToMove
            # Update kings position if moved
            if move.PieceMoved == 'wK':
                self.WhiteKingLocation = (move.StartRow, move.StartCol)
            elif move.PieceMoved == "bK":
                self.BlackKingLocation = (move.StartRow, move.StartCol)
            # Undo en passant move
            if move.IsEnpassantMove:
                # Leave the landing square blank
                self.board[move.EndRow,move.EndCol] = '--'
                # Restore the captured pawn at its original location
                self.board[move.StartRow,move.EndCol] = move.PieceCaptured

            # Undo a 2-square pawn advance (reset en passant possibility)
            if move.PieceMoved == 'p' and abs(move.StartRow - move.EndRow) == 2:
                self.EnpassantPossible = ()
            # Undo castling rights
            self.CastleRightsLog.pop()  # Get rid of the most recent castling rights
            # Set the current castling rights to the last one in the log (before the move)
            newRights = self.CastleRightsLog[-1]
            self.CurrentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            # Undo castling moves
            if move.IsCastleMove:
                if move.EndCol - move.StartCol == 2:  # Kingside
                    # Undo the rook's move during kingside castling
                    self.board[move.EndRow,move.EndCol + 1] = self.board[move.EndRow,
                        move.EndCol - 1]  # Move rook back to its original position
                    self.board[move.EndRow,move.EndCol - 1] = '--'  # Clear the square the rook was moved to
                else:  # Queenside
                    # Undo the rook's move during queenside castling
                    self.board[move.EndRow,move.EndCol - 2] = self.board[move.EndRow,
                        move.EndCol + 1]  # Move rook back to its original position
                    self.board[move.EndRow,move.EndCol + 1] = '--'  # Clear the square the rook was moved to

    def UpdateCastleRights(self, move):
        # If a white king moves, both white castling rights are lost
        if move.PieceMoved == 'wK':
            self.CurrentCastlingRight.wks = False
            self.CurrentCastlingRight.wqs = False
        # If a black king moves, both black castling rights are lost
        elif move.PieceMoved == 'bK':
            self.CurrentCastlingRight.bks = False
            self.CurrentCastlingRight.bqs = False
        # If a white rook moves
        elif move.PieceMoved == 'wR':
            if move.StartRow == 7:  # White rooks are on row 7
                if move.StartCol == 0:  # Left rook (queen-side)
                    self.CurrentCastlingRight.wqs = False
                elif move.StartCol == 7:  # Right rook (king-side)
                    self.CurrentCastlingRight.wks = False
        # If a black rook moves
        elif move.PieceMoved == 'bR':
            if move.StartRow == 0:  # Black rooks are on row 0
                if move.StartCol == 0:  # Left rook (queen-side)
                    self.CurrentCastlingRight.bqs = False
                elif move.StartCol == 7:  # Right rook (king-side)
                    self.CurrentCastlingRight.bks = False

    def GetValidMoves(self):
        tempEnpassantPossible = self.EnpassantPossible
        tempCastleRights = CastleRights(self.CurrentCastlingRight.wks, self.CurrentCastlingRight.bks,
                                             self.CurrentCastlingRight.wqs, self.CurrentCastlingRight.bqs)
        # 1: Generate all possible moves
        moves = self.GetAllPossibleMoves()
        if self.WhiteToMove:
            self.GetCastleMoves(self.WhiteKingLocation[0], self.WhiteKingLocation[1], moves)
        else:
            self.GetCastleMoves(self.BlackKingLocation[0], self.BlackKingLocation[1], moves)
        # 2: For each move, make the move
        for i in range(len(moves) - 1, -1, -1):  # Go backwards through the list when removing items
            self.MakeMove(moves[i])

            # 3: Generate all opponent's moves
            self.WhiteToMove = not self.WhiteToMove

            # 4: Check if the king is in check after the move
            if self.inCheck():  # If the king is in check, the move is not valid
                moves.remove(moves[i])

            # 5: Restore the turn
            self.WhiteToMove = not self.WhiteToMove

            # 6: Undo the move
            self.UndoMove()
        if len(moves) == 0:  # No valid moves left, so either checkmate or stalemate
            if self.inCheck():
                self.CheckMate = True  # The player is in check and has no valid moves, so checkmate
                self.StaleMate = False
            else:
                self.StaleMate = True  # The player is not in check but has no valid moves, so stalemate
                self.CheckMate = False
        else:
            self.CheckMate = False  # There are valid moves, so not checkmate
            self.StaleMate = False  # There are valid moves, so not stalemate
        self.EnpassantPossible=tempEnpassantPossible
        self.CurrentCastlingRight = tempCastleRights
        # 7: Return the valid moves
        return moves

    def inCheck(self):
        if self.WhiteToMove:
            # Check if the white king's position is under attack
            return self.squareUnderAttack(self.WhiteKingLocation[0], self.WhiteKingLocation[1])
        else:
            # Check if the black king's position is under attack
            return self.squareUnderAttack(self.BlackKingLocation[0], self.BlackKingLocation[1])

    def squareUnderAttack(self, r, c, skip_castling_check=False):
        # Switch to opponent's turn
        self.WhiteToMove = not self.WhiteToMove
        # Get all opponent's possible moves
        if skip_castling_check:
            return False
        oppMoves = self.GetAllPossibleMoves()
        # Switch turns back to original player
        self.WhiteToMove = not self.WhiteToMove

        # Check if any opponent move attacks the square (r, c)
        for move in oppMoves:
            if move.EndRow == r and move.EndCol == c:  # Square is under attack
                return True
        return False

    def GetAllPossibleMoves(self):
        moves=[]
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r,c][0]
                if (turn=="w" and self.WhiteToMove) or (turn=="b" and not self.WhiteToMove ):
                    piece=self.board[r,c][1]
                    self.MoveFunction[piece](r,c,moves)
        return moves
    def GetPawnMoves(self, r, c, moves):
        if self.WhiteToMove:  # white pawn moves
            if self.board[r-1,c]=="--":
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2,c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))

            # captures
            if c - 1 >= 0:  # capture to the left
                if self.board[r - 1,c - 1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.EnpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, IsEnpassantMove=True))
            if c + 1 <= 7:  # capture to the right
                if self.board[r - 1,c + 1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.EnpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, IsEnpassantMove=True))

        else:  # black pawn moves
            if self.board[r + 1,c] == "--":  # 1 square pawn advance
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2,c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))

            # captures
            if c - 1 >= 0:  # capture to the left
                if self.board[r + 1,c - 1][0] == 'w':  # enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r +1, c - 1) == self.EnpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, IsEnpassantMove=True))
            if c + 1 <= 7:  # capture to the right
                if self.board[r + 1,c + 1][0] == 'w':  # enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.EnpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, IsEnpassantMove=True))

    def GetRookMoves(self,r,c,moves):
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]  # up, left, down, right
        EnemyColor = "b" if self.WhiteToMove else "w"

        for d in directions:
            for i in range(1, 8):  # Sliding up to 7 squares in a direction
                EndRow = r + d[0] * i
                EndCol = c + d[1] * i
                if 0 <= EndRow < 8 and 0 <= EndCol < 8:  # Ensure within board limits
                    EndPiece = self.board[EndRow,EndCol]
                    if EndPiece == "--":  # Empty space, valid move
                        moves.append(Move((r, c), (EndRow, EndCol), self.board))
                    elif EndPiece[0] == EnemyColor:  # Enemy piece, valid move
                        moves.append(Move((r, c), (EndRow, EndCol), self.board))
                        break  # Can't slide past enemy
                    else:
                        break  # Friendly piece, invalid move
                else:
                    break  # Off the board
    def GetKnightMoves(self, r, c, moves):
        KnightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        AllyColor = "w" if self.WhiteToMove else "b"

        for m in KnightMoves:
            EndRow = r + m[0]
            EndCol = c + m[1]
            if 0 <= EndRow < 8 and 0 <= EndCol < 8:  # Ensure within board limits
                EndPiece = self.board[EndRow,EndCol]
                if EndPiece[0] != AllyColor:  # Not an ally piece (either empty or enemy)
                    moves.append(Move((r, c), (EndRow, EndCol), self.board))

    def GetBishopMoves(self, r, c, moves):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Diagonal directions
        EnemyColor = "b" if self.WhiteToMove else "w"

        for d in directions:
            for i in range(1, 8):  # Sliding up to 7 squares in a direction
                EndRow = r + d[0] * i
                EndCol = c + d[1] * i
                if 0 <= EndRow < 8 and 0 <= EndCol < 8:  # Ensure within board limits
                    EndPiece = self.board[EndRow,EndCol]
                    if EndPiece == "--":  # Empty space, valid move
                        moves.append(Move((r, c), (EndRow, EndCol), self.board))
                    elif EndPiece[0] == EnemyColor:  # Enemy piece, valid move
                        moves.append(Move((r, c), (EndRow, EndCol), self.board))
                        break  # Can't slide past enemy
                    else:
                        break  # Friendly piece, invalid move
                else:
                    break  # Off the board

    def GetQueenMoves(self, r, c, moves):
        self.GetRookMoves(r, c, moves)
        self.GetBishopMoves(r, c, moves)

    def GetKingMoves(self, r, c, moves):
        kingMoves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        allyColor = "w" if self.WhiteToMove else "b"

        for i in range(8):
            EndRow = r + kingMoves[i][0]
            EndCol = c + kingMoves[i][1]
            if 0 <= EndRow < 8 and 0 <= EndCol < 8:  # Ensure within board limits
                endPiece = self.board[EndRow,EndCol]
                if endPiece[0] != allyColor:  # Not an ally piece (either empty or enemy)
                    moves.append(Move((r, c), (EndRow, EndCol), self.board))


    def GetCastleMoves(self, r, c, moves):
        # Can't castle while in check
        if self.squareUnderAttack(r, c):
            return

        # Kingside castling
        if (self.WhiteToMove and self.CurrentCastlingRight.wks) or (
                not self.WhiteToMove and self.CurrentCastlingRight.bks):
            self.GetKingsideCastleMoves(r, c, moves)

        # Queenside castling
        if (self.WhiteToMove and self.CurrentCastlingRight.wqs) or (
                not self.WhiteToMove and self.CurrentCastlingRight.bqs):
            self.GetQueensideCastleMoves(r, c, moves)

    # Kingside castling move
    def GetKingsideCastleMoves(self, r, c, moves):
        # Check if the squares between the king and the rook are empty
        if self.board[r,c + 1] == '--' and self.board[r,c + 2] == '--':
            # Ensure the squares are not under attack
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                # Add the castling move to the move list
                moves.append(Move((r, c), (r, c + 2), self.board, IsCastleMove=True))

    # Queenside castling move
    def GetQueensideCastleMoves(self, r, c, moves):
        # Check if the squares between the king and the rook are empty
        if self.board[r,c - 1] == '--' and self.board[r,c - 2] == '--' and self.board[r,c - 3] == '--':
            # Ensure the squares are not under attack
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                # Add the castling move to the move list
                moves.append(Move((r, c), (r, c - 2), self.board,IsCastleMove=True))


class CastleRights :
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks= bks
        self.wqs= wqs
        self.bqs= bqs

class Move:
    RanksToRows={"1":7,"2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    RowsToRanks={ v:k for k,v in  RanksToRows.items()}
    FilesToCols={"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    ColsToFiles={ v:k for k,v in  FilesToCols.items()}

    def __init__(self, StartSq, EndSq, board, IsEnpassantMove=False,IsCastleMove=False):
        self.StartRow=StartSq[0]
        self.StartCol=StartSq[1]
        self.EndRow=EndSq[0]
        self.EndCol=EndSq[1]
        self.PieceMoved=board[self.StartRow,self.StartCol]
        self.PieceCaptured=board[self.EndRow,self.EndCol]
        self.IsPawnPromotion = False
        if (self.PieceMoved =='wp' and self.EndRow == 0) or (self.PieceMoved == 'bp' and self.EndRow == 7) :
            self.IsPawnPromotion = True
        self.IsEnpassantMove = IsEnpassantMove
        if self.IsEnpassantMove:
            self.PieceCaptured = 'wp' if self.PieceMoved == "bp" else "bp"
        self.IsCastleMove = IsCastleMove
        self.MoveId = self.StartRow * 1000 + self.StartCol * 100 + self.EndRow * 10 + self.EndCol
        self.StartSq=StartSq
        self.EndSq=EndSq
        self.board=board

    def __str__(self):
        start_square = self.GetRankFile(self.StartRow, self.StartCol)
        end_square = self.GetRankFile(self.EndRow, self.EndCol)
        return f"{start_square}{end_square}"

    def GetChessNotification(self):
       # x = Move(self.StartSq, self.EndSq, self.board)
        #game_state = GameState()  # Create an instance of the GameState class
        #AIMove = get_AIMove()
        #if x in game_state.GetValidMoves():
        return  self.GetRankFile(self.StartRow,self.StartCol) + self.GetRankFile(self.EndRow, self.EndCol)
        #print(AIMove)

    def GetRankFile(self,r,c):
        return self.ColsToFiles[c] + self.RowsToRanks[r]

    #Overriding the equals method
    def __eq__(self,other):
        if isinstance(other,Move):
            return self.MoveId==other.MoveId
        return False




