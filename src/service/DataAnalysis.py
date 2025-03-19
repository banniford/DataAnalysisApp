# 用于数据分析的类 DataAnalysis.py
import pandas as pd
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

class DataAnalysis:
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_ui = main_window.main_ui
        self.df = None
        self._data_avg = {}
        self._data_max_min = {}
        self._stable_interval = {}
    
    @property
    def data_avg(self):
        return self._data_avg

    @property
    def data_max_min(self):
        return self._data_max_min
    
    @property
    def stable_interval(self):
        return self._stable_interval
    
    def set_stable_interval(self, name, stable_interval):
        self._stable_interval[name] = stable_interval
        return self._stable_interval[name]

    def set_table_data(self, df):
        self.df = df

    def get_table_header(self)->list:
        # 获取表头
        table_header = self.df.columns.tolist()
        return table_header
    
    def get_table_num(self)->int:
        # 获取表格行数
        return len(self.df)
    
    def get_table_columns(self)->int:
        # 获取表格列数
        return len(self.df.columns)
    
    def get_var_value(self, var_name):
        # 获取变量值
        return self.df[var_name].values
    
    def cal_avg(self,master_var, var_name):
        # 计算平均值
        if not self.stable_interval[master_var]:
            self.data_avg[var_name] = [self.df[var_name].mean()]
            return
        
        self.data_avg[var_name] = []
        for interval in self.stable_interval[master_var]:
            avg = self.df[var_name][interval[0]:interval[1]].mean()
            self.data_avg[var_name].append(avg)
    
    def cal_max_min(self, master_var,var_name):
        # 计算最大最小值以及对应的索引
        if not self.stable_interval[master_var]:
            self.data_max_min[var_name] = [[self.df[var_name].max(), self.df[var_name].idxmax() ,self.df[var_name].min(),self.df[var_name].idxmin() ]]
            return
        self.data_max_min[var_name] = []
        for interval in self.stable_interval[master_var]:
            max_value = self.df[var_name][interval[0]:interval[1]].max()
            max_value_index = self.df[var_name][interval[0]:interval[1]].idxmax()
            min_value = self.df[var_name][interval[0]:interval[1]].min()
            min_value_index = self.df[var_name][interval[0]:interval[1]].idxmin()
            self.data_max_min[var_name].append((max_value,
                                                max_value_index,
                                                min_value,
                                                min_value_index))
        
        
    def detect_jumps(self, key , window, threshold):
        """优化后的突变点检测算法"""
        # 使用numpy的滑动窗口函数
        values = self.df[key].values
        windows = sliding_window_view(values, window)
        
        # 计算每个窗口的标准差
        stds = np.std(windows, axis=1)

        # 检测突变点（标准差超过阈值）
        jumps = np.where(stds > threshold)[0]

        if len(jumps) == 0:
            return []
        
        # 去除连续点，只保留突变起始点
        clean_jumps = [jumps[0]]
        for i in range(1, len(jumps)):
            if jumps[i] - jumps[i - 1] > window:
                clean_jumps.append(jumps[i])
        
        return clean_jumps
    
    
    def pandas_detect_jumps(self, key , window, threshold):
        """检测突变点位置"""
        # 计算滑动窗口内的标准差
        rolling_std = self.df[key].rolling(window).std()

        # 检测突变点（标准差超过阈值）
        jumps = self.df.index[rolling_std > threshold].tolist()

        if len(jumps) == 0:
            return []
        
        # 去除连续点，只保留突变起始点
        clean_jumps = [jumps[0]]
        for i in range(1, len(jumps)):
            if jumps[i] - jumps[i - 1] > window:
                clean_jumps.append(jumps[i])

        return clean_jumps