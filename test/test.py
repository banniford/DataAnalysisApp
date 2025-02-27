import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
# fname 为 你下载的字体库路径，注意 SourceHanSansSC-Bold.otf 字体的路径
Zhfont = matplotlib.font_manager.FontProperties(fname="../assets/font/SourceHanSansSC-Bold.otf") 
 

import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

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
        self.ax.figure.canvas.draw()
    
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
        self.ax.figure.canvas.draw()
    
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
            self.ax.figure.canvas.draw()
        elif event.key == 'a':
            # 添加新参考线
            self.add_line(event.xdata)

# ======================
# 4. 主程序
# ======================
if __name__ == "__main__":
    # 生成数据
    df = generate_data()
    
    # 检测突变点
    jumps = detect_jumps(df)
    
    # 创建图表,设置字体
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.plot(df.index, df['value'], color='gray', alpha=0.8, label='原始数据')
    
    # 初始化参考线管理器
    line_manager = ReferenceLineManager(ax, df, jumps)
    
    # 添加交互光标
    cursor = Cursor(ax, useblit=True, color='blue', linewidth=1, horizOn=False, vertOn=True)
    
    # 图表样式
    ax.set_title("突变点检测与参考线编辑 (点击拖动参考线，按D删除，按A添加)",fontproperties=Zhfont)
    ax.set_xlabel("数据点位",fontproperties=Zhfont)
    ax.set_ylabel("数值",fontproperties=Zhfont)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()
