# mpl_canvas.py
import sys
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams
from PyQt6.QtCore import Qt
import numpy as np

# 获取打包或开发模式下的资源路径
def resource_path(relative_path):
    """获取资源文件的路径，兼容 PyInstaller 和源码运行"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时路径
        base_path = sys._MEIPASS
    else:
        # 源码运行时获取项目根路径（src 上一级）
        base_path = os.path.dirname(os.path.abspath(__file__))  # 当前文件 src/ui/mplcanvas.py
        base_path = os.path.abspath(os.path.join(base_path, "..", ".."))  # 回到项目根

    return os.path.join(base_path, relative_path)

# 字体加载
font_path = resource_path("assets/font/SourceHanSansSC-Bold.otf")
font_manager.fontManager.addfont(font_path)
prop = font_manager.FontProperties(fname=font_path)

# 字体设置
rcParams['font.sans-serif'] = prop.get_name()  # 设置字体
rcParams['axes.unicode_minus'] = False         # 正负号正常显示

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=10, height=5, dpi=100):
        self.fig, self.ax_left = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax_right = self.ax_left.twinx()
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        
        # 设置性能优化参数
        self._set_performance_options()
        self._add_text_watermark()  # ✅ 添加水印

    def _add_text_watermark(self):
        """在背景添加平铺文字水印"""
        text = "intertek"
        fontsize = 20  # 减小字体大小以便排列
        alpha = 0.15
        rotation = 30

        # 设置水印的网格参数
        x_step = 0.3  # 横向步长（根据画布宽度调整）
        y_step = 0.15  # 纵向步长（考虑旋转后的覆盖）
        
        # 生成覆盖整个画布及外延的坐标（-0.5到1.5确保边缘覆盖）
        x_positions = np.arange(-0.5, 1.5, x_step)
        y_positions = np.arange(-0.5, 1.5, y_step)

        for row, y in enumerate(y_positions):
            for col, x in enumerate(x_positions):
                # 奇數行横向偏移半個步长，实现交错排列
                if row % 2 == 1:
                    adjusted_x = x + x_step / 2
                else:
                    adjusted_x = x
                self.fig.text(
                    adjusted_x, y, text,
                    fontsize=fontsize,
                    color='gray',
                    ha='center',
                    va='center',
                    alpha=alpha,
                    rotation=rotation,
                    zorder=0
                )

    def _set_performance_options(self):
        """设置Matplotlib性能优化参数"""
        plt.rcParams['path.simplify'] = True        # 启用路径简化
        plt.rcParams['path.simplify_threshold'] = 0.3  # 简化阈值
        plt.rcParams['agg.path.chunksize'] = 30000  # 大块数据处理
        plt.rcParams['figure.facecolor'] = 'white'  # 禁用透明背景
        plt.rcParams['axes.facecolor'] = 'white'    # 禁用透明背景
        self.figure.set_tight_layout(True)           # 减少布局计算

class MplWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = MplCanvas(self)
        
        # ---- 新增：创建工具栏 ----
        self.toolbar = NavigationToolbar(self.canvas, self)
        self._set_layout()
 
    def _set_layout(self):
        layout = QVBoxLayout()
        # 先加 toolbar，再加 canvas
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
