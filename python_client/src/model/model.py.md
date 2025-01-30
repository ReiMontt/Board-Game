# Model Class Documentation

## Table of Contents

* [1. Overview](#1-overview)
* [2. Class `Model`](#2-class-model)
    * [2.1 Constructor `__init__`](#21-constructor-__init__)
    * [2.2 Method `new_game`](#22-method-new_game)
    * [2.3 Method `_get_all_enemy_moves`](#23-method-_get_all_enemy_moves)
    * [2.4 Method `_is_draw`](#24-method-_is_draw)
    * [2.5 Method `_is_checkmate`](#25-method-_is_checkmate)
    * [2.6 Method `_copy_state`](#26-method-_copy_state)
    * [2.7 Method `piece_select`](#27-method-piece_select)
    * [2.8 Method `_is_move_valid`](#28-method-_is_move_valid)
    * [2.9 Method `move`](#29-method-move)
    * [2.10 Method `_is_drop_valid`](#210-method-_is_drop_valid)
    * [2.11 Method `drop`](#211-method-drop)
    * [2.12 Method `undo`](#212-method-undo)
    * [2.13 Property `state`](#213-property-state)


<a name="1-overview"></a>
## 1. Overview

This document provides internal code documentation for the `Model` class, which manages the game state and logic for a turn-based board game.  The model uses dataclasses for efficient state representation and manipulation.

<a name="2-class-model"></a>
## 2. Class `Model`

The `Model` class encapsulates the game's logic, including board setup, move validation, game state transitions, and win/draw conditions.

<a name="21-constructor-__init__"></a>
### 2.1 Constructor `__init__`

```python
def __init__(self, board: Board, piece_info: PieceInfo):
    self._max_moves = 3
    self._board = board
    self._piece_info = piece_info
    self.new_game()
```

The constructor initializes the `Model` with a `Board` and `PieceInfo` object. It sets the maximum number of moves per turn to 3 and calls `new_game()` to start a new game.

<a name="22-method-new_game"></a>
### 2.2 Method `new_game`

```python
def new_game(self):
    self._board.setup(self._piece_info)
    self._state: GameState = GameState(
        game_status = GameStatus.ongoing,
        board_status = self._board.get_board,
        turn = Player.p1,
        selected_piece = None,
        moves_left = self._max_moves,
        P1_captured = [],
        P2_captured = []
    )

    self._prev_state: GameState | None = None
    self._recent_state: list[GameState] = []
```

This method sets up a new game by initializing the board using the provided `piece_info` and resetting the game state.  It sets the game status to `ongoing`, the turn to player 1 (`Player.p1`), and the number of moves left to the maximum.  Captured pieces lists are also initialized as empty.


<a name="23-method-_get_all_enemy_moves"></a>
### 2.3 Method `_get_all_enemy_moves`

```python
def _get_all_enemy_moves(self) -> list[Location]:
    all_pieces: list[Piece] = []

    for row in self._state.board_status:
        for piece in row:
            if piece is not None:
                all_pieces.append(piece)

    all_moves: list[Location] = []

    for piece in all_pieces:
        for delta_x, delta_y in piece.get_moves:
            if piece.get_location is not None:
                new_row = piece.get_location.row - delta_y
                new_col = piece.get_location.col - delta_x
                if piece.get_player is not self._state.turn:
                    all_moves.append(Location(row = new_row, col = new_col))

    return all_moves
```

This method iterates through all pieces on the board. If a piece belongs to the opponent, it calculates all possible moves for that piece and adds the resulting locations to a list.  This is used for AI or determining potential threats.  Note that the algorithm assumes moves are relative to the piece's current location (`delta_x`, `delta_y`).


<a name="24-method-_is_draw"></a>
### 2.4 Method `_is_draw`

```python
def _is_draw(self) -> bool:
    return (self._is_checkmate(Player.p1) and self._is_checkmate(Player.p2))
```

A draw is declared if both players are in checkmate.


<a name="25-method-_is_checkmate"></a>
### 2.5 Method `_is_checkmate`

```python
def _is_checkmate(self, player: Player) -> bool:
    # ... (complex logic, see detailed explanation below)
    return False #simplified return
```

This method determines if a player is in checkmate.  It's a complex function, explained in detail below:

**Algorithm:**

1. **Identify Pieces:** The function first separates pieces into `protected_pieces` (pieces with the `Trait.protected` trait) and `counter_pieces` (other pieces) belonging to the opponent.

2. **Find Possible Moves:** It then iterates through `protected_pieces`, calculating possible move locations.  These locations are added to the `paths` list if they are empty or to the `infiltrators` list if they contain a piece belonging to the checked player.

3. **Identify Counter Locations:**  It similarly iterates through `counter_pieces`, identifying locations that threaten the checked player's pieces and stores them in `counter_locations`.

4. **Checkmate Condition:** If there are no available `paths` for the protected pieces to escape, the function checks if any `infiltrators` (opponent pieces on the same locations as the checked pieces) exist. If infiltrators exist and their number is greater than 1, it is checkmate.  Otherwise, it's not checkmate.  If there are available paths, it's not checkmate.


<a name="26-method-_copy_state"></a>
### 2.6 Method `_copy_state`

```python
def _copy_state(self) -> GameState:
    # ... (detailed deep copy logic, see explanation below)
    return GameState(...) #simplified return
```

This method creates a deep copy of the current game state.  It iterates through all elements of the `GameState` and recreates them to avoid modifying the original state unintentionally.  This is crucial for undo functionality.


<a name="27-method-piece_select"></a>
### 2.7 Method `piece_select`

```python
def piece_select(self, piece: Piece, player: Player):
    if piece.get_player is self._state.turn and player is self._state.turn:
        self._state = self.state.change_to({
            'selected_piece': piece
        })

        self._prev_state = self._copy_state()
```

This method selects a piece for a move or drop. It checks if the selected piece belongs to the current player. If so, it updates the game state by setting the `selected_piece` and makes a copy of the state using `_copy_state()` for potential undo.


<a name="28-method-_is_move_valid"></a>
### 2.8 Method `_is_move_valid`

```python
def _is_move_valid(self, target_location: Location) -> bool:
    # ... (move validation logic, see explanation below)
    return False #simplified return
```

This method checks if a move to the `target_location` is valid.

**Algorithm:**

1. **Check for Selected Piece:** It first verifies that a piece has been selected.

2. **Target Piece Check:** It then checks if a piece already exists at the target location. If so, it verifies that the target piece does not belong to the same player and is not protected.

3. **Move Range Check:** The method then iterates over the possible moves of the selected piece to determine if the `target_location` is within the valid move range.


<a name="29-method-move"></a>
### 2.9 Method `move`

```python
def move(self, target_location: Location, player: Player):
    # ... (complex move logic, see explanation below)
```

This method executes a move if it's valid, updating the board and game state accordingly.  It handles capturing pieces, updating the turn, checking for win/draw conditions, and managing move counters.

**Algorithm:**

1. **Validation:** It first checks if the move is valid using `_is_move_valid()`.

2. **Capture:** If a piece exists at the target location, it is captured and added to the appropriate captured pieces list.

3. **Move Piece:** The selected piece is moved to the `target_location` on the board.

4. **Game Status Check:** The method then checks if the move results in a draw or a checkmate using `_is_draw()` and `_is_checkmate()`.  The game status is updated accordingly.

5. **Turn and Moves Update:** The turn and moves left are updated.

6. **Undo History:** The previous game state is added to the `_recent_state` list for undo functionality.


<a name="210-method-_is_drop_valid"></a>
### 2.10 Method `_is_drop_valid`

```python
def _is_drop_valid(self, target_location: Location):
    # ... (drop validation logic, see explanation below)
    return False #simplified return
```

This method checks if dropping a piece at the `target_location` is valid.  It ensures the drop location doesn't directly expose any protected pieces to attack.

**Algorithm:**

1. **Identify Protected Pieces:** It identifies all protected enemy pieces.

2. **Check Paths:** It checks if any paths from the protected pieces to the target location exist.

3. **Validity:** If a path exists, the drop is invalid; otherwise, it's valid.


<a name="211-method-drop"></a>
### 2.11 Method `drop`

```python
def drop(self, target_location: Location, player: Player):
    # ... (drop logic, see explanation below)
```

This method executes a drop action, placing a selected piece onto the board at a given location.  Similar to `move`, it manages game state updates, win/draw conditions, and undo history.

**Algorithm:**  It is similar to the `move` method. The main difference is that it places the selected piece onto the board instead of moving an existing piece.


<a name="212-method-undo"></a>
### 2.12 Method `undo`

```python
def undo(self, player: Player):
    if self._recent_state[-1].selected_piece is not None:
        if self._recent_state[-1].selected_piece.get_location is not None and player is self._recent_state[-1].turn:
            if Trait.can_undo in self._recent_state[-1].selected_piece.get_traits:
                self._state = self._recent_state[-1]
                self._state = self.state.change_to({
                    'selected_piece': None
                })
                self._recent_state[:-1]
```

This method performs an undo action, reverting the game state to the previous one if the piece has a `Trait.can_undo` trait, the player is the same, and a piece was selected in the previous state.  It removes the last element from the `_recent_state` list.


<a name="213-property-state"></a>
### 2.13 Property `state`

```python
@property
def state(self) -> GameState:
    return replace(self._state)
```

This property returns a modified copy of the current game state using `replace()`.  This prevents direct modification of the internal `_state` variable.
