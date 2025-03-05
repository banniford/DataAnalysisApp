# mpl_canvas.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib import font_manager,rcParams
import mplcursors  # 引入mplcursors库

# 字体加载
font_path = "../assets/font/SourceHanSansSC-Bold.otf"
font_manager.fontManager.addfont(font_path)
prop = font_manager.FontProperties(fname=font_path)

# 字体设置
rcParams['font.sans-serif'] = prop.get_name()  # 根据名称设置字体
rcParams['axes.unicode_minus'] = False  # 使坐标轴刻度标签正常显示正负号

from service.ReferenceLineManager import ReferenceLineManager

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=10, height=5, dpi=100):
        self.fig,self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.line_manager = ReferenceLineManager(self.ax)
    


class MplWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = MplCanvas(self)
        self.set_Layout()
    
    def set_Layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)