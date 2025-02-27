
import warnings
warnings.filterwarnings("ignore")
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.uic import loadUi

class MainWindow(QMainWindow):
    def __init__(self, ui_path):
        super().__init__()
        loadUi(ui_path, self)