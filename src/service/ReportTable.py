from PyQt6.QtWidgets import QAbstractItemView, QHeaderView, QAbstractScrollArea, QTableWidgetItem, QMenu, QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence
from service.DataAnalysis import DataAnalysis
import numpy as np

class ReportTable:
    def __init__(self, main_window,data_analysis:DataAnalysis):
        self.main_window = main_window
        self.main_ui = main_window.main_ui
        self.table = self.main_ui.tableWidget
        self.data_analysis = data_analysis
        self.table_data = {}
        # 小数点精度
        self._precision = 2
        self.cal_list = []


        # 设置表格大小调整为内容适应
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)  
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # 设置表格不可编辑
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # 启用表格自适应列宽
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # 绑定右键菜单
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        # 绑定 Ctrl+C 复制快捷键
        self.table.keyPressEvent = self.keyPressEvent

    @property
    def precision(self):
        return self._precision
    
    @precision.setter
    def precision(self, value):
        self._precision = value
        if self.cal_list:
            self.update_table(self.cal_list)

    def update_precision(self, precision):
        """更新小数点精度"""
        self.precision = precision

    def update_table(self, cal_list:list):
        """更新表格数据"""
        self.cal_list = cal_list
        for i in cal_list:
            if i not in self.table_data:
                    self.table_data[i] = {"avg": [], "max_min": []}
        
            # 平均数根据小数点精度进行四舍五入
            self.table_data[i]["avg"] = [
                np.floor(value * (10 ** self.precision)) / (10 ** self.precision) 
                for value in self.data_analysis.data_avg[i]
            ]
            self.table_data[i]["max_min"] = self.data_analysis.data_max_min[i]
        # 清空表格
        self.clear_all_columns()
        # 显示数据
        self.show_data(cal_list)

    def show_data(self,cal_list:list):
        """显示数据"""
        # 添加第一列为稳定阶段的数据
        if not self.data_analysis.stable_interval[cal_list[0]]:
            self.add_column("稳定阶段", [f"0 - {self.data_analysis.get_table_num()-1}"])
            self.data_analysis.get_table_columns()
        else:
            self.add_column("稳定阶段", [f"{interval[0]} - {interval[1]}" for interval in self.data_analysis.stable_interval[cal_list[0]]])
        # 添加第二列主次变量得参数 名称+平均值 在前面
        for i in cal_list:
            self.add_column(f"{i} 平均值", self.table_data[i]["avg"])

        for i in cal_list:
             # 添加第四列为主变量最大值索引
            self.add_column(f"{i} 最大值索引", [f"{max_min[1]}" for max_min in self.table_data[i]['max_min']])
            # 添加第五列为最大值
            self.add_column(f"{i} 最大值", [f"{np.floor(max_min[0] * (10 ** self.precision)) / (10 ** self.precision)}" for max_min in self.table_data[i]['max_min']])
           # 添加第六列为最小值索引
            self.add_column(f"{i} 最小值索引", [f"{max_min[3]}" for max_min in self.table_data[i]['max_min']])
            # 添加第七列为最小值
            self.add_column(f"{i} 最小值", [f"{np.floor(max_min[2] * (10 ** self.precision)) / (10 ** self.precision)}" for max_min in self.table_data[i]['max_min']])

    def update_csv_table(self, table_data:dict):
        """更新表格数据"""
        self.clear_all_columns()
        for key,value in table_data.items():
            # 检查列表是否为数值列表，如果是则保留小数点精度
            if all(isinstance(val, (float)) for val in value):
                value = [np.floor(val * (10 ** self.precision)) / (10 ** self.precision) for val in value]
            self.add_column(key, value)

    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu(self.table)
        copy_action = menu.addAction("复制")
        copy_action.triggered.connect(self.copy_selection)
        menu.exec(self.table.viewport().mapToGlobal(position))

    def copy_selection(self):
        """复制选中内容到剪贴板"""
        try:
            selected_ranges = self.table.selectedRanges()
            if not selected_ranges:
                return

            copied_data = []
            for selection in selected_ranges:
                rows = []
                for row in range(selection.topRow(), selection.bottomRow() + 1):
                    columns = []
                    for col in range(selection.leftColumn(), selection.rightColumn() + 1):
                        item = self.table.item(row, col)
                        columns.append(item.text() if item else "")
                    rows.append("\t".join(columns))
                copied_data.append("\n".join(rows))

            clipboard = QApplication.clipboard()
            clipboard.setText("\n".join(copied_data))

        except Exception as e:
            QMessageBox.critical(None, "复制失败", f"错误: {str(e)}")

    def keyPressEvent(self, event):
        """监听 Ctrl+C 复制"""
        try:
            if event.matches(QKeySequence.StandardKey.Copy):
                self.copy_selection()
            else:
                super(QAbstractItemView, self.table).keyPressEvent(event)  # 保持原有按键功能
        except Exception as e:
            QMessageBox.critical(None, "快捷键错误", f"错误: {str(e)}")

    def add_column(self, column_name: str, data: list):
        """添加一列数据"""
        col_index = self.table.columnCount()  # 获取当前列数
        self.table.insertColumn(col_index)  # 插入新列
        self.table.setHorizontalHeaderLabels(self.get_column_headers() + [column_name])

        # 填充数据
        for row_index, value in enumerate(data):
            if row_index >= self.table.rowCount():
                self.table.insertRow(row_index)  # 如果数据超出行数，新增行
            self.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

    def add_row(self, row_data: list):
        """添加一行数据"""
        row_index = self.table.rowCount()  # 获取当前行数
        self.table.insertRow(row_index)  # 插入新行

        # 填充数据
        for col_index, value in enumerate(row_data):
            if col_index >= self.table.columnCount():
                self.table.insertColumn(col_index)  # 如果数据超出列数，新增列
            self.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

    def delete_column(self, column_name):
        """删除指定列"""
        col_index = self.get_column_headers().index(column_name)  # 获取列索引
        self.table.removeColumn(col_index)  # 删除列
        

    def delete_row(self, row_index):
        """删除指定行"""
        if 0 <= row_index < self.table.rowCount():
            self.table.removeRow(row_index)  # 删除行
        
    def get_column_headers(self):
        """获取表格当前列头"""
        return [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount()) if self.table.horizontalHeaderItem(i)]

    def clear_all_rows(self):
        """清空所有行"""
        self.table.setRowCount(0)

    def clear_all_columns(self):
        """清空下的所有列"""
        self.table.setColumnCount(0)

    def get_all_table_data(self):
        """获取表格所有数据"""
        table_data = []

        # 获取列头
        column_headers = self.get_column_headers()
        table_data.append(column_headers)

        # 遍历所有行和列获取数据
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            table_data.append(row_data)

        return table_data