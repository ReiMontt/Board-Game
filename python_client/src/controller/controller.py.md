# Controller Class Documentation

[Linked Table of Contents](#linked-table-of-contents)

## Linked Table of Contents

* [1. Introduction](#1-introduction)
* [2. Class Overview: `Controller`](#2-class-overview-controller)
    * [2.1 Attributes](#21-attributes)
    * [2.2 Methods](#22-methods)
        * [2.2.1 `__init__(self, model: Model, view: View)`](#221-__init__self-model-model-view-view)
        * [2.2.2 `start(self)`](#222-startself)
        * [2.2.3 `on_new_game(self)`](#223-on_new_gameself)
        * [2.2.4 `on_piece_select(self, piece: Piece, player: Player)`](#224-on_piece_selectself-piece-piece-player-player)
        * [2.2.5 `on_move(self, location: Location, player: Player)`](#225-on_moveself-location-location-player-player)
        * [2.2.6 `on_drop(self, location: Location, player: Player)`](#226-on_dropself-location-location-player-player)
        * [2.2.7 `on_undo(self, player: Player)`](#227-on_undosellf-player-player)
        * [2.2.8 `register_game_state_change_observer(self, observer: GameStateChangeObserver)`](#228-register_game_state_change_observerself-observer-gamestatechangeobserver)
        * [2.2.9 `_on_state_change(self, state: GameState)`](#229-_on_state_changeself-state-gamestate)


## 1. Introduction

This document provides internal code documentation for the `Controller` class.  The `Controller` acts as the intermediary between the `Model` (game logic) and the `View` (user interface), managing user interactions and updating both the model and the view accordingly.


## 2. Class Overview: `Controller`

The `Controller` class orchestrates the game flow by receiving inputs from the `View`, updating the `Model`, and propagating state changes back to the `View`. It uses the Observer pattern to efficiently manage updates.

### 2.1 Attributes

| Attribute Name                     | Type                                     | Description                                                                 |
|--------------------------------------|------------------------------------------|-----------------------------------------------------------------------------|
| `_model`                            | `Model`                                  | Instance of the `Model` class, representing the game's internal state.      |
| `_view`                             | `View`                                   | Instance of the `View` class, responsible for displaying the game and handling user input. |
| `_game_state_change_observers`      | `list[GameStateChangeObserver]`           | A list of observers that are notified whenever the game state changes.       |


### 2.2 Methods

#### 2.2.1 `__init__(self, model: Model, view: View)`

The constructor initializes the `Controller` with instances of the `Model` and `View`. It also initializes the list of game state change observers to an empty list.

#### 2.2.2 `start(self)`

This method initializes the game loop. It registers the `View` as a game state change observer and registers various event handlers within the `View` to listen for user actions (new game, piece selection, movement, drop, and undo). Finally, it starts the `View`'s main run loop.

#### 2.2.3 `on_new_game(self)`

This method is called when the user initiates a new game. It instructs the `Model` to create a new game state and then notifies all observers of the state change using `_on_state_change`.

#### 2.2.4 `on_piece_select(self, piece: Piece, player: Player)`

This method handles piece selection events. It updates the `Model` with the selected piece and player information and subsequently updates all observers.

#### 2.2.5 `on_move(self, location: Location, player: Player)`

This method handles piece movement events. It informs the `Model` about the move and updates the observers using `_on_state_change`.

#### 2.2.6 `on_drop(self, location: Location, player: Player)`

This method handles piece dropping events.  Similar to `on_move`, it updates the `Model` and notifies observers.

#### 2.2.7 `on_undo(self, player: Player)`

This method handles undo requests. It requests an undo from the `Model` and updates the observers.

#### 2.2.8 `register_game_state_change_observer(self, observer: GameStateChangeObserver)`

This method adds a new observer to the list of observers that will be notified of game state changes.

#### 2.2.9 `_on_state_change(self, state: GameState)`

This is a private helper method. It iterates through the list of registered observers and calls the `on_state_change` method on each observer, passing the current `GameState`.  This method implements the notification mechanism of the Observer pattern, ensuring that all interested parties are updated whenever the game state changes.  The algorithm is a simple iteration over the observer list.
