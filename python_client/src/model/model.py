from dataclasses import replace
from .project_types import (
    Board, PieceInfo, Piece, GameStatus, GameState, 
    Location, Player, Trait
)

class Model:
    def __init__(self, board: Board, piece_info: PieceInfo):
        self._max_moves = 3
        self._board = board
        self._piece_info = piece_info
        self.new_game()

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

    def _is_draw(self) -> bool:
        return (self._is_checkmate(Player.p1) and self._is_checkmate(Player.p2))

    def _is_checkmate(self, player: Player) -> bool:
        protected_pieces: list[Piece] = []
        counter_pieces: list[Piece] = []

        for row in self._state.board_status:
            for piece in row:
                if piece is not None:
                    if piece.get_player is not player:
                        if Trait.protected in piece.get_traits:
                            protected_pieces.append(piece)
                        else:
                            counter_pieces.append(piece)

        paths: list[Location] = []
        infiltrators: list[Piece] = []

        for piece in protected_pieces:
            for delta_x, delta_y in piece.get_moves:
                if piece.get_location is not None:
                    new_row = piece.get_location.row - delta_y
                    new_col = piece.get_location.col - delta_x
                    if new_row in range(self._board.get_row) and new_col in range(self._board.get_col):
                        target_piece = self._state.board_status[new_row][new_col]
                        if target_piece is None:
                            paths.append(Location(row = new_row, col = new_col))
                        else:
                            if target_piece.get_player is player:
                                infiltrators.append(target_piece)
        
        counter_locations: list[Location] = []
        for piece in counter_pieces:
            for delta_x, delta_y in piece.get_moves:
                if piece.get_location is not None:
                    new_row = piece.get_location.row - delta_y
                    new_col = piece.get_location.col - delta_x
                    if new_row in range(self._board.get_row) and new_col in range(self._board.get_col):
                        target_piece = self._state.board_status[new_row][new_col]
                        if target_piece is not None:
                            if target_piece.get_player is player and target_piece.get_location is not None:
                                counter_locations.append(target_piece.get_location)

        if not paths:
            for piece in infiltrators:
                if piece.get_player is player and piece.get_location in counter_locations:
                    if len(infiltrators) > 1:
                        return True
                    return False
                
        return False

    def _copy_state(self) -> GameState:
        game_status = self._state.game_status
        board_status: list[list[Piece | None]] = [[
            Piece(
                piece.get_location,
                piece.get_piece_type,
                piece.get_traits,
                piece.get_moves,
                piece.get_player  
            ) if piece is not None else None for piece in row] for row in self._state.board_status]
        turn = self._state.turn
        moves_left = self._state.moves_left
        
        selected_piece = None

        if self._state.selected_piece is not None:
            location = self._state.selected_piece.get_location
            piece_type = self._state.selected_piece.get_piece_type
            traits = self._state.selected_piece.get_traits
            moves = self._state.selected_piece.get_moves
            player = self._state.selected_piece.get_player

            selected_piece = Piece(location, piece_type, traits, moves, player)

        P1_captured: list[Piece] = [
            Piece(
                piece.get_location,
                piece.get_piece_type,
                piece.get_traits,
                piece.get_moves,
                piece.get_player  
            ) for piece in self._state.P1_captured]

        P2_captured: list[Piece] = [
            Piece(
                piece.get_location,
                piece.get_piece_type,
                piece.get_traits,
                piece.get_moves,
                piece.get_player
            ) for piece in self._state.P2_captured]

        return GameState(
                game_status = game_status,
                board_status = board_status,
                turn = turn,
                selected_piece = selected_piece,
                moves_left = moves_left,
                P1_captured = P1_captured,
                P2_captured = P2_captured
            )

    def piece_select(self, piece: Piece, player: Player):
        if piece.get_player is self._state.turn and player is self._state.turn:
            self._state = self.state.change_to({
                'selected_piece': piece
            })

            self._prev_state = self._copy_state()

    def _is_move_valid(self, target_location: Location) -> bool:
        if self._state.selected_piece is not None:
            if self._state.board_status[target_location.row][target_location.col] is not None:
                target_piece = self._state.board_status[target_location.row][target_location.col]
                if target_piece is not None:
                    if self._state.selected_piece.get_player is target_piece.get_player or Trait.protected in self._state.selected_piece.get_traits:
                        return False
                    if Trait.protected in target_piece.get_traits:
                        return False
            
            for delta_x, delta_y in self._state.selected_piece.get_moves:
                if self._state.selected_piece.get_location is not None:
                    new_row = self._state.selected_piece.get_location.row - delta_y
                    new_col = self._state.selected_piece.get_location.col + delta_x
                    if new_row == target_location.row and new_col == target_location.col:
                        return True            
        
        return False

    def move(self, target_location: Location, player: Player):
        if player is self._state.turn and self._state.selected_piece is not None:
            if self._is_move_valid(target_location):
                new_board_status: list[list[Piece | None]] = self._state.board_status
                target_piece: Piece | None = new_board_status[target_location.row][target_location.col]
                if target_piece is not None:
                    target_piece.get_player = self._state.selected_piece.get_player
                    target_piece.get_moves = [(x*-1, y*-1) for x, y in target_piece.get_moves]
                    target_piece.get_location = None

                    if self._state.selected_piece.get_player is Player.p1:
                        self._state.P1_captured.append(target_piece)
                    else:
                        self._state.P2_captured.append(target_piece)

                new_board_status[target_location.row][target_location.col] = self._state.selected_piece

                current_location: Location | None = self._state.selected_piece.get_location
                if current_location is not None:
                    new_board_status[current_location.row][current_location.col] = None

                selected_piece: Piece | None = new_board_status[target_location.row][target_location.col]
                if selected_piece is not None:
                    selected_piece.get_location = target_location

                new_player = Player.p1 if self._state.turn is not Player.p1 else Player.p2

                if self._is_draw():
                    self._state = self.state.change_to({
                        'game_status': GameStatus.draw,
                        'board_status': new_board_status, 
                        'selected_piece': None
                    })
                elif self._is_checkmate(self._state.turn):
                    self._state = self.state.change_to({
                        'game_status': GameStatus.has_winner,
                        'board_status': new_board_status, 
                        'selected_piece': None
                    })
                else:
                    self._state = self.state.change_to({
                        'board_status': new_board_status, 
                        'turn': new_player if self._state.moves_left - 1 == 0 else self._state.turn,
                        'moves_left': self._state.moves_left - 1 if self._state.moves_left - 1 != 0 else self._max_moves,
                        'selected_piece': None
                    })

                if self._recent_state:
                    self._recent_state = []
                if self._prev_state is not None:
                    self._recent_state.append(self._prev_state)

            self._state = self.state.change_to({
                'selected_piece': None
            })

    def _is_drop_valid(self, target_location: Location):
        protected_pieces: list[Piece] = []
        paths: list[Location] = []

        for row in self._state.board_status:
            for piece in row:
                if piece is not None:
                    if Trait.protected in piece.get_traits:
                        if piece.get_player is not self._state.turn:
                            protected_pieces.append(piece)
        
        for piece in protected_pieces:
            for delta_x, delta_y in piece.get_moves:
                if piece.get_location is not None:
                    new_row = piece.get_location.row - delta_y
                    new_col = piece.get_location.col - delta_x
                    if new_row in range(self._board.get_row) and new_col in range(self._board.get_col):
                        target_piece = self._state.board_status[new_row][new_col]
                        if target_piece is None:
                            paths.append(Location(row = new_row, col = new_col))

        if target_location in paths:
            return False

        return True

    def drop(self, target_location: Location, player: Player):
        if player is self._state.turn:
            new_board_status = self._state.board_status
            if new_board_status[target_location.row][target_location.col] is None:
                if self._is_drop_valid(target_location):
                    if self._state.selected_piece is not None:
                        if self._state.selected_piece.get_player is Player.p1:
                            for captured in self._state.P1_captured:
                                if self._state.selected_piece == captured:
                                    self._state.P1_captured.remove(captured)
                        else:
                            for captured in self._state.P2_captured:
                                if self._state.selected_piece == captured:
                                    self._state.P2_captured.remove(captured)

                    new_board_status[target_location.row][target_location.col] = self._state.selected_piece
                    dropped: None | Piece = new_board_status[target_location.row][target_location.col]

                    if dropped is not None:
                        dropped.get_location = target_location

                    new_player = Player.p1 if self._state.turn is not Player.p1 else Player.p2

                    self._state = self.state.change_to({
                        'board_status': new_board_status,
                        'turn': new_player if self._state.moves_left - 1 == 0 else self._state.turn,
                        'moves_left': self._state.moves_left - 1 if self._state.moves_left - 1 != 0 else self._max_moves,
                        'selected_piece': None
                    })

                    if self._recent_state:
                        self._recent_state = []
                    if self._prev_state is not None:
                        self._recent_state.append(self._prev_state)

        self._state = self.state.change_to({
            'selected_piece': None
        })

    def undo(self, player: Player):
        if self._recent_state[-1].selected_piece is not None:
            if self._recent_state[-1].selected_piece.get_location is not None and player is self._recent_state[-1].turn:
                if Trait.can_undo in self._recent_state[-1].selected_piece.get_traits:
                    self._state = self._recent_state[-1]
                    self._state = self.state.change_to({
                        'selected_piece': None
                    })
                    self._recent_state[:-1]

    @property
    def state(self) -> GameState:
        return replace(self._state)