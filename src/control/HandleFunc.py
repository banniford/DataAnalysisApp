
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

        self.main_ui.spinBox_0.valueChanged.connect(self.on_spinBox_0_valueChanged)
        self.main_ui.checkBox_3.stateChanged.connect(self.changeDeltT)
        self.main_ui.comboBox2_1.currentTextChanged.connect(self.checkAbleComboBoxLeft)
        self.main_ui.comboBox2_2.currentTextChanged.connect(self.checkAbleComboBoxRight)
        self.main_ui.comboBox2_3.currentTextChanged.connect(self.update_comBobox_left_ylim)
        self.main_ui.comboBox2_4.currentTextChanged.connect(self.update_comBobox_right_ylim)

    def on_spinBox_0_valueChanged(self):
        self.delt_T_set = self.main_ui.spinBox_0.value()

    def _raw_index_formatter(self, value, pos):
        """示例：直接显示整数索引"""
        return f"{int(value)}"

    def _scaled_index_formatter(self, value, pos):
        """示例：显示索引 * self.delt_T_set"""
        return f"{int(value * self.delt_T_set)}"

    def changeDeltT(self):
        if self.main_ui.checkBox_3.isChecked():
            self.main_ui.spinBox_0.setEnabled(False)
            self.draw.update_x_formatter(self._scaled_index_formatter)
        else:
            self.main_ui.spinBox_0.setEnabled(True)
            self.draw.update_x_formatter(self._raw_index_formatter)


    def checkAbleComboBoxLeft(self):
        items = self.main_ui.comboBox2_1.checkedItems()
        if "全选" in items:
            items.remove("全选")
        # 设置主变量
        self.update_master(items)
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
        self.update_slave(items)
        self.main_ui.comboBox2_4.clear()
        self.main_ui.comboBox2_4.showPopup()
        self.main_ui.comboBox2_4.addItems(items)
        # 设置下拉框样式, 使其不显示下拉箭头
        self.main_ui.comboBox2_4.setStyleSheet("QComboBox {combobox-popup: 0;}")
        # 设置 下拉框最大显示条目数 
        self.main_ui.comboBox2_4.setMaxVisibleItems(5)
        # 设置下拉框滚动条显示策略
        self.main_ui.comboBox2_4.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)   
        
    def update_comBobox_left_ylim(self):
        # 绘制主变量散点图
        if self.main_ui.comboBox2_3.currentText() == "":
            return
        v = self.data_analysis.get_var_value(self.main_ui.comboBox2_3.currentText())
        self.draw.update_left_ylim(v)
        

    def update_comBobox_right_ylim(self):
        # 绘制从变量
        if self.main_ui.comboBox2_4.currentText() == "":
            return
        v = self.data_analysis.get_var_value(self.main_ui.comboBox2_4.currentText())
        self.draw.update_right_ylim(v)

    def update_master(self, master_var:list):
        '''
        检查主变量是变多还是变少，变多直接赋值，并在从变量列表中删除该项，变少需要清除变少的主变量图，并在从变量列表中添加该项
        '''
        if len(master_var) >= len(self.master_var):
            # 清除从变量列表, 并添加新的从变量
            diff = list(set(master_var)-set(self.master_var))
            self.main_ui.comboBox2_2.remove_diff(diff)
            self.master_var = master_var
            # 绘制主变量散点图
            for var_key in self.master_var:
                v = self.data_analysis.get_var_value(var_key)
                self.draw.draw_scatter(var_key, range(len(v)), v)
                # 检测突变点
                jumps = self.data_analysis.pandas_detect_jumps(var_key, 50, self.draw.slider.val)
                self.draw.draw_reference_line(var_key,jumps)
                
        else:
            diff = list(set(self.master_var)-set(master_var))
            # 清除从变量列表, 并添加新的从变量
            self.main_ui.comboBox2_2.addCheckableItems(diff)
            self.master_var = master_var
            for var_key in diff:
                self.draw.clear_scatter(var_key)
                self.draw.clear_reference_line(var_key)
            
        
    def update_slave(self, slave_var:list):
        '''
        检查从变量是变多还是变少，变多直接赋值，并在主变量列表中删除该项，变少需要清除变少的从变量图，并在主变量列表中添加该项
        '''
        if len(slave_var) > len(self.slave_var):
            # 清除主变量列表, 并添加新的主变量
            diff = list(set(slave_var)-set(self.slave_var))
            self.main_ui.comboBox2_1.remove_diff(diff)
            self.slave_var = slave_var
            # 绘制从变量散点图
            for var_key in self.slave_var:
                v = self.data_analysis.get_var_value(var_key)
                self.draw.draw_scatter(var_key, range(len(v)), v)
        else:
            diff = list(set(self.slave_var)-set(slave_var))
            # 清除主变量列表, 并添加新的主变量
            self.main_ui.comboBox2_1.addCheckableItems(diff)
            self.slave_var = slave_var
            for var_key in diff:
                self.draw.clear_scatter(var_key)
        

    def msg(self, msg:str):
        # 打印时间在前面，格式化输出
        msg = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + msg
        self.main_ui.textEdit.append(msg)

    

    