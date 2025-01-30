from __future__ import annotations
from typing import Protocol
from model import GameState, Location, Player, Piece


class NewGameObserver(Protocol):
    def on_new_game(self):
        ...

class PieceSelectObserver(Protocol):
    def on_piece_select(self, piece: Piece, player: Player):
        ...

class MoveObserver(Protocol):
    def on_move(self, location: Location, player: Player):
        ...

class DropObserver(Protocol):
    def on_drop(self, location: Location, player: Player):
        ...

class UndoObserver(Protocol):
    def on_undo(self, player: Player):
        ...

class GameStateChangeObserver(Protocol):
    def on_state_change(self, state: GameState):
        ...

class View(Protocol):
    def run(self):
        ...

    def on_state_change(self, state: GameState):
        ...

    def register_new_game_observer(self, observer: NewGameObserver):
        ...
    
    def register_piece_select_observer(self, observer: PieceSelectObserver):
        ...

    def register_move_observer(self, observer: MoveObserver):
        ...

    def register_drop_observer(self, observer: DropObserver):
        ...
    
    def register_undo_observer(self, observer: UndoObserver):
        ...
