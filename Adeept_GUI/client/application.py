# TODO Drive controller (forward, backwards, turn left, turn right, speed)

# TODO Camera controller (up, down, home)

# TODO Light controller

# TODO 'Mode' controller (Police, Fire Engine, opencv follow, opencv detect, opencv line follow)

# TODO Status Controller (Connect, Shutdown)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow 
from PyQt6.QtWidgets import QWidget
import sys


class AdeeptGui(QMainWindow):
    """ GUI to control an Adeept Robot """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Adeept Robot Controller')
        self.setMinimumSize(600, 480)


def main():
    app = QApplication(sys.argv)
    view = AdeeptGui()
    view.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
