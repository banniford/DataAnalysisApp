
import warnings
warnings.filterwarnings("ignore")
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from ui.Ui_DataAnalysis import Ui_MainWindow
from service.FileManager import FileManager
from service.DataAnalysis import DataAnalysis

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self)
        self.data_analysis = DataAnalysis(self)
        self.file_manager = FileManager(self,self.data_analysis)



        self.main_ui.action_0.triggered.connect(self.file_manager.LoadCSVFile)
        self.main_ui.action_1.triggered.connect(self.file_manager.SaveCSVFile)

    