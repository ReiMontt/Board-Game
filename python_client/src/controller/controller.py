from model import Model
from view import View
from model import (GameState, Location, Player, Piece)
from view import (GameStateChangeObserver, View)

class Controller:
    def __init__(self, model: Model, view: View):
        self._model = model
        self._view = view

        self._game_state_change_observers: list[GameStateChangeObserver] = []

    def start(self):
        view = self._view
        
        self.register_game_state_change_observer(view)
        view.register_new_game_observer(self)
        view.register_piece_select_observer(self)
        view.register_move_observer(self)
        view.register_drop_observer(self)
        view.register_undo_observer(self)

        view.run()

    def on_new_game(self):
        self._model.new_game()
        self._on_state_change(self._model.state)
    
    def on_piece_select(self, piece: Piece, player: Player):
        self._model.piece_select(piece, player)
        self._on_state_change(self._model.state)

    def on_move(self, location: Location, player: Player):
        self._model.move(location, player)
        self._on_state_change(self._model.state)

    def on_drop(self, location: Location, player: Player):
        self._model.drop(location, player)
        self._on_state_change(self._model.state)

    def on_undo(self, player: Player):
        self._model.undo(player)
        self._on_state_change(self._model.state)
    
    def register_game_state_change_observer(self, observer: GameStateChangeObserver):
        self._game_state_change_observers.append(observer)
    
    def _on_state_change(self, state: GameState):
        for observer in self._game_state_change_observers:
            observer.on_state_change(state)