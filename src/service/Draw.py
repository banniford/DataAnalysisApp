from ui.mplcanvas import MplWidget
import mplcursors  # 引入mplcursors库
from matplotlib.widgets import Cursor, Slider
from PyQt6.QtWidgets import QMainWindow
from service.ReferenceLineManager import ReferenceLineManager
from service.LineManager import LineManager

class Draw:
    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window
        self.main_ui = main_window.main_ui
        
        # 获取 MplWidget 对象
        self.mpl_widget = self.main_window.findChild(MplWidget, "mplWidget")  # "mplWidget" 是你在 Qt Designer 中设置的 objectName
        # 访问 canvas 属性并绘图
        self.canvas = self.mpl_widget.canvas
        self.reference_line_manager = ReferenceLineManager(self.canvas.ax)
        self.line_manager = {}
        # 添加交互光标
        cursor = Cursor(self.canvas.ax, useblit=False, color='blue', linewidth=1, horizOn=False, vertOn=True) 
        # 添加滑块
        self.slider = self.add_threshold_slider(self.main_ui.doubleSpinBox_2.value(),self.main_ui.doubleSpinBox_3.value()) 
        # 绑定事件
        self.slider.on_changed(lambda val: self.update_jumps())
        # 更新阈值
        self.main_ui.doubleSpinBox_2.valueChanged.connect(self.update_slider_threshold)
        self.main_ui.doubleSpinBox_3.valueChanged.connect(self.update_slider_threshold)
        # 添加表头
        self.canvas.ax.set_title("数据分析(点击拖动参考线，按D删除，按C清空，按A添加)")
        self.canvas.ax.set_xlabel("数据点位/ΔT(ms)")
        self.canvas.ax.set_ylabel("数值")
        
    def create_line_manager(self, name):
        """创建折线管理器"""
        if name not in self.line_manager:
            self.line_manager[name] = LineManager(self.canvas.ax)
        return self.line_manager[name]
    
    def add_threshold_slider(self, initial_threshold,max_threshold):
        """添加阈值调整滑块"""
        ax_slider = self.canvas.fig.add_axes([0.2, 0.01, 0.6, 0.02], facecolor='lightgoldenrodyellow')
        slider = Slider(ax_slider, '突变识别阈值', 0.0, max_threshold, valinit=initial_threshold)
        return slider
    
    def update_slider_threshold(self):
        """更新阈值"""
        # 删除滑块
        self.canvas.fig.delaxes(self.slider.ax)
        # 添加
        initial_threshold = self.main_ui.doubleSpinBox_2.value()
        max_threshold = self.main_ui.doubleSpinBox_3.value()
        self.slider = self.add_threshold_slider(initial_threshold,max_threshold)
        self.slider.on_changed(self.update_jumps)
    
    def update_jumps(self):
        """根据新阈值更新突变点和参考线"""
        print("update_jumps")
        pass

    def draw_scatter(self,x ,y ,color='red', linestyle='--', alpha=0.8, picker=5):
        scatter= self.canvas.ax.scatter(x, y, color=color, linestyle=linestyle, alpha=alpha, picker=picker)
        # 添加鼠标悬停显示数据点数值的功能
        mplcursors.cursor(scatter, hover=True).connect(
            "add", lambda sel: sel.annotation.set_text(f"({sel.target[0]:.0f}, {sel.target[1]:.6f})")
        )
        self.canvas.draw_idle()
    
    