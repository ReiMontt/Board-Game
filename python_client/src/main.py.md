# Chogi Game: Internal Code Documentation

[TOC]

## 1. Overview

This document provides internal documentation for the main execution flow of the Chogi game.  The game uses a Model-View-Controller (MVC) architectural pattern.

## 2. Modules

The code utilizes three core modules:

| Module      | Description                                      |
|-------------|--------------------------------------------------|
| `model`     | Contains the game's data and logic (Model, ChogiBoard, ChogiPieceInfo). |
| `view`      | Handles the game's visual representation (PygameView). |
| `controller`| Manages user input and updates the model and view. |


## 3. Main Execution Flow

The `if __name__ == '__main__':` block orchestrates the game's initialization and execution.


```python
if __name__ == '__main__':
    model = Model(ChogiBoard(8, 8), ChogiPieceInfo())
    view = PygameView(model.state)
    controller = Controller(model, view)
    controller.start()
```

This section instantiates the core components of the MVC architecture:

1. **Model Initialization:** A `Model` object is created.  This involves initializing a `ChogiBoard` object (presumably an 8x8 board) and a `ChogiPieceInfo` object (containing information about the game pieces).  The details of `ChogiBoard` and `ChogiPieceInfo` are not provided in this snippet but are assumed to be defined within the `model` module.

2. **View Initialization:** A `PygameView` object is created, passing the initial game state (`model.state`) from the `Model` as an argument. This sets up the Pygame display to reflect the initial board configuration.

3. **Controller Initialization:** A `Controller` object is created, taking both the `Model` and `View` as arguments. This establishes the connection between the game's logic, data, and presentation.

4. **Game Start:** The `controller.start()` method is called, initiating the game loop.  The implementation of this method is not shown here, but it is presumed to handle user input, update the game state, and refresh the view accordingly.


## 4.  Class Interactions

The code demonstrates a clear separation of concerns via the MVC pattern.  The `Model` holds the game's data, the `View` displays it, and the `Controller` manages the interaction between them.  Data flow is unidirectional, from the Model to the View, with the Controller acting as the intermediary.  The details of the classes and their methods are not explicitly shown in this code snippet but are crucial for understanding the full game logic.  Further documentation of these classes is recommended.
