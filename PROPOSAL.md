# Proposal

## Problem Statement

I love playing games, I always wanted to code up an entire game from scratch myself and I thought what better game can it be than chess. Chess is one of my favorite board games. Just a 8x8 grid with few pieces having different valid moves makes up the entire game and everything composes to become such a complex game. It's beauty lies in the simplicity of the game and the enormous amount of combinations that could be played on it (literally greater than the atoms in the universe).

You might think what's new in chess? There are so many versions of chess online. But I want to build an open-source modular chess engine where I could modify the capabilities of each piece like maybe give the knight's ability to the queen, introduce new pieces with special powers or add different ai bots using different strategies. So the main contribution of this project is not so much as to build a new game but to provide an open source chess engine that people can tweak as well as from a pedagogical standpoint show what a good OOP design is.

I want this chess engine to have basic chess game features that includes checkmate detection, special moves (castling and en passant) and ability to try out different strategies for bots. The key challanges here would be how to design such modular chess engine using object oriented principles and how to represent the state of the game plus move history in python data structures.

This is part of my Coding Cafe course @ Plaksha. The course goes over basics of python, data structures and object-oriented principles all of which is extememly essential for a project like this.


## Key Features
- OOP Chess Library (eg g = Game(),=  g.move(KNIGHT, E4), g.isOver())
- PyGame wrapper
- Chess Board, Pieces, Valid Moves
- Checkmate detector
- Special moves such as castling and en passant
- Two Player Chess
- Chess bot: random move
- Chess bot: material-counting greedy bot (optional)
- Open Chess API (future)

## Challanges
- Good Object-Oriented Design
- Chess Game current state representation in python data structures
- Evaluate different bot strategies
- Learn PyGame and implement a wrapper on top of this engine to be able to visualize the current state and make moves visually

## Timeline & Feasibility

- Refer [PLAN.md](PLAN.md)