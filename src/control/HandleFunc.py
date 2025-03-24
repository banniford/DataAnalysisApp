
import warnings
warnings.filterwarnings("ignore")
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow,QDialog
from ui.Ui_DataAnalysis import Ui_MainWindow
from ui.Ui_folder import Ui_Dialog
from service.FileManager import FileManager
from service.Draw import Draw

from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self)
        self.file_manager = FileManager(self)
        self.draw = Draw(self)
        # 采集间隔
        # self.delt_T = 200
        self.delt_T_set = self.main_ui.doubleSpinBox_1.value()
        self.master_var = []
        self.slave_var = []


        self.main_ui.action_0.triggered.connect(self.file_manager.loadCSVFile)
        self.main_ui.action_1.triggered.connect(self.file_manager.saveCSVFile)
        self.main_ui.action_2.triggered.connect(self.open_folder_csv)
        self.main_ui.action_3.triggered.connect(self.draw.set_scatter_visible)
        self.main_ui.action_4.triggered.connect(self.draw.set_reference_line_visible)



        self.main_ui.doubleSpinBox_1.valueChanged.connect(self.on_doubleSpinBox_1_valueChanged)
        self.main_ui.checkBox_3.stateChanged.connect(self.changeDeltT)
        self.main_ui.comboBox2_1.currentTextChanged.connect(self.checkAbleComboBoxLeft)
        self.main_ui.comboBox2_2.currentTextChanged.connect(self.checkAbleComboBoxRight)
        self.main_ui.comboBox2_3.currentTextChanged.connect(self.update_comBobox_left_ylim)
        self.main_ui.comboBox2_4.currentTextChanged.connect(self.update_comBobox_right_ylim)
        self.main_ui.comboBox2_5.currentTextChanged.connect(self.update_comBobox_left_color)
        self.main_ui.comboBox2_6.currentTextChanged.connect(self.update_comBobox_right_color)
        self.init_comboBox()

        self.main_ui.spinBox_4.valueChanged.connect(lambda val: self.draw.report_table.update_precision(val))

    def init_comboBox(self):
        # 设置下拉框样式, 使其不显示下拉箭头
        self.main_ui.comboBox2_3.setStyleSheet("QComboBox {combobox-popup: 0;}")
        # 设置下拉框最大显示条目数
        self.main_ui.comboBox2_3.setMaxVisibleItems(5)
        # 设置下拉框滚动条显示策略
        self.main_ui.comboBox2_3.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # 设置下拉框样式, 使其不显示下拉箭头
        self.main_ui.comboBox2_4.setStyleSheet("QComboBox {combobox-popup: 0;}")
        # 设置 下拉框最大显示条目数 
        self.main_ui.comboBox2_4.setMaxVisibleItems(5)
        # 设置下拉框滚动条显示策略
        self.main_ui.comboBox2_4.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded) 

        # 设置下拉框样式, 使其不显示下拉箭头
        self.main_ui.comboBox2_5.setStyleSheet("QComboBox {combobox-popup: 0;}")
        # 设置 下拉框最大显示条目数 
        self.main_ui.comboBox2_5.setMaxVisibleItems(5)
        # 设置下拉框滚动条显示策略
        self.main_ui.comboBox2_5.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded) 
        self.main_ui.comboBox2_5.addItems(self.draw.color_map.keys())
        # 设置索引为-1
        self.main_ui.comboBox2_5.setCurrentIndex(-1)

        # 设置下拉框样式, 使其不显示下拉箭头
        self.main_ui.comboBox2_6.setStyleSheet("QComboBox {combobox-popup: 0;}")
        # 设置 下拉框最大显示条目数
        self.main_ui.comboBox2_6.setMaxVisibleItems(5)
        # 设置下拉框滚动条显示策略
        self.main_ui.comboBox2_6.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.main_ui.comboBox2_6.addItems(self.draw.color_map.keys())
        # 设置索引为-1
        self.main_ui.comboBox2_6.setCurrentIndex(-1)




    def open_folder_csv(self):
        """打开子窗口，并确保它在主窗口之上"""
        self.folder = Folder()
        self.folder.main_ui.pushButton_1.clicked.connect(self.load_folder)
        self.folder.main_ui.pushButton_2.clicked.connect(self.cal_csv)
        self.folder.main_ui.spinBox_0.valueChanged.connect(lambda val: self.file_manager.change_header_threshold(val))
        if not hasattr(self, 'folder') or self.folder is None:
            self.folder = Folder(self)  # 让 Folder 依赖 MainWindow
        self.folder.show()  # 以非模态方式打开
        self.folder.raise_()  # 确保窗口在最前面

    def load_folder(self):
        table_header = self.file_manager.load_folder()
        self.folder.main_ui.comboBox_1.clear()
        if table_header is None:
            return
        self.folder.main_ui.comboBox_1.addCheckableItems(table_header)
        self.folder.main_ui.comboBox_1.setCurrentIndex(-1)  # 设置默认不选中任何选项
        self.folder.main_ui.comboBox_1.lineEdit().clear()  # 确保 lineEdit 初始状态为空

    def cal_csv(self):
        if not self.file_manager.folder_path:
            self.msg("未选择文件夹")
            return
        if not self.file_manager.csv_files:
            self.msg(f"文件夹 {self.folder_path} 下没有 csv 文件")
            return
        
        var_list = self.folder.main_ui.comboBox_1.checkedItems()
        if not var_list:
            self.msg("未选择变量")
            return
        
        cal_type = self.folder.main_ui.comboBox.currentText()
        if cal_type == "平均值":
            table_data =  {"文件名":[]}
            for i in self.file_manager.csv_files:
                try:
                    df = self.file_manager.load_file(self.file_manager.folder_path + "/" + i)
                    table_data["文件名"].append(i)
                    for var in var_list:
                        if not table_data.get(f"{var} 平均值"):
                            table_data[f"{var} 平均值"] = []
                        table_data[f"{var} 平均值"].append(self.draw.data_analysis.cal_csv_avg(df,var))
                except Exception as e:
                    self.msg(f"文件 {i} 加载失败,失败原因 {e} ")
                    continue
            self.draw.report_table.update_csv_table(table_data)
        elif cal_type == "最大值":
            table_data =  {"文件名":[]}
            for i in self.file_manager.csv_files:
                try:
                    df = self.file_manager.load_file(self.file_manager.folder_path + "/" + i)
                    table_data["文件名"].append(i)
                    for var in var_list:
                        if not table_data.get(f"{var} 最大值"):
                            table_data[f"{var} 最大值"] = []
                        if not table_data.get(f"{var} 最大值索引"):
                            table_data[f"{var} 最大值索引"] = []
                        max,idx = self.draw.data_analysis.cal_csv_max(df,var)
                        table_data[f"{var} 最大值"].append(max)
                        table_data[f"{var} 最大值索引"].append(idx)
                except Exception as e:
                    self.msg(f"文件 {i} 加载失败,失败原因 {e} ")
                    continue
            self.draw.report_table.update_csv_table(table_data)
            
        elif cal_type == "最小值":
            table_data =  {"文件名":[]}
            table_data =  {"文件名":[]}
            for i in self.file_manager.csv_files:
                try:
                    df = self.file_manager.load_file(self.file_manager.folder_path + "/" + i)
                    table_data["文件名"].append(i)
                    for var in var_list:
                        if not table_data.get(f"{var} 最小值"):
                            table_data[f"{var} 最小值"] = []
                        if not table_data.get(f"{var} 最小值索引"):
                            table_data[f"{var} 最小值索引"] = []
                        min,idx = self.draw.data_analysis.cal_csv_min(df,var)
                        table_data[f"{var} 最小值"].append(min)
                        table_data[f"{var} 最小值索引"].append(idx)
                except Exception as e:
                    self.msg(f"文件 {i} 加载失败,失败原因 {e} ")
                    continue
            self.draw.report_table.update_csv_table(table_data)



    def on_doubleSpinBox_1_valueChanged(self):
        self.delt_T_set = self.main_ui.doubleSpinBox_1.value()

    def _raw_index_formatter(self, value, pos):
        """示例：直接显示整数索引"""
        return f"{int(value)}"

    def _scaled_index_formatter(self, value, pos):
        """示例：显示索引 * self.delt_T_set"""
        return f"{int(value * self.delt_T_set)}"

    def changeDeltT(self):
        if self.main_ui.checkBox_3.isChecked():
            self.main_ui.doubleSpinBox_1.setEnabled(False)
            self.draw.update_x_formatter(self._scaled_index_formatter)
            # 设置y轴标签，在右下角
            xlabel = self.draw.canvas.ax_left.set_xlabel("T[s]", labelpad=0.1)
            xlabel.set_horizontalalignment("right")
            xlabel.set_position((1.0, 1.0))  # 可根据效果微调位置
        else:
            self.main_ui.doubleSpinBox_1.setEnabled(True)
            self.draw.update_x_formatter(self._raw_index_formatter)
            # xlabel 设置为空，不显示
            self.draw.canvas.ax_left.set_xlabel("数据点位")


    def checkAbleComboBoxLeft(self):
        items = self.main_ui.comboBox2_1.checkedItems()
        # if "全选" in items:
        #     items.remove("全选")
        self.update_master(items)
        # 设置主变量
        # 获取之前的主变量
        text = self.main_ui.comboBox2_3.currentText()
        # 清除主变量
        self.main_ui.comboBox2_3.clear()
        self.main_ui.comboBox2_3.showPopup()
        self.main_ui.comboBox2_3.addItems(items)
        # 设置之前的主变量
        if text in items:
            self.main_ui.comboBox2_3.setCurrentIndex(items.index(text))
        
    
    def checkAbleComboBoxRight(self):
        items = self.main_ui.comboBox2_2.checkedItems()
        # if "全选" in items:
        #     items.remove("全选")
        self.update_slave(items)  
        # 设置从变量
        self.main_ui.comboBox2_4.clear()
        self.main_ui.comboBox2_4.showPopup()
        self.main_ui.comboBox2_4.addItems(items)
        
        
    def update_comBobox_left_ylim(self):
        '''
        更新左侧y轴范围
        '''
        if self.main_ui.comboBox2_3.currentText() == "":
            return
        # 更新左侧y轴范围
        self.draw.update_left_ylim()
        # 更新左侧y轴颜色
        master_var = self.main_ui.comboBox2_3.currentText()
        cur_color = self.draw.line_manager[master_var].color
        reverse_map = {v: k for k, v in self.draw.color_map.items()}
        # 设置颜色,查找颜色对应的索引
        self.main_ui.comboBox2_5.setCurrentIndex(self.main_ui.comboBox2_5.findText(reverse_map[cur_color]))

    def update_comBobox_left_color(self):
        '''
        更新左侧y轴颜色
        '''
        if self.main_ui.comboBox2_3.currentText() == "":
            return
        # 更新左侧y轴颜色
        master_var = self.main_ui.comboBox2_3.currentText()
        line = self.draw.line_manager.get(master_var)
        if line is None:
            return
        line.color = self.draw.color_map[self.main_ui.comboBox2_5.currentText()]

        # 修改主变量的散点颜色
        scatter = self.draw.scatter_manager.get(master_var)
        if scatter is None:
            return
        scatter.color = self.draw.color_map[self.main_ui.comboBox2_5.currentText()]

    def update_comBobox_right_ylim(self):
        '''
        更新 右侧y轴范围
        '''
        if self.main_ui.comboBox2_4.currentText() == "":
            return
        # 更新右侧y轴范围
        self.draw.update_right_ylim()
        # 更新右侧y轴颜色
        slave_var = self.main_ui.comboBox2_4.currentText()
        cur_color = self.draw.line_manager[slave_var].color
        reverse_map = {v: k for k, v in self.draw.color_map.items()}
        # 设置颜色,查找颜色对应的索引
        self.main_ui.comboBox2_6.setCurrentIndex(self.main_ui.comboBox2_6.findText(reverse_map[cur_color]))

    def update_comBobox_right_color(self):
        '''
        更新右侧y轴颜色
        '''
        if self.main_ui.comboBox2_4.currentText() == "":
            return
        # 更新右侧y轴颜色
        slave_var = self.main_ui.comboBox2_4.currentText()
        line = self.draw.line_manager.get(slave_var)
        if line is None:
            return
        line.color = self.draw.color_map[self.main_ui.comboBox2_6.currentText()]
        # 修改从变量的散点颜色
        scatter = self.draw.scatter_manager.get(slave_var)
        if scatter is None:
            return
        scatter.color = self.draw.color_map[self.main_ui.comboBox2_6.currentText()]

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
                self.draw.draw_master(var_key)
        else:
            diff = list(set(self.master_var)-set(master_var))
            # 清除从变量列表, 并添加新的从变量
            self.main_ui.comboBox2_2.addCheckableItems(diff)
            self.master_var = master_var
            for var_key in diff:
                self.draw.clear_master(var_key)
            
        
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
                self.draw.draw_slave(var_key)
        else:
            diff = list(set(self.slave_var)-set(slave_var))
            # 清除主变量列表, 并添加新的主变量
            self.main_ui.comboBox2_1.addCheckableItems(diff)
            self.slave_var = slave_var
            for var_key in diff:
                self.draw.clear_slave(var_key)

    def msg(self, msg:str):
        # 打印时间在前面，格式化输出
        msg = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + msg
        self.main_ui.textEdit.append(msg)

    

class Folder(QDialog):
    def __init__(self):
        super().__init__()
        self.main_ui = Ui_Dialog()
        self.main_ui.setupUi(self)
        self.main_ui.comboBox.clear()
        self.main_ui.comboBox.addItems(["平均值", "最大值", "最小值"])

        # 设置窗口始终保持在前
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

