from PyQt6.QtWidgets import QFileDialog
import os
import pandas as pd

class FileManager:
    def __init__(self, main_window,data_analysis):
        self.main_window = main_window
        self.main_ui = main_window.main_ui
        self.data_analysis = data_analysis
        self.cwd = os.getcwd()
        self.file_path = None
        self.df = None

    def ClearFile(self):
        self.file_path = None
        self.df = None
        self.main_ui.comboBox2_1.clear()
        self.main_ui.comboBox2_2.clear()


    def LoadCSVFile(self):
        self.file_path = QFileDialog.getOpenFileName(self.main_window, '选择CSV文件', '', 'CSV files(*.csv)')
        if not self.file_path[0]:  # 用户取消
            self.main_ui.textEdit.append("未选择 csv 文件")
            self.ClearFile()
            return
        # 使用pandas读取csv文件
        try:
            self.df = pd.read_csv(self.file_path[0])
            self.main_ui.textEdit.append(f"文件 {self.file_path[0]} 加载成功")
            table_header = self.data_analysis.get_table_header(self.df)
            self.addcomboBoxItems(table_header)
        except Exception as e:
            print(e)
            self.main_ui.textEdit.append(f"文件 {self.file_path[0]} 加载失败")
            self.ClearFile()

        
    def SaveCSVFile(self):
        save_path = QFileDialog.getSaveFileName(self.main_window, '保存 CSV 文件', '', 'CSV files(*.csv)')
        if not save_path[0]:  # 用户取消
            self.main_ui.textEdit.append("未选择保存路径")
            return
        try:
            self.df.to_csv(save_path[0], index=False)
            self.main_ui.textEdit.append(f"文件 {save_path[0]} 保存成功")
        except Exception as e:
            print(e)
            self.main_ui.textEdit.append(f"文件 {save_path[0]} 保存失败")

    def addcomboBoxItems(self, items: list):
        self.main_ui.comboBox2_1.addCheckableItems(items)
        self.main_ui.comboBox2_2.addCheckableItems(items)