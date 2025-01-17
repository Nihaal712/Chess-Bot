'''
This is our main driver file. It will be responsible for handling user input and
displaying the current game state object'''
from string import whitespace

import pygame as p
from Chess import ChessEngine,SmartMoveFinder
import chess
HEIGHT=WIDTH=512
DIMENSION=8
SQ_SIZE=HEIGHT//8
MAX_FPS=15
IMAGES={}
"""
Initialize global dicctionary of images. This will be called exactly once in the main.
"""
def LoadImages () :
    pieces = ["wR","wN","wB","wK","wQ","wp","bR","bN","bB","bK","bQ","bp"]
    for piece in pieces:
        IMAGES[piece]=p.transform.scale(p.image.load("images/"+ piece +".png"),(SQ_SIZE,SQ_SIZE))
        #Note:we can access an image by saying 'IMAGES['wp']'
"""
The main driver for our code. this will be handling the input and updating the output.
"""
def main():
    p.init()
    screen=p.display.set_mode((HEIGHT,WIDTH))
    clock=p.time.Clock()
    screen.fill(p.Color("white"))
    gs=ChessEngine.GameState()
    LoadImages() #load images only once before using while loop
    ValidMoves=gs.GetValidMoves()
    MoveMade=False #Flag variable when a move is made
    Animate=False
    Running=True
    movestillpresent=[]
    SqSelected=()
    PlayerClicks=[]
    GameOver=False
    PlayerOne=True
    PlayerTwo=False
    while Running:
        HumanTurn = (gs.WhiteToMove and PlayerOne) or (not gs.WhiteToMove and PlayerTwo)
        for e in p.event.get():
            if e.type==p.QUIT:
                Running=False
            #Mouse Handler
            elif e.type==p.MOUSEBUTTONDOWN :
                if not GameOver and HumanTurn:
                    location=p.mouse.get_pos()
                    col=location[0]//SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if SqSelected==(row,col):
                        SqSelected=()
                        PlayerClicks=[]
                    else:
                        SqSelected=(row,col)
                        PlayerClicks.append(SqSelected)
                    if len(PlayerClicks) ==2:
                        move=ChessEngine.Move(PlayerClicks[0],PlayerClicks[1],gs.board)
                        print(move.GetChessNotification())
                        movestillpresent.append(move.GetChessNotification())
                        for i in range(len(ValidMoves)):
                            if move == ValidMoves[i]:
                                gs.MakeMove(ValidMoves[i])
                                MoveMade=True
                                Animate=True
                                SqSelected = ()
                                PlayerClicks = []
                        if not MoveMade:
                            PlayerClicks=[SqSelected]
            #Key Handler
            elif e.type==p.KEYDOWN:
                if e.key== p.K_z: # press z to undo move
                    gs.UndoMove()
                    MoveMade = True
                    Animate=False
                if e.key==p.K_r: # reset the board
                    gs=ChessEngine.GameState()
                    ValidMoves=gs.GetValidMoves()
                    SqSelected=()
                    PlayerClicks=[]
                    MoveMade=False
                    Animate=False

        #AI MOVE FINDER
        if not GameOver and not HumanTurn:
            AIMove=SmartMoveFinder.FindBestMove(gs,ValidMoves)
            if AIMove==None:
                AIMove=SmartMoveFinder.FindRandomMove(ValidMoves)
            print(AIMove)
            movestillpresent.append(AIMove.GetChessNotification())
            print(movestillpresent)
            gs.MakeMove(AIMove)
            MoveMade=True
            Animate=True




        if MoveMade:
            if Animate:
                AnimateMove(gs.MoveLog[-1], screen, gs.board, clock)
            ValidMoves=gs.GetValidMoves()
            MoveMade = False
            Animate=False

        DrawGameState(screen,gs,ValidMoves,SqSelected)

        if gs.CheckMate:
            GameOver=True
            if gs.WhiteToMove:
                DrawText(screen,"Black wins by Checkmate")
            else:
                DrawText(screen,"White wins by Checkmate")
        elif gs.StaleMate:
            GameOver=True
            DrawText(screen,"StaleMate")

        clock.tick(MAX_FPS)
        p.display.flip()

""""
For game graphics
"""
def DrawGameState(screen,gs,ValidMoves,SqSelected):
    DrawBoard(screen)#draw squares on the screen
    DrawPieces(screen,gs.board)# draw pieces on board
    HighlightSquare(screen,gs,ValidMoves, SqSelected)

def DrawBoard(screen):
    global colors
    colors=[p.Color("white"),p.Color("light green")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color=colors[((r + c)%2)]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def HighlightSquare(screen,gs,ValidMoves, SqSelected):
    if SqSelected != ():
        r, c = SqSelected
        if gs.board[r,c][0]==("w" if gs.WhiteToMove else "b"): #sqselected is piece that can be moved
            s=p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100)# transparent value 0-transparent, 255-opaque
            s.fill(p.Color("blue"))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            #highlight move coming out from the sqselected
            s.fill(p.Color("yellow"))
            for move in ValidMoves:
                if move.StartRow==r and move.StartCol==c:
                    screen.blit(s,(move.EndCol*SQ_SIZE,move.EndRow*SQ_SIZE))

def DrawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece=board[r,c]
            if piece !="--" :
                screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def AnimateMove(move,screen,board,clock):
    global colors
    coords=[] #list of coords that the animation will move through
    dR=move.EndRow-move.StartRow
    dC=move.EndCol-move.StartCol
    FramesPerSquare=10 #frames to move one square
    FrameCount=(abs(dR)+abs(dC))*FramesPerSquare
    for frame in range(FrameCount+1):
        r,c=(move.StartRow+dR*frame/FrameCount,move.StartCol+dC*frame/FrameCount)
        DrawBoard(screen)
        DrawPieces(screen, board)
        color=colors[(move.EndRow+move.EndCol)%2]
        EndSquare=p.Rect(move.EndCol*SQ_SIZE,move.EndRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen,color,EndSquare)
        if move.PieceCaptured !="--":
            screen.blit(IMAGES[move.PieceCaptured],EndSquare)
        screen.blit(IMAGES[move.PieceMoved],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def DrawText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)  # Corrected font name
    TextObject = font.render(text, True, p.Color("Black"))  # Enabled anti-aliasing (True)

    # Centering the text
    TextLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH / 2 - TextObject.get_width() / 2,
        HEIGHT / 2 - TextObject.get_height() / 2
    )

    # Blitting the text onto the screen
    screen.blit(TextObject, TextLocation)


if __name__=="__main__":
    main()








