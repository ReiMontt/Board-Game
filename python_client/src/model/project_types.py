from __future__ import annotations
from enum import StrEnum, auto
from dataclasses import dataclass, replace
from typing import Self, Protocol, TypedDict

class Player(StrEnum):
    p1 = auto()
    p2 = auto()

class GameStatus(StrEnum):
    ongoing = auto()
    has_winner = auto()
    draw = auto()

@dataclass(frozen = True)
class Location:
    row: int
    col: int

class PieceInfo(Protocol):
    def get_piece_info(self) -> list[tuple[Location, PieceType, list[Trait], list[tuple[int, int]], Player]]:
        ...

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

##################################################### Chogi Types ############################################################################

class PieceType(StrEnum):
    chick = auto()
    elephant = auto()
    giraffe = auto()
    monkey = auto()
    lion = auto()

class Trait(StrEnum):
    protected = auto()
    can_undo = auto()

class Moves(Protocol):
    forward = [(0, +1)]
    diagonal = [(dr, dc) for dr in {-1, +1} for dc in {-1, +1}]
    orthogonal = [(dr, dc) for dr in {-1, 0, +1} for dc in {-1, 0, +1} if 0 in {dr, dc} and (dr, dc) != (0, 0)]

    def get_moves(self, player: Player) -> list[tuple[int, int]]:
        ...

class ChickMoves(Moves):
    def get_moves(self, player: Player) -> list[tuple[int, int]]:
        if player is Player.p2:
            return [(x*-1, y*-1) for x, y in self.forward]
        return self.forward

class ElephantMoves(Moves):
    def get_moves(self, player: Player) -> list[tuple[int, int]]:
        if player is Player.p2:
            return [(x*-1, y*-1) for x, y in self.diagonal]
        return self.diagonal

class GiraffeMoves(Moves):
    def get_moves(self, player: Player) -> list[tuple[int, int]]:
        if player is Player.p2:
            return [(x*-1, y*-1) for x, y in self.orthogonal]
        return self.orthogonal

class MonkeyMoves(Moves):
    def get_moves(self, player: Player) -> list[tuple[int, int]]:
        if player is Player.p2:
            return [(x*-1, y*-1) for x, y in [*self.diagonal, *self.orthogonal]]
        return [*self.diagonal, *self.orthogonal]

class LionMoves(Moves):
    def get_moves(self, player: Player) -> list[tuple[int, int]]:
        if player is Player.p2:
            return [(x*-1, y*-1) for x, y in [*self.diagonal, *self.orthogonal]]
        return [*self.diagonal, *self.orthogonal]
    
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

class ChogiPieceInfo(PieceInfo):
    def get_piece_info(self) -> list[tuple[Location, PieceType, list[Trait], list[tuple[int, int]], Player]]:
        piece_info: list[tuple[Location, PieceType, list[Trait], list[tuple[int, int]], Player]] = []
        for player in Player:
            if player is Player.p1:
                piece_info += [(Location(6, i), PieceType.chick, [Trait.can_undo], ChickMoves().get_moves(player), player) for i in range(8)] + [
                        (Location(7, 1), PieceType.elephant, [], ElephantMoves().get_moves(player), player), 
                        (Location(7, 6), PieceType.elephant, [], ElephantMoves().get_moves(player), player)
                    ] + [
                        (Location(7, 0), PieceType.giraffe, [], GiraffeMoves().get_moves(player), player), 
                        (Location(7, 7), PieceType.giraffe, [], GiraffeMoves().get_moves(player), player)
                    ] + [
                        (Location(7, 2), PieceType.monkey, [], MonkeyMoves().get_moves(player), player), 
                        (Location(7, 5), PieceType.monkey, [], MonkeyMoves().get_moves(player), player)
                    ] + [
                        (Location(7, 3), PieceType.lion, [Trait.protected], LionMoves().get_moves(player), player), 
                        (Location(7, 4), PieceType.lion, [Trait.protected], LionMoves().get_moves(player), player)                        
                    ]
            else:
                piece_info += [(Location(1, i), PieceType.chick, [Trait.can_undo], ChickMoves().get_moves(player), player) for i in range(8)] + [
                        (Location(0, 1), PieceType.elephant, [], ElephantMoves().get_moves(player), player), 
                        (Location(0, 6), PieceType.elephant, [], ElephantMoves().get_moves(player), player)
                    ] + [
                        (Location(0, 0), PieceType.giraffe, [], GiraffeMoves().get_moves(player), player), 
                        (Location(0, 7), PieceType.giraffe, [], GiraffeMoves().get_moves(player), player)
                    ] + [
                        (Location(0, 2), PieceType.monkey, [], MonkeyMoves().get_moves(player), player), 
                        (Location(0, 5), PieceType.monkey, [], MonkeyMoves().get_moves(player), player)
                    ] + [
                        (Location(0, 3), PieceType.lion, [Trait.protected], LionMoves().get_moves(player), player), 
                        (Location(0, 4), PieceType.lion, [Trait.protected], LionMoves().get_moves(player), player)
                    ]
        
        return piece_info

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