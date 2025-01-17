import random

PieceScore={"K":0,"Q":9,"R":5,"B":3,"N":3,"p":1}
CHECKMATE=1000
STALEMATE=0

def FindRandomMove(ValidMoves):
       return ValidMoves[random.randint(0,len(ValidMoves)-1)]


def FindBestMove(gs,ValidMoves):
    TurnMultiplier = 1 if gs.WhiteToMove else -1  # Multiplier to evaluate from the perspective of the player to move
    OpponentMinMaxScore = CHECKMATE  # Initialize the maximum score to a very low value (representing losing for the player)
    BestPlayerMove = None  # Initialize the best move as None
    random.shuffle(ValidMoves)
    for PlayerMove in ValidMoves:  # Loop over all valid moves
        gs.MakeMove(PlayerMove)  # Make the move on the game state
        OpponentsMoves=gs.GetValidMoves()
        OpponentMaxScore=-CHECKMATE
        for OpponentsMove in OpponentsMoves:
            gs.MakeMove(OpponentsMove)
            if gs.CheckMate:  # Check if the game is in checkmate after the move
                score = -TurnMultiplier *CHECKMATE  # Winning score for the current player
            elif gs.StaleMate:  # Check if the game is in stalemate
                score = STALEMATE  # Neutral score for stalemate
            else:
                # If no checkmate or stalemate, evaluate the board based on material
                score = -TurnMultiplier * ScoreMaterial(gs.board)

            # If the score for this move is better than the current max score, update the best move
            if score > OpponentMaxScore:
                OpponentMaxScore = score  # Update the maximum score found so far


            gs.UndoMove()  # Undo the move to restore the board state for the next iteration
        if OpponentMaxScore < OpponentMinMaxScore:
            OpponentMinMaxScore=OpponentMaxScore
            BestPlayerMove=PlayerMove
        gs.UndoMove()
    return BestPlayerMove  # Return the best move found


"""
score the board on base of material
"""
def ScoreMaterial(board):
    score=0
    for row in board:
        for square in row:
            if square[0]=="w":
                score+=PieceScore[square[1]]
            elif square[0]=="b":
                score-=PieceScore[square[1]]

    return score

