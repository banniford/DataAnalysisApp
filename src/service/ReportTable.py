from PyQt6.QtWidgets import QAbstractItemView, QHeaderView, QAbstractScrollArea, QTableWidgetItem, QMenu, QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence
from service.DataAnalysis import DataAnalysis

class ReportTable:
    def __init__(self, main_window,data_analysis:DataAnalysis):
        self.main_window = main_window
        self.main_ui = main_window.main_ui
        self.table = self.main_ui.tableWidget
        self.data_analysis = data_analysis
        self.table_data = {}


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


    def update_table(self, name):
        """更新表格数据"""
        if name not in self.table_data:
            self.table_data[name] = {"avg": [], "max_min": []}
        
        self.table_data[name]["avg"] = self.data_analysis.data_avg[name]
        self.table_data[name]["max_min"] = self.data_analysis.data_max_min[name]
        self.show_data(name)

    def show_data(self, name):
        """显示数据"""
        # 检查当前name是否等于 comboBox2_3 的值
        if self.main_ui.comboBox2_3.currentText() != name and self.data_analysis.stable_interval.get(name) is None:
            return
        
        
        self.clear_all_columns()
        # 添加第一列为稳定阶段的数据
        if not self.data_analysis.stable_interval[name]:
            self.add_column("稳定阶段", [f"0 - {self.data_analysis.get_table_num()-1}"])
            self.data_analysis.get_table_columns()
        else:
            self.add_column("稳定阶段", [f"{interval[0]} - {interval[1]}" for interval in self.data_analysis.stable_interval[name]])
        # 添加第二列为原始表格中 Time [s] 列的数据
        if not self.data_analysis.stable_interval[name]:
            self.add_column("Time [s]", [f"{self.data_analysis.get_var_value('Time [s]')[0]} - {self.data_analysis.get_var_value('Time [s]')[self.data_analysis.get_table_num()-1]}"])
        else:
            self.add_column("Time [s]", [f"{self.data_analysis.get_var_value('Time [s]')[interval[0]]} - {self.data_analysis.get_var_value('Time [s]')[interval[1]]}"  for interval in self.data_analysis.stable_interval[name]])
        # 添加第三列为平均值
        self.add_column("平均值", self.table_data[name]["avg"])
        # 添加第四列为最大值索引
        self.add_column("最大值索引", [f"{max_min[1]}" for max_min in self.table_data[name]['max_min']])
        # 添加第五列为最大值
        self.add_column("最大值", [f"{max_min[0]}" for max_min in self.table_data[name]['max_min']])
        # 添加第六列为最小值索引
        self.add_column("最小值索引", [f"{max_min[3]}" for max_min in self.table_data[name]['max_min']])
        # 添加第七列为最小值
        self.add_column("最小值", [f"{max_min[2]}" for max_min in self.table_data[name]['max_min']])


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
        """清空所有列"""
        self.table.setColumnCount(0)