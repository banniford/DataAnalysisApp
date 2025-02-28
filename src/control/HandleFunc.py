
import warnings
warnings.filterwarnings("ignore")
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from ui.Ui_DataAnalysis import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self)
        self.main_ui.comboBox2_1.addCheckableItems(['test', 'test1', 'test2'])