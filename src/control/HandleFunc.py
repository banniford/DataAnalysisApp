
import warnings
warnings.filterwarnings("ignore")
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow
from ui.Ui_DataAnalysis import Ui_MainWindow
from service.FileManager import FileManager
from service.DataAnalysis import DataAnalysis
from service.Draw import Draw
from service.ReportTable import ReportTable
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self)
        self.data_analysis = DataAnalysis(self)
        self.file_manager = FileManager(self)
        self.draw = Draw(self)
        self.report_table = ReportTable(self)
        # 采集间隔
        # self.delt_T = 200
        self.delt_T_set = self.main_ui.spinBox_0.value()
        self.master_var = []
        self.slave_var = []


        self.main_ui.action_0.triggered.connect(self.file_manager.loadCSVFile)
        self.main_ui.action_1.triggered.connect(self.file_manager.saveCSVFile)

        self.main_ui.checkBox_3.stateChanged.connect(self.changeDeltT)
        self.main_ui.comboBox2_1.currentTextChanged.connect(self.checkAbleComboBoxLeft)
        self.main_ui.comboBox2_2.currentTextChanged.connect(self.checkAbleComboBoxRight)
        self.main_ui.comboBox2_3.currentTextChanged.connect(self.comBoboxLeft)
        self.main_ui.comboBox2_4.currentTextChanged.connect(self.comBoboxRight)

    def checkAbleComboBoxLeft(self):
        items = self.main_ui.comboBox2_1.checkedItems()
        if "全选" in items:
            items.remove("全选")
        # 设置主变量
        self.master_var = items
        self.main_ui.comboBox2_3.clear()
        self.main_ui.comboBox2_3.addItems(items)
        # 设置下拉框样式, 使其不显示下拉箭头
        self.main_ui.comboBox2_3.setStyleSheet("QComboBox {combobox-popup: 0;}")
        # 设置下拉框最大显示条目数
        self.main_ui.comboBox2_3.setMaxVisibleItems(5)
        # 设置下拉框滚动条显示策略
        self.main_ui.comboBox2_3.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        
    
    def checkAbleComboBoxRight(self):
        items = self.main_ui.comboBox2_2.checkedItems()
        if "全选" in items:
            items.remove("全选")
        # 设置从变量
        self.slave_var = items
        self.main_ui.comboBox2_4.clear()
        self.main_ui.comboBox2_4.showPopup()
        self.main_ui.comboBox2_4.addItems(items)
        # 设置下拉框样式, 使其不显示下拉箭头
        self.main_ui.comboBox2_4.setStyleSheet("QComboBox {combobox-popup: 0;}")
        # 设置 下拉框最大显示条目数 
        self.main_ui.comboBox2_4.setMaxVisibleItems(5)
        # 设置下拉框滚动条显示策略
        self.main_ui.comboBox2_4.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)   
        
    def comBoboxLeft(self):
        # 绘制主变量散点图
        if self.master_var == []:
            return
        
        pass

    def comBoboxRight(self):
        # 绘制从变量
        if self.slave_var == []:
            return
        pass

    def msg(self, msg:str):
        # 打印时间在前面，格式化输出
        msg = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + msg
        self.main_ui.textEdit.append(msg)


    def changeDeltT(self):
        if self.main_ui.checkBox_3.isChecked():
            self.main_ui.spinBox_0.setEnabled(False)
            self.main_ui.spinBox_0.setValue(self.delt_T_set)
        else:
            self.main_ui.spinBox_0.setEnabled(True)
            self.main_ui.spinBox_0.setValue(self.delt_T_set)

    