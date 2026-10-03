## Important Classes
- Piece
    - abilities: cross, straight, jump, l-shape, step, ahead, crosskill
    - it will not know where it is!
- Board
    - 2d array of 64 cell
    - dictionary (cell -> piece)?
    - instantiate 32 pieces
    - instantiate 64 cells
    - place intial pieces on the board
    - know where all the pieces are
    - 
- GameEngine
    - Players
    - Turn
    - Checkmate
    - is move valid?
- Moves
    - Variables: piece, startcell, endcell
- Cell
    - colNumber, rowNumber
    - getColAlphabet()
    - piece: null if empty 
    - row number

- Player
    - name, stats...

- Ability

## Class Descriptions

1. Piece Class
    - This class will have every chess piece and their abilities (how it moves) like cross, L shape, jump etc. But a piece doesn't know where it is on the board!
2. Board Class
    - The board class will basically render the entire chess board and have 64 cells, with 32 pieces and would place the pieces at their start position whenever a new game is played. Board would know where each piece is!
3. GameEngine
    - The GameEngine class will keep a track of the players who are currently playing against each other and keep a track of also whose turn is it next. While doing so, it will also check if a player has been checkmated and check if the move which player wants to play is legal or not.
4. Moves
    - The Moves class would have piece, startPos, and endPos as its member variables and would basically define a move from a specific piece from point A to point B.
5. Cell
    - A cell would be a part of the 8x8 Chess Board and would hold information like if the cell contains any piece or not. It would have a column number, row number for indexing and would show the final positions as (a,b,c,d,e,f,g,h,) x (1,2,3,4,5,6,7,8)
6. Player
    - The Player Class would hold the stats, name of the Player playing the match
7. Ability
    - ENUM, list of abilities supported

## TODO by Tommorow
for each class, list the variables which will capture the information needed by that class and functions which will cover all its responsibilities.
