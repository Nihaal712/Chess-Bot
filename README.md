# Chess Bot

A Python-based chess engine designed to simulate and analyze chess games. The bot integrates a graphical user interface (GUI), implements chess rules (including special moves like castling, en passant, and pawn promotion), and uses AI to calculate and make optimal moves.

## Features

- **GUI for Gameplay**: An interactive chessboard built using `pygame` for playing chess against the bot or other players.
- **AI-powered Moves**: The bot leverages the minimax algorithm with alpha-beta pruning for decision-making.
- **Chess Rules Implementation**:
  - Castling
  - En passant
  - Pawn promotion
- **Move Validation**: Ensures all moves follow chess rules and accounts for checks and checkmates.
- **Custom Board States**: Ability to load and analyze custom chess board setups.

## Project Structure

Chess-Bot/
- **ChessMain.py**: Entry point for the chess game with GUI.
- **ChessEngine.py**: Core logic for move generation, validation, and board state management.
- **README.md**: Documentation for the project.
- **requirements.txt**: Python dependencies required to run the project.
- **resources/**: Contains images for chess pieces and the board.
  - **wP.png**: Example: White pawn image.
  - **bP.png**: Example: Black pawn image.
  - `...`: Other chess piece images.
- **tests/**: Unit tests for validating engine functionality.
  - **test_chess.py**: Test cases for move generation, validation, and special rules.

## Requirements

To run the chess bot, ensure the following dependencies are installed:

- Python 3.8 or later
- Libraries:
  - `pygame`
  - `numpy`
  - `chess`

## Further Development

Currently, the project uses a **Naive LSTM** method for move prediction. In the future, we plan to enhance this approach by converting the chessboard dataset into a vector structure that captures spatial relationships between pieces. This will allow us to integrate CNN and LSTM together for better move prediction:
- **CNN** will capture spatial patterns of piece interactions.
- **LSTM** will handle the sequential nature of moves.

Additionally, the **`chess.ipynb`** notebook is not yet integrated with **ChessMain.py**. We plan to merge it into the main codebase to improve the overall prediction system and make it more robust.
