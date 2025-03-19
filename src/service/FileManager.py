# Filename: FileManager.py
from PyQt6.QtWidgets import QFileDialog
import os
import pandas as pd
import numpy as np

class FileManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_ui = main_window.main_ui
        self.cwd = os.getcwd()
        self.file_path = None
        self.df = None

    def clear(self):
        self.file_path = None
        self.df = None
        self.main_ui.comboBox2_1.clear()
        self.main_ui.comboBox2_2.clear()
        self.main_window.draw.reset()

    def loadCSVFile(self):
        """
        通用方式：先手动读取 CSV 文件的所有行，自动检测到哪一行才是真正的表头；
        然后用 skiprows + header=0 让 pandas 正式解析该文件。
        """
        self.clear()
        self.file_path = QFileDialog.getOpenFileName(self.main_window, '选择CSV文件', '', 'CSV files(*.csv)')
        if not self.file_path[0]:  # 用户取消
            self.main_window.msg("未选择 csv 文件")
            return

        try:
            # 1) 自动检测 CSV 中真正的表头行号
            header_line_index = self._detect_header_line_by_colcount(self.file_path[0])
            if header_line_index is None:
                # 如果检测不到合适的表头行，你可以选择报错或给个默认值
                self.main_window.msg("未找到稳定的表头行，请检查文件格式")
                return
            print(f"检测到表头行号：{header_line_index}")
            # 2) 用 skiprows 指定要跳过的行，让 pandas 从检测到的那行开始当作表头
            self.df = pd.read_csv(
                self.file_path[0],
                skiprows=header_line_index,  # 跳过前 header_line_index 行
                header=0,                    # 让这一行成为 columns
                float_precision='round_trip',
                skip_blank_lines=True
            )

            # 3) 替换表头中的特殊符号
            self._clean_special_symbols_in_columns()

            # 4) 删除全部为 NaN 的行（如果有多余空行）
            self.df.dropna(axis=0, how='all', inplace=True)
            # ★ 只保留数值型的列（float / int）
            self.df = self.df.select_dtypes(include=[np.number])

            # 5) 将 DataFrame 交给你的数据分析模块
            self.main_window.draw.data_analysis.set_table_data(self.df)
            table_header = self.main_window.draw.data_analysis.get_table_header()
            self.addComboBoxItems(table_header)

            self.main_window.msg(f"文件 {self.file_path[0]} 加载成功")
        except Exception as e:
            print(e)
            self.main_window.msg(f"文件 {self.file_path[0]} 加载失败")
            self.clear()

    def saveCSVFile(self):
        save_path = QFileDialog.getSaveFileName(self.main_window, '保存 CSV 文件', '', 'CSV files(*.csv)')
        if not save_path[0]:  # 用户取消
            self.main_window.msg("未选择保存路径")
            return
        try:
            self.df.to_csv(save_path[0], index=False)
            self.main_window.msg(f"文件 {save_path[0]} 保存成功")
        except Exception as e:
            print(e)
            self.main_window.msg(f"文件 {save_path[0]} 保存失败")

    def addComboBoxItems(self, items: list):
        self.main_ui.comboBox2_1.addCheckableItems(items)
        self.main_ui.comboBox2_2.addCheckableItems(items)

    # -------------------------------------------------------
    # 下面是通用的“自动检测表头行”函数 & 表头符号清洗函数
    # -------------------------------------------------------

    def _detect_header_line_by_colcount(self, csv_path):
        """
        从 CSV 文件开头逐行扫描，尝试找到最可能的表头所在行。
        策略：
          1) 忽略空行或只有少数列的行。
          2) 找到第一行，其列数较多(>=某阈值) 并且后面若干行的列数也一致或相似，
             则判定它为表头行。
        返回：
          - 如果找到，返回该行在文件中的“索引”（从 0 开始）
          - 如果找不到，返回 None
        """
        lines = []
        # 先把文件整行读进来，存储到 list 中
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 统计每一行的列数
        col_counts = []
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            # 跳过空行
            if not line_stripped:
                col_counts.append(0)
                continue
            # 分割逗号，统计列数
            columns = line_stripped.split(',')
            col_counts.append(len(columns))

        # 这里给一个简化逻辑：找“第一个显著大于 1 的列数”，
        # 并且后面紧邻的几行也保持相似列数(±0或±1都算)，则视为表头。
        # 你也可以改成“找最大列数”或者别的更复杂判断。
        for i in range(len(col_counts)):
            c = col_counts[i]
            if c > 15: # 举个例子，假设列数大于 15 就是表头
                # 检查后面若干行，如果列数也和 c 差不多，就认为是表头行
                # 这里简单判断下一行也有同样列数就通过
                if i + 1 < len(col_counts) and col_counts[i+1] == c:
                    return i
                # 或者可放宽判断：绝大部分后续行都 == c 时即可
                # if self._check_consistent_after(i, col_counts):
                #     return i

        return None

    # 如果想更严格地判断，可以再写一个辅助函数检查后续若干行的一致性
    # def _check_consistent_after(self, start_index, col_counts, tolerance=0):
    #     """
    #     判断从 start_index 之后的多行，是否都与 col_counts[start_index] 相同
    #     （或在某个范围内）。
    #     """
    #     base = col_counts[start_index]
    #     # 先只简单看看后面 5 行
    #     for j in range(start_index+1, min(start_index+6, len(col_counts))):
    #         if abs(col_counts[j] - base) > tolerance:
    #             return False
    #     return True

    def _clean_special_symbols_in_columns(self):
        """
        清洗表头中不需要的符号，比如 λ、Σ 等。
        也可以在这里添加更多针对表头的清理逻辑。
        """
        if self.df is None or self.df.empty:
            return

        replace_map = {
            'λ': '_lambda_',
            'Σ': '_sigma_',
            # 需要别的替换可自行补充
        }
        new_columns = []
        for col in self.df.columns:
            for old, new in replace_map.items():
                col = col.replace(old, new)
            new_columns.append(col)
        self.df.columns = new_columns
