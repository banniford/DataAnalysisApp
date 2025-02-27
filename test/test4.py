import numpy as np

def detect_jump_intervals_moving_avg(values, window=5, threshold=1.0):
    """
    基于移动平均的方法检测突变区间，并在每个区间内找到 90% 位置的点。
    
    参数:
        values (np.array): 输入数据。
        window (int): 移动平均的窗口大小。
        threshold (float): 偏差阈值，用于判断是否为突变点。
    
    返回:
        np.array: 每个突变区间内 90% 位置的点。
    """
    if len(values) < window:
        return np.array([])
    
    # 计算移动平均值
    moving_avg = np.convolve(values, np.ones(window)/window, mode='valid')
    
    # 计算每个点与移动平均值的偏差
    deviations = np.abs(values[window-1:] - moving_avg)
    
    # 找到偏差超过阈值的点
    jump_indices = np.where(deviations > threshold)[0] + window - 1
    
    # 合并连续的突变点形成突变区间
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
        # 突变区间的起始和结束位置
        start = interval[0]
        end = interval[-1] + 1  # 结束位置需要加 1
        # 计算 90% 位置的点
        target_index = start + int(0.9 * (end - start))
        # 找到最接近目标点的点
        closest_index = np.argmin(np.abs(np.arange(start, end) - target_index))
        result_points.append(closest_index)
    
    return np.array(result_points)

# 示例数据
values = np.array([
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 平稳段
    2, 3, 4, 5, 6, 7, 8, 9, 10, 11,  # 突变段（上升）
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 平稳段
    10, 9, 8, 7, 6, 5, 4, 3, 2, 1,  # 突变段（下降）
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1   # 平稳段
])

# 运行函数
jump_points = detect_jump_intervals_moving_avg(values, window=5, threshold=1.0)
print("突变区间内 90% 位置的点:", jump_points)
