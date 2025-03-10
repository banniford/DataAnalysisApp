import pandas as pd
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

class DataAnalysis:
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_ui = main_window.main_ui
        self.df = None
    
    def set_table_data(self, df):
        self.df = df

    def get_table_header(self):
        # 获取表头, 去除名为 Time [s] 的列
        table_header = self.df.columns.tolist()
        if 'Time [s]' in table_header:
            table_header.remove('Time [s]')
        return table_header
    
    def get_table_num(self):
        # 获取表格行数
        return len(self.df)
    
    def get_var_value(self, var_name):
        # 获取变量值
        return self.df[var_name].values
    
    
    def detect_jumps(self, key , window, threshold):
        """优化后的突变点检测算法"""
        # 使用numpy的滑动窗口函数
        values = self.df[key].values
        windows = sliding_window_view(values, window)
        
        # 计算每个窗口的标准差
        stds = np.std(windows, axis=1)

        # 检测突变点（标准差超过阈值）
        jumps = np.where(stds > threshold)[0]

        # 去除连续点，只保留突变起始点
        clean_jumps = [jumps[0]]
        for i in range(1, len(jumps)):
            if jumps[i] - jumps[i - 1] > window:
                clean_jumps.append(jumps[i])
        
        return clean_jumps
    
    
