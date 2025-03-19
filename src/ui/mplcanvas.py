# mpl_canvas.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib import font_manager,rcParams
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_agg import FigureCanvasAgg

# 字体加载
font_path = "../assets/font/SourceHanSansSC-Bold.otf"
font_manager.fontManager.addfont(font_path)
prop = font_manager.FontProperties(fname=font_path)

# 字体设置
rcParams['font.sans-serif'] = prop.get_name()  # 根据名称设置字体
rcParams['axes.unicode_minus'] = False  # 使坐标轴刻度标签正常显示正负号

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

    def _set_performance_options(self):
        """设置Matplotlib性能优化参数"""
        plt.rcParams['path.simplify'] = True        # 启用路径简化
        plt.rcParams['path.simplify_threshold'] = 0.3  # 简化阈值
        plt.rcParams['agg.path.chunksize'] = 15000  # 大块数据处理
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
