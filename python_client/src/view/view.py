import pygame, sys

from model import (
    GameState, GameStatus, Player, Location, Piece, PieceType, Trait
)
from .observers import (
    NewGameObserver, PieceSelectObserver, MoveObserver, DropObserver, UndoObserver, View
)

from cs150241project_networking import CS150241ProjectNetworking

class TextView:
    def __init__(self, x: int, y: int, game_status: GameStatus, turn: Player, moves_left: int, player_id: int):
        self._x = x
        self._y = y
        self._game_status = game_status
        self._turn = turn
        self._moves_left = moves_left
        self._player_id = player_id

    def render(self, screen: pygame.Surface):
        font = pygame.font.SysFont('arialrounded', 28)
        font_color = '#F1E7D8'

        subtext_font1 = pygame.font.SysFont('arialrounded', 18)
        subtext_font2 = pygame.font.SysFont('arialrounded', 12)

        match self._game_status:
            case GameStatus.ongoing:
                text = 'Your Turn' if Player[f'p{self._player_id}'] is self._turn else 'Opponent\'s Turn'
                text_obj = font.render(text, True, font_color)
                text_rect = text_obj.get_rect()
                text_rect.center = (self._x, self._y)
                screen.blit(text_obj, text_rect)

                if Player[f'p{self._player_id}'] is self._turn:
                    subtext_obj = subtext_font1.render(f'Moves left: {self._moves_left}', True, font_color)
                    subtext_rect = subtext_obj.get_rect()
                    subtext_rect.center = (self._x, self._y + 30)
                    screen.blit(subtext_obj, subtext_rect)

                player_text_obj = subtext_font1.render(f'You are Player {self._player_id}', True, font_color)
                player_text_rect = player_text_obj.get_rect()
                player_text_rect.center = (self._x, 11 * self._y)
                screen.blit(player_text_obj, player_text_rect)

                inst_text_obj = subtext_font2.render('Press \'U\' to undo move once (chick piece only)', True, font_color)
                inst_text_rect = inst_text_obj.get_rect()
                inst_text_rect.center = (self._x, 11 * self._y + 30)
                screen.blit(inst_text_obj, inst_text_rect)

            case GameStatus.has_winner:
                text = 'You win!' if Player[f'p{self._player_id}'] is self._turn else 'You lose'
                text_obj = font.render(text, True, font_color)
                text_rect = text_obj.get_rect()
                text_rect.center = (self._x, self._y)
                screen.blit(text_obj, text_rect)

                inst_text_obj = subtext_font1.render('Press \'R\' to play again', True, font_color)
                inst_text_rect = inst_text_obj.get_rect()
                inst_text_rect.center = (self._x, 11 * self._y)
                screen.blit(inst_text_obj, inst_text_rect)

            case GameStatus.draw:
                text = 'Draw'
                text_obj = font.render(text, True, font_color)
                text_rect = text_obj.get_rect()
                text_rect.center = (self._x, self._y)
                screen.blit(text_obj, text_rect)

                inst_text_obj = subtext_font1.render('Press \'R\' to play again', True, font_color)
                inst_text_rect = inst_text_obj.get_rect()
                inst_text_rect.center = (self._x, 11 * self._y)
                screen.blit(inst_text_obj, inst_text_rect)

class PieceView:
    def __init__(self, x: int, y: int, width: int, piece: Piece):        
        self._x = x
        self._y = y
        self._width = width

        self._piece = piece
        self.piece_info()
    
    def piece_info(self):
        self._location = self._piece.get_location
        self._piece_type = self._piece.get_piece_type
        self._traits = self._piece.get_traits
        self._moves = self._piece.get_moves
        self._player = self._piece.get_player

    def render(self, screen: pygame.Surface):
        piece_icon = None

        match self._piece_type:
            case PieceType.chick:
                piece_icon = pygame.image.load(r'src\sprites\chick.png')
            case PieceType.elephant:
                piece_icon = pygame.image.load(r'src\sprites\elephant.png')
            case PieceType.giraffe:
                piece_icon = pygame.image.load(r'src\sprites\giraffe.png')
            case PieceType.monkey:
                piece_icon = pygame.image.load(r'src\sprites\monkey.png')
            case PieceType.lion:
                piece_icon = pygame.image.load(r'src\sprites\lion.png')

        piece_icon = pygame.transform.scale(piece_icon, (self._width, self._width))
        
        if self._player is Player.p2:
            piece_icon = pygame.transform.rotate(piece_icon, 180)

        screen.blit(piece_icon, (self._x, self._y))
    
    def is_on_piece(self, mx: int, my: int) -> bool:
        return (mx in range (self._x, self._x + self._width) and my in range (self._y, self._y + self._width))
    
    @property
    def get_piece(self):
        return self._piece

class BoardView:
    def __init__(self, row: int, col: int):
        self._row = row
        self._col = col

    def _render_tile(self, x: int, y: int, highlight: str):
        tile = None

        match highlight:
            case 'select':
                tile = pygame.image.load(r'src\sprites\select_tile.png')
            case 'move':
                tile = pygame.image.load(r'src\sprites\move_tile.png')
            case 'capture':
                tile = pygame.image.load(r'src\sprites\capture_tile.png')            
            case _:
                tile = pygame.image.load(r'src\sprites\tile.png')
        
        tile = pygame.transform.scale(tile, (self._tile_width, self._tile_width))
        self._screen.blit(tile, (x, y))

    def get_tile_coords(self) -> list[tuple[int, int]]:
        coords: list[tuple[int, int]] = []

        for i in range(self._row):
            for j in range(self._col):
                coords.append((self._x + j * self._tile_width, self._y + i * self._tile_width))

        return coords

    def mouse_on_tile(self, x: int, y: int, mx: int, my: int) -> bool:
        return (mx in range (x, x + self._tile_width) and my in range(y, y + self._tile_width))

    def mouse_on_board(self, mx: int, my: int) -> bool:
        for xi, yi in self.get_tile_coords():
            if self.mouse_on_tile(xi, yi, mx, my):
                return True
        
        return False

    def render_board(self, screen: pygame.Surface, x: int, y: int, tile_width: int):
        self._screen = screen
        self._x = x
        self._y = y
        self._tile_width = tile_width

        for xi, yi in self.get_tile_coords():
            self._render_tile(xi, yi, '')

        board_width = 10
        pygame.draw.rect(screen, '#AA8E5E', (
            x - board_width, 
            y - board_width, 
            2 * board_width + self._col * tile_width, 
            2 * board_width + self._row * tile_width
        ), 10)

    def get_action_location(self, mx: int, my: int) -> Location | None:
        for i in range(self._row):
            for j in range(self._col):
                x = self._x + j * self._tile_width
                y = self._y + i * self._tile_width
                if self.mouse_on_tile(x, y, mx, my):
                    return Location(row = i, col = j)

    def render_select_tile(self, mx: int, my: int, player: Player, board_status: list[list[Piece | None]]):
        for i in range(self._row):
            for j in range(self._col):
                x = self._x + j * self._tile_width
                y = self._y + i * self._tile_width
                if self.mouse_on_tile(x, y, mx, my):
                    piece: None | Piece = board_status[i][j]
                    if piece is not None:
                        if piece.get_player is player:
                            self._render_tile(x, y, 'select')
    
    def get_piece_destinations(self, piece: Piece, board_status: list[list[Piece | None]]) -> list[Location]:
        possible_destinations: list[Location] = []

        for delta_x, delta_y in piece.get_moves:
            if piece.get_location is not None:
                new_row = piece.get_location.row - delta_y
                new_col = piece.get_location.col + delta_x
                if new_row in range(self._row) and new_col in range(self._col):
                    target_piece: Piece | None = board_status[new_row][new_col]
                    if Trait.protected in piece.get_traits:
                        if target_piece is None:
                            possible_destinations.append(Location(row = new_row, col = new_col))
                    else:
                        if target_piece is None:
                            possible_destinations.append(Location(row = new_row, col = new_col))
                        else:
                            if piece.get_player is not target_piece.get_player:
                                possible_destinations.append(Location(row = new_row, col = new_col))
        
        return possible_destinations

    def render_destination_tiles(self, piece: Piece, board_status: list[list[Piece | None]]):
        possible_destinations = self.get_piece_destinations(piece, board_status)
            
        for destination in possible_destinations:
            x = self._x + destination.col * self._tile_width
            y = self._y + destination.row * self._tile_width
            if board_status[destination.row][destination.col] is None:
                self._render_tile(x, y, 'move')
            else:
                self._render_tile(x, y, 'capture')
    
    def get_drop_locations(self, piece: Piece, board_status: list[list[Piece | None]]) -> list[Location]:
        protected_paths: list[Location] = []
        for row in board_status:
            for p in row:
                if p is not None and p.get_traits:
                    if Trait.protected in p.get_traits and piece.get_player is not p.get_player:
                        protected_paths += self.get_piece_destinations(p, board_status)
        
        drop_locations: list[Location] = []
        for i in range(self._row):
            for j in range(self._col):
                if board_status[i][j] is None and Location(row = i, col = j) not in protected_paths:
                    drop_locations.append(Location(row = i, col = j))

        return drop_locations

    def render_drop_tiles(self, piece: Piece, board_status: list[list[Piece | None]]):
        for i in range(self._row):
            for j in range(self._col):
                if Location(row = i, col = j) in self.get_drop_locations(piece, board_status):
                    x = self._x + j * self._tile_width
                    y = self._y + i * self._tile_width
                    self._render_tile(x, y, 'move')
    
    @property
    def get_row(self):
        return self._row
    
    @property
    def get_col(self):
        return self._col

    @property
    def get_x(self):
        return self._x

    @property
    def get_y(self):
        return self._y

    @property
    def get_tile_width(self):
        return self._tile_width

class PygameView(View):
    def __init__(self, state: GameState):
        self.init_network()
        self.on_state_change(state)

        self._width: int = 720
        self._height: int = 720
        
        self._board: BoardView = BoardView(8, 8)
        self._pieces: list[PieceView] = []
        self._new_game_observers: list[NewGameObserver] = []
        self._piece_select_observers: list[PieceSelectObserver] = []
        self._move_observers: list[MoveObserver] = []
        self._drop_observers: list[DropObserver] = []
        self._undo_observers: list[UndoObserver] = []

    def on_state_change(self, state: GameState):
        self._state = state
        self._game_status: GameStatus = state.game_status
        self._board_status: list[list[Piece | None]] = state.board_status
        self._turn: Player = state.turn
        self._moves_left = state.moves_left
        self._selected_piece: Piece | None = state.selected_piece
        self._P1_captured: list[Piece] = state.P1_captured
        self._P2_captured: list[Piece] = state.P2_captured

    def init_network(self):
        self._network = CS150241ProjectNetworking.connect('localhost', 15000)
        self._latest_message = None
        self._player_id = self._network.player_id

    def run(self):
        pygame.init()

        width: int = self._width
        height: int = self._height
        
        tile_width: int = width // (2 * self._board.get_col)
        board_width: int = self._board.get_col * tile_width
        board_height: int = self._board.get_row * tile_width

        board_x: int = (width - board_width) // 2
        board_y: int = (height - board_height) // 2

        piece_width: int = tile_width - tile_width // 6 

        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(f'Chogi v150: Player {self._player_id}')

        self._screen = screen

        clock = pygame.time.Clock()

        sel_mx, sel_my = -1, -1

        while True:
            screen.fill("#99BE8F")

            TextView(width // 2, height // 12, self._game_status, self._turn, self._moves_left, self._player_id).render(self._screen)

            mx, my = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self._game_status is GameStatus.ongoing:
                            if self._board.mouse_on_board(mx, my):
                                if self._selected_piece is not None:
                                    destination = self._board.get_action_location(mx, my)
                                    destination_str = str((destination.row, destination.col)) if destination is not None else 'None'
                                    if self._selected_piece.get_location is not None:
                                        move_message = 'move#' + destination_str + f'#p{self._player_id}'
                                        self._network.send(move_message)
                                    else:
                                        drop_message = 'drop#' + destination_str + f'#p{self._player_id}'
                                        self._network.send(drop_message)
                                else:
                                    sel_mx, sel_my = mx, my
                                    selected_piece = self._select_piece(sel_mx, sel_my)
                                    if selected_piece is not None:
                                        select_message = 'select#'
                                        piece_str = str((
                                            str((selected_piece.get_location.row, selected_piece.get_location.col)) if selected_piece.get_location is not None else 'None',
                                            str(selected_piece.get_piece_type),
                                            str([str(trait) for trait in selected_piece.get_traits]),
                                            str(selected_piece.get_moves),
                                            str(selected_piece.get_player)
                                        ))
                                        select_message += (piece_str + f'#p{self._player_id}')
                                        self._network.send(select_message)
                                    else:
                                        self._network.send(f'select#None#p{self._player_id}')
                            else:
                                sel_mx, sel_my = mx, my
                                selected_piece = self._select_piece(sel_mx, sel_my)
                                if selected_piece is not None:
                                    select_message = 'select#'
                                    piece_str = str((
                                        'None',
                                        str(selected_piece.get_piece_type),
                                        str([str(trait) for trait in selected_piece.get_traits]),
                                        str(selected_piece.get_moves),
                                        str(selected_piece.get_player)
                                    ))         
                                    select_message += (piece_str + f'#p{self._player_id}')
                                    self._network.send(select_message)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        if self._game_status is not GameStatus.ongoing:
                            self._new_game()
                            new_game_message = f'new_game#None#p{self._player_id}'
                            self._network.send(new_game_message)
                    elif event.key == pygame.K_u:
                        if self._game_status is GameStatus.ongoing:
                            undo_message = f'undo#None#p{self._player_id}'
                            self._network.send(undo_message)

            self._board.render_board(screen, board_x, board_y, tile_width)

            self._receiver()

            if self._game_status is GameStatus.ongoing and Player[f'p{self._player_id}'] is self._turn:
                self._render_highlights(mx, my, sel_mx, sel_my)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            self._pieces = []

            self._set_active_pieces(board_x, board_y, piece_width)
            self._set_captured_pieces(
                (width - len(self._P1_captured) * tile_width) // 2, board_y + board_height + tile_width // 3, piece_width, self._P1_captured
            )
            self._set_captured_pieces(
                (width - len(self._P2_captured) * tile_width) // 2, board_y - piece_width - tile_width // 3, piece_width, self._P2_captured
            )

            self._render_pieces()
            pygame.display.flip()

            clock.tick(60)
    
    def _render_highlights(self, mx: int, my: int, sel_mx: int, sel_my: int):
        self._update_cursor(mx, my)
        if self._selected_piece is not None:
            if self._selected_piece.get_location is not None:
                self._board.render_select_tile(sel_mx, sel_my, self._turn, self._board_status)
                self._board.render_destination_tiles(self._selected_piece, self._board_status)
            else:
                self._board.render_drop_tiles(self._selected_piece, self._board_status)
        else:
            if self._is_own_piece_selected(mx, my):
                self._board.render_select_tile(mx, my, self._turn, self._board_status)


    def _receiver(self):
        for message in self._network.recv():
            self._latest_message = message

        if self._latest_message is not None:
            latest_message = self._latest_message.payload
            split = latest_message.split('#')

            player = Player[split[2]]
            
            match split[0]:
                case 'select':
                    if split[1] != 'None':
                        fields_str = split[1]
                        fields = eval(fields_str)

                        piece: Piece = Piece(
                            Location(row = eval(fields[0])[0], col = eval(fields[0])[1]) if fields[0] != 'None' else None,
                            PieceType[fields[1]],
                            [Trait[trait] for trait in eval(fields[2])],
                            eval(fields[3]),
                            Player[fields[4]]
                        )

                        self._on_piece_select(piece, player)
                case 'move':
                    destination = eval(split[1])
                    self._on_move(Location(destination[0], destination[1]), player)
                case 'drop':
                    destination = eval(split[1])
                    self._on_drop(Location(destination[0], destination[1]), player)
                case 'undo':
                    self._on_undo(player)
                case 'new_game':
                    self._new_game()
                case _:
                    pass

    def _update_cursor(self, mx: int, my: int):
        if self._selected_piece is not None:
            if self._selected_piece.get_location is not None:
                tile_width = self._board.get_tile_width
                sel_x = self._board.get_x + self._selected_piece.get_location.col * tile_width
                sel_y = self._board.get_x + self._selected_piece.get_location.row * tile_width
                if self._board.mouse_on_tile(sel_x, sel_y, mx, my):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    return
                for destination in self._board.get_piece_destinations(self._selected_piece, self._board_status):
                    x = self._board.get_x + destination.col * tile_width
                    y = self._board.get_y + destination.row * tile_width
                    if self._board.mouse_on_tile(x, y, mx, my):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                        return
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        else:
            if self._is_own_piece_selected(mx, my):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def _set_active_pieces(self, x: int, y: int, width: int):
        for (i, row) in zip(range(self._board.get_row), self._board_status):
            for (j, piece) in zip(range(self._board.get_col), row):
                if piece is not None:
                    tile_width = self._board.get_tile_width
                    piece_x = x + j * tile_width + (tile_width - width) // 2
                    piece_y = y + i * tile_width + (tile_width - width) // 2
                    self._pieces.append(PieceView(piece_x, piece_y, width, piece))

    def _render_pieces(self):
        for piece in (self._pieces):
            piece.render(self._screen)

    def _is_own_piece_selected(self, mx: int, my: int) -> bool:
        for piece in self._pieces:
            if piece.is_on_piece(mx, my) and piece.get_piece.get_player is self._turn and Player[f'p{self._player_id}'] is self._turn:
                return True
        
        return False

    def _select_piece(self, mx: int, my: int) -> Piece | None:
        for piece in self._pieces:
            if piece.is_on_piece(mx, my):
                return piece.get_piece

    def _set_captured_pieces(self, x: int, y: int, width: int, captured: list[Piece]):
        for i in range(len(captured)):
            self._pieces.append(PieceView(x + i * self._board.get_tile_width, y, width, captured[i]))

    def register_new_game_observer(self, observer: NewGameObserver):
        self._new_game_observers.append(observer)
    
    def register_piece_select_observer(self, observer: PieceSelectObserver):
        self._piece_select_observers.append(observer)

    def register_move_observer(self, observer: MoveObserver):
        self._move_observers.append(observer)

    def register_drop_observer(self, observer: DropObserver):
        self._drop_observers.append(observer)
    
    def register_undo_observer(self, observer: UndoObserver):
        self._undo_observers.append(observer)

    def _new_game(self):
        for observer in self._new_game_observers:
            observer.on_new_game()

    def _on_piece_select(self, piece: Piece, player: Player):
        for observer in self._piece_select_observers:
            observer.on_piece_select(piece, player)

    def _on_move(self, location: Location, player: Player):
        for observer in self._move_observers:
            observer.on_move(location, player)

    def _on_drop(self, location: Location, player: Player):
        for observer in self._drop_observers:
            observer.on_drop(location, player)
    
    def _on_undo(self, player: Player):
        for observer in self._undo_observers:
            observer.on_undo(player)