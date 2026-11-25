# Plan

Status: [x] done, [~] partly done, [ ] not started

- Week 05: Proposal, Timeline, Dev Environment, initial repo
  - [x] [Proposal.md](PROPOSAL.md)
  - [x] [Plan.md](PLAN.md)
- Week 06: Architectural Design
  - [x] State Representation
  - [x] OOP Design ([ARCHITECTURE.md](ARCHITECTURE.md))
- Week 07: Phase 1
  - [x] Map OOP Design to classes
  - [x] Implement valid moves for pieces
- Week 08: Phase 2
  - [x] Complete the basic chess engine
  - [x] Player by player move capability
- Week 09: Phase 3 (midpoint checkpoint)
  - [x] Learn PyGame
  - [x] Implement PyGame wrapper around the library
- Week 10: Phase 4 (feature freeze)
  - [x] Checkmate detector (plus stalemate)
  - [x] Special moves: castling and en passant
  - [x] Random move bot
  - [ ] Material-counting greedy bot (optional)
- Week 11: Integration and Testing
  - [~] Testing: rules checked with test games and standard move counts (perft), 15 random bot-vs-bot games all finish without crashing
  - [ ] Try playing games with friends and against supported bots
  - [~] Debug any errors and release first MVP (fixed: undo after resigning took back a move)
- Week 12: Refinement & Optimization
  - [x] En passant
  - [ ] Choice of piece on promotion
  - [x] Draw rules (50-move rule, threefold repetition, insufficient material)
  - [ ] Faster legal-move checking (make/undo a move instead of copying the board)
- Week 13: Documentation
  - [x] README updated to match the code
  - [x] ARCHITECTURE.md updated to match the code
- Week 14: Presentation Prep & Buffer
- Week 15: Final Presentation
- Week 16: home 🏡 ;)

## Done beyond the original plan

- Undo and resign
- Helpful error messages for illegal moves
- Legal-move highlights, check highlight and move history in the GUI
