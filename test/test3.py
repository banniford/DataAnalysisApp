import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import matplotlib
def detect_jump_intervals_diff(values, threshold=1.0):
    """基于差分的方法检测突变区间"""
    diff = np.diff(values)
    jump_indices = np.where(np.abs(diff) > threshold)[0]
    
    # 合并连续区间
    if len(jump_indices) == 0:
        return np.array([])
    
    diff_jump = np.diff(jump_indices)
    breaks = np.where(diff_jump != 1)[0] + 1
    intervals = np.split(jump_indices, breaks)
    
    # 在每个突变区间内找到 90% 位置的点
    result_points = []
    for interval in intervals:
        if len(interval) == 0:
            continue
        start = interval[0]
        end = interval[-1] + 1  # 结束位置需要加 1
        target_index = start + int(0.9 * (end - start))
        closest_index = np.argmin(np.abs(np.arange(start, end) - target_index))
        result_points.append({target_index: closest_index})
    
    return np.array(result_points)

# 示例数据
values = np.array([1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 9,9,9,9,9,9,9,8,7,6,5,1,1,1,1,1])
jump_points = detect_jump_intervals_diff(values, threshold=0.5)
print("突变区间内 90% 位置的点:", jump_points)
