import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor, Slider
from numpy.lib.stride_tricks import sliding_window_view
from matplotlib import font_manager
from matplotlib import rcParams

# 字体加载
font_path = "../assets/font/simhei.ttf"
font_manager.fontManager.addfont(font_path)
prop = font_manager.FontProperties(fname=font_path)

# 字体设置
# rcParams['font.family'] = 'sans-serif' # 使用字体中的无衬线体
rcParams['font.sans-serif'] = prop.get_name()  # 根据名称设置字体
rcParams['axes.unicode_minus'] = False # 使坐标轴刻度标签正常显示正负号

# ======================
# 1. 生成模拟数据
# ======================
def generate_data(total_points=20000, chunk_size=1000):
    """生成包含稳定区间和突变点的模拟数据"""
    np.random.seed(42)
    data = []
    current_value = 0.5
    
    for i in range(total_points // chunk_size):
        # 稳定区间（轻微波动）
        stable = current_value + 0.1 * np.random.randn(chunk_size - 20)
        
        # 突变区间（快速上升）
        rise = np.linspace(current_value, current_value + 1, 20)
        
        # 更新当前值
        current_value += 1
        data.extend(np.concatenate([stable, rise]))
    
    return pd.DataFrame({'value': data})

# ======================
# 2. 突变点检测算法
# ======================
def detect_jumps(df, window=50, threshold=0.3):
    """检测突变点位置"""
    # 计算滑动窗口内的标准差
    rolling_std = df['value'].rolling(window).std()
    
    # 检测突变点（标准差超过阈值）
    jumps = df.index[rolling_std > threshold].tolist()
    
    # 去除连续点，只保留突变起始点
    clean_jumps = [jumps[0]]
    for i in range(1, len(jumps)):
        if jumps[i] - jumps[i-1] > window:
            clean_jumps.append(jumps[i])
    
    return clean_jumps

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
        result_points.append(closest_index)
    
    return np.array(result_points)

# ======================
# 3. 交互式参考线管理
# ======================
class ReferenceLineManager:
    def __init__(self, ax, df, initial_jumps):
        self.ax = ax
        self.df = df
        self.lines = []
        self.current_line = None
        
        # 初始化参考线
        for pos in initial_jumps:
            self.add_line(pos)
        
        # 绑定事件
        self.cid_press = ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = ax.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = ax.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cid_key = ax.figure.canvas.mpl_connect('key_press_event', self.on_key)
    
    def add_line(self, xpos):
        """添加一条参考线"""
        line = self.ax.axvline(x=xpos, color='red', linestyle='--', alpha=0.8, picker=5)
        self.lines.append(line)
        self.ax.figure.canvas.draw_idle()  # 仅更新需要修改的部分
    
    def on_press(self, event):
        """鼠标按下事件"""
        if event.inaxes != self.ax:
            return
        
        # 检查是否点击了某条线
        if event.button == 1:  # 左键
            for line in self.lines:
                if line.contains(event)[0]:
                    self.current_line = line
                    break
    
    def on_motion(self, event):
        """鼠标移动事件"""
        if self.current_line is None or event.inaxes != self.ax:
            return
        
        # 移动参考线
        self.current_line.set_xdata([event.xdata, event.xdata])
        self.ax.figure.canvas.draw_idle()  # 仅更新需要修改的部分
    
    def on_release(self, event):
        """鼠标释放事件"""
        self.current_line = None
    
    def on_key(self, event):
        """键盘事件"""
        if event.key == 'd' and self.current_line is not None:
            # 删除当前选中的参考线
            self.current_line.remove()
            self.lines.remove(self.current_line)
            self.current_line = None
            self.ax.figure.canvas.draw_idle()
        elif event.key == 'a':
            # 添加新参考线
            self.add_line(event.xdata)
        elif event.key == 'c':
            # 删除所有参考线
            for line in self.lines:
                line.remove()
            self.lines.clear()
            self.ax.figure.canvas.draw_idle()
        elif event.key == 's':
            # 保存参考线位置
            save_reference_lines(self)

# ======================
# 4. 保存参考线位置
# ======================
def save_reference_lines(line_manager, filename="reference_lines.csv"):
    """保存参考线位置到文件"""
    positions = [line.get_xdata()[0] for line in line_manager.lines]
    pd.DataFrame({"position": positions}).to_csv(filename, index=False)
    print(f"参考线位置已保存到 {filename}")

# ======================
# 5. 动态调整阈值
# ======================
def add_threshold_slider(ax, initial_threshold=0.3):
    """添加阈值调整滑块"""
    ax_slider = plt.axes([0.2, 0.02, 0.6, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, '阈值', 0.1, 1.0, valinit=initial_threshold)
    return slider

def update_jumps(val, df, line_manager):
    """根据新阈值更新突变点和参考线"""
    # 删除所有现有参考线
    for line in line_manager.lines:
        line.remove()
    line_manager.lines.clear()
    
    # 重新检测突变点
    jumps = detect_jumps(df, threshold=val)
    for pos in jumps:
        line_manager.add_line(pos)

# ======================
# 6. 主程序
# ======================
if __name__ == "__main__":
    # 生成数据
    df = generate_data()
    
    # 检测突变点
    jumps = detect_jumps(df)
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.plot(df.index, df['value'], color='gray', alpha=0.8, label='原始数据',marker='o',markerfacecolor='red',markersize=3)
    
    # 初始化参考线管理器
    line_manager = ReferenceLineManager(ax, df, jumps)
    
    # 添加交互光标
    cursor = Cursor(ax, useblit=True, color='blue', linewidth=1, horizOn=False, vertOn=True)
    
    # 添加阈值调整滑块
    slider = add_threshold_slider(plt.gca())
    slider.on_changed(lambda val: update_jumps(val, df, line_manager))
    # 图表样式
    ax.set_title("突变点检测与参考线编辑 (点击拖动参考线，按D删除，按C清空，按A添加，按S保存)")
    ax.set_xlabel("数据点位")
    ax.set_ylabel("数值")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()
