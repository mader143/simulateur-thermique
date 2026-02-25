import sys

sys.path.append("..")

from SimControlcopy import SimControl
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = SimControl()
    main_window.show()

    app.exec_()