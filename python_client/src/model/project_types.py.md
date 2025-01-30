# Chogi Game Code Documentation

## Table of Contents

* [1. Introduction](#1-introduction)
* [2. Data Structures](#2-data-structures)
    * [2.1. `Player` Enum](#21-player-enum)
    * [2.2. `GameStatus` Enum](#22-gamestatus-enum)
    * [2.3. `Location` Data Class](#23-location-data-class)
    * [2.4. `PieceInfo` Protocol](#24-pieceinfo-protocol)
    * [2.5. `Board` Protocol](#25-board-protocol)
    * [2.6. `GameState` Data Class](#26-gamestate-data-class)
    * [2.7. `PieceType` Enum](#27-piecetype-enum)
    * [2.8. `Trait` Enum](#28-trait-enum)
    * [2.9. `Moves` Protocol](#29-moves-protocol)
    * [2.10. `Piece` Class](#210-piece-class)
* [3. Game Logic Classes](#3-game-logic-classes)
    * [3.1. `Moves` Implementations](#31-moves-implementations)
        * [3.1.1. `ChickMoves` Class](#311-chickmoves-class)
        * [3.1.2. `ElephantMoves` Class](#312-elephantmoves-class)
        * [3.1.3. `GiraffeMoves` Class](#313-giraffemoves-class)
        * [3.1.4. `MonkeyMoves` Class](#314-monkeymoves-class)
        * [3.1.5. `LionMoves` Class](#315-lionmoves-class)
    * [3.2. `ChogiPieceInfo` Class](#32-chogipieceinfo-class)
    * [3.3. `ChogiBoard` Class](#33-chogiborad-class)


<a name="1-introduction"></a>
## 1. Introduction

This document details the code implementation of a Chogi game.  The code utilizes dataclasses, enums, and protocols to represent the game state, pieces, and board.


<a name="2-data-structures"></a>
## 2. Data Structures

This section describes the core data structures used to represent the game.

<a name="21-player-enum"></a>
### 2.1. `Player` Enum

```python
class Player(StrEnum):
    p1 = auto()
    p2 = auto()
```

This enum defines the two players in the game: `p1` and `p2`.

<a name="22-gamestatus-enum"></a>
### 2.2. `GameStatus` Enum

```python
class GameStatus(StrEnum):
    ongoing = auto()
    has_winner = auto()
    draw = auto()
```

This enum represents the possible states of the game: `ongoing`, `has_winner`, and `draw`.

<a name="23-location-data-class"></a>
### 2.3. `Location` Data Class

```python
@dataclass(frozen = True)
class Location:
    row: int
    col: int
```

Represents the location of a piece on the board using row and column indices.

<a name="24-pieceinfo-protocol"></a>
### 2.4. `PieceInfo` Protocol

```python
class PieceInfo(Protocol):
    def get_piece_info(self) -> list[tuple[Location, PieceType, list[Trait], list[tuple[int, int]], Player]]:
        ...
```

A protocol defining the interface for classes providing initial piece information for board setup.


<a name="25-board-protocol"></a>
### 2.5. `Board` Protocol

```python
class Board(Protocol):
    def __init__(self, row: int, col: int):
        ...

    def setup(self, piece_info: PieceInfo):
        ...

    @property
    def get_row(self) -> int:
        ...

    @property
    def get_col(self) -> int:
        ...

    @property
    def get_board(self) -> list[list[Piece | None]]:
        ...
```

A protocol defining the interface for board representation.  It specifies methods for initialization, setup, and accessing board dimensions and the board itself.

<a name="26-gamestate-data-class"></a>
### 2.6. `GameState` Data Class

```python
@dataclass(frozen = True)
class GameState:
    game_status: GameStatus
    board_status: list[list[Piece | None]]
    turn: Player
    moves_left: int
    selected_piece: Piece | None
    P1_captured: list[Piece]
    P2_captured: list[Piece]

    class New(TypedDict, total=False):
        game_status: GameStatus
        board_status: list[list[Piece | None]]
        turn: Player
        moves_left: int
        selected_piece: Piece | None
        P1_captured: list[Piece]
        P2_captured: list[Piece]

    def change_to(self, new: New) -> Self:
        ret = replace(self, **new)
        return ret
```

This dataclass holds the complete state of the game including the game status, board, current player's turn, remaining moves, selected piece, and captured pieces for each player.  The `change_to` method allows for immutably updating the game state.


<a name="27-piecetype-enum"></a>
### 2.7. `PieceType` Enum

```python
class PieceType(StrEnum):
    chick = auto()
    elephant = auto()
    giraffe = auto()
    monkey = auto()
    lion = auto()
```

This enum defines the different types of pieces in the Chogi game.

<a name="28-trait-enum"></a>
### 2.8. `Trait` Enum

```python
class Trait(StrEnum):
    protected = auto()
    can_undo = auto()
```

This enum defines special traits a piece can have.

<a name="29-moves-protocol"></a>
### 2.9. `Moves` Protocol

```python
class Moves(Protocol):
    forward = [(0, +1)]
    diagonal = [(dr, dc) for dr in {-1, +1} for dc in {-1, +1}]
    orthogonal = [(dr, dc) for dr in {-1, 0, +1} for dc in {-1, 0, +1} if 0 in {dr, dc} and (dr, dc) != (0, 0)]

    def get_moves(self, player: Player) -> list[tuple[int, int]]:
        ...
```

This protocol defines the interface for classes determining piece movement.  It includes default move sets for forward, diagonal, and orthogonal movements.


<a name="210-piece-class"></a>
### 2.10. `Piece` Class

```python
class Piece:
    def __init__(self, location: Location | None, piece_type: PieceType, traits: list[Trait], moves: list[tuple[int, int]], player: Player):
        self._location = location
        self._piece_type = piece_type
        self._traits = traits
        self._moves = moves
        self._player = player

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Piece):
            return NotImplemented
        return (self._location, self._piece_type, self._traits, self._moves, self._player) == (other._location, other._piece_type, other._traits, other._moves, other._player)

    @property
    def get_location(self) -> Location | None:
        return self._location

    @get_location.setter
    def get_location(self, location: Location | None):
        self._location = location

    @property
    def get_piece_type(self) -> PieceType:
        return self._piece_type

    @property
    def get_traits(self) -> list[Trait]:
        return self._traits

    @property
    def get_moves(self) -> list[tuple[int, int]]:
        return self._moves

    @get_moves.setter
    def get_moves(self, moves: list[tuple[int, int]]):
        self._moves = moves

    @property
    def get_player(self) -> Player:
        return self._player

    @get_player.setter
    def get_player(self, player: Player):
        self._player = player
```

This class represents a single game piece, storing its location, type, traits, possible moves, and the player it belongs to.  It uses properties to provide controlled access to its attributes.  The `__eq__` method enables comparison of pieces.


<a name="3-game-logic-classes"></a>
## 3. Game Logic Classes

This section details the classes responsible for the game's logic.

<a name="31-moves-implementations"></a>
### 3.1. `Moves` Implementations

These classes implement the `Moves` protocol, defining movement rules for each piece type.  They account for differences in player direction.

<a name="311-chickmoves-class"></a>
#### 3.1.1. `ChickMoves` Class

```python
class ChickMoves(Moves):
    def get_moves(self, player: Player) -> list[tuple[int, int]]:
        if player is Player.p2:
            return [(x*-1, y*-1) for x, y in self.forward]
        return self.forward
```

Chick pieces can only move forward.  Player 2's chicks move in the opposite direction.

<a name="312-elephantmoves-class"></a>
#### 3.1.2. `ElephantMoves` Class

```python
class ElephantMoves(Moves):
    def get_moves(self, player: Player) -> list[tuple[int, int]]:
        if player is Player.p2:
            return [(x*-1, y*-1) for x, y in self.diagonal]
        return self.diagonal
```

Elephant pieces can move diagonally. Player 2's elephants move in the opposite diagonal direction.

<a name="313-giraffemoves-class"></a>
#### 3.1.3. `GiraffeMoves` Class

```python
class GiraffeMoves(Moves):
    def get_moves(self, player: Player) -> list[tuple[int, int]]:
        if player is Player.p2:
            return [(x*-1, y*-1) for x, y in self.orthogonal]
        return self.orthogonal
```

Giraffe pieces can move orthogonally. Player 2's giraffes move in the opposite orthogonal direction.


<a name="314-monkeymoves-class"></a>
#### 3.1.4. `MonkeyMoves` Class

```python
class MonkeyMoves(Moves):
    def get_moves(self, player: Player) -> list[tuple[int, int]]:
        if player is Player.p2:
            return [(x*-1, y*-1) for x, y in [*self.diagonal, *self.orthogonal]]
        return [*self.diagonal, *self.orthogonal]
```

Monkey pieces can move diagonally or orthogonally. Player 2's monkeys move in the opposite diagonal or orthogonal direction.


<a name="315-lionmoves-class"></a>
#### 3.1.5. `LionMoves` Class

```python
class LionMoves(Moves):
    def get_moves(self, player: Player) -> list[tuple[int, int]]:
        if player is Player.p2:
            return [(x*-1, y*-1) for x, y in [*self.diagonal, *self.orthogonal]]
        return [*self.diagonal, *self.orthogonal]
```

Lion pieces can move diagonally or orthogonally. Player 2's lions move in the opposite diagonal or orthogonal direction.


<a name="32-chogipieceinfo-class"></a>
### 3.2. `ChogiPieceInfo` Class

```python
class ChogiPieceInfo(PieceInfo):
    def get_piece_info(self) -> list[tuple[Location, PieceType, list[Trait], list[tuple[int, int]], Player]]:
        piece_info: list[tuple[Location, PieceType, list[Trait], list[tuple[int, int]], Player]] = []
        for player in Player:
            # ... (Piece placement logic for each player) ...
        return piece_info
```

This class implements the `PieceInfo` protocol, providing the initial piece placement for the Chogi board.  The `get_piece_info` method generates a list of tuples, each defining a piece's location, type, traits, moves, and player. The code iterates through each player and defines the initial positions and characteristics for each piece type on the board.


<a name="33-chogiborad-class"></a>
### 3.3. `ChogiBoard` Class

```python
class ChogiBoard(Board):
    def __init__(self, row: int, col: int):
        self._row = row
        self._col = col

    def setup(self, piece_info: PieceInfo):
        self._board: list[list[Piece | None]] = [[None for _ in range(self._col)] for _ in range(self._row)]
        for location, piece_type, traits, moves, player in piece_info.get_piece_info():
            self._board[location.row][location.col] = Piece(
                location,
                piece_type,
                traits,
                moves,
                player
            )

    @property
    def get_row(self) -> int:
        return self._row

    @property
    def get_col(self) -> int:
        return self._col

    @property
    def get_board(self) -> list[list[Piece | None]]:
        return self._board
```

This class implements the `Board` protocol, representing the Chogi game board. The `setup` method uses the provided `PieceInfo` to populate the board with pieces.  The `get_row`, `get_col`, and `get_board` properties provide access to the board's dimensions and its internal representation.
