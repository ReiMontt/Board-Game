from model import (Model, ChogiBoard, ChogiPieceInfo)
from view import PygameView
from controller import Controller

if __name__ == '__main__':
    model = Model(ChogiBoard(8, 8), ChogiPieceInfo())
    view = PygameView(model.state)

    controller = Controller(model, view)
    controller.start()