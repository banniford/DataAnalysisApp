import pandas as pd
import numpy as np

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
    
