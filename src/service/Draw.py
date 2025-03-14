from ui.mplcanvas import MplWidget
import mplcursors  # 引入mplcursors库
from matplotlib.widgets import Slider
from PyQt6.QtWidgets import QMainWindow
from service.ReferenceLineManager import ReferenceLineManager
from service.LineManager import LineManager
from matplotlib.ticker import FuncFormatter

class Draw:
    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window
        self.main_ui = main_window.main_ui
        
        # 获取 MplWidget 对象
        self.mpl_widget = self.main_window.findChild(MplWidget, "mplWidget")  # "mplWidget" 是你在 Qt Designer 中设置的 objectName
        # 访问 canvas 属性并绘图
        self.canvas = self.mpl_widget.canvas
        self.reference_line_manager = {}
        self.line_manager = {}
        self.scatter_manager = {}
        # 添加滑块
        self.slider = self.add_threshold_slider(self.main_ui.doubleSpinBox_2.value(),self.main_ui.doubleSpinBox_3.value()) 
        # 绑定事件
        self.slider.on_changed(lambda val: self.update_jumps())
        # 更新阈值
        self.main_ui.doubleSpinBox_2.valueChanged.connect(self.update_slider_threshold)
        self.main_ui.doubleSpinBox_3.valueChanged.connect(self.update_slider_threshold)
        # 添加表头
        self.canvas.ax_left.set_title("数据分析(点击拖动参考线，按D删除，按C清空，按A添加)")
        self.canvas.ax_left.set_xlabel("数据点位/ΔT(ms)")
        self.canvas.ax_left.set_ylabel("数值")
        # 左侧坐标轴在最上层
        self.canvas.ax_left.set_zorder(1)
        # Matplotlib 自动计算比较合适的边距和间隔。
        self.canvas.fig.tight_layout()
        
    def create_line_manager(self, name)->LineManager:
        """创建折线管理器"""
        if name not in self.line_manager:
            self.line_manager[name] = LineManager(self.canvas.ax_left)
        return self.line_manager[name]
    
    def create_reference_line_manager(self, name)->ReferenceLineManager:
        """创建参考线管理器"""
        if name not in self.reference_line_manager:
            self.reference_line_manager[name] = ReferenceLineManager(self.canvas.ax_left)
        return self.reference_line_manager[name]
    
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
        
    def draw_reference_line(self, name, jumps):
        """绘制参考线"""
        # 创建参考线管理器
        reference_line_manager = self.create_reference_line_manager(name)
        # 绘制参考线
        for pos in jumps:
            reference_line_manager.add_line('t',pos)

    def clear_reference_line(self, name):
        """清除参考线"""
        reference_line_manager = self.reference_line_manager.get(name)
        if reference_line_manager:
            reference_line_manager.clear_lines()
    
    def update_jumps(self):
        """根据新阈值更新突变点和参考线"""
        for name, reference_line_manager in self.reference_line_manager.items():
            # 删除所有现有参考线
            reference_line_manager.clear_lines()
            # 重新检测突变点
            jumps = self.main_window.data_analysis.detect_jumps(name, 50, self.slider.val)
            self.draw_reference_line(name,jumps)
        self.canvas.draw_idle()
        pass

    def draw_scatter(self, label, x ,y ,color='gray', linestyle='--', alpha=0.5, picker=5):
        if label in self.scatter_manager:
            return 
        scatter= self.canvas.ax_left.scatter(x, y, label = label,color=color, linestyle=linestyle, alpha=alpha, picker=picker)
        # 添加鼠标悬停显示数据点数值的功能
        mplcursors.cursor(scatter, hover=True).connect(
            "add", lambda sel: sel.annotation.set_text(f"({sel.target[0]:.0f}, {sel.target[1]:.6f})")
        )
        # 更新图例
        self.canvas.ax_left.legend()
        # 添加到管理器
        self.scatter_manager[label] = scatter
        self.canvas.draw_idle()

    def clear_scatter(self, label):
        scatter = self.scatter_manager.get(label)
        if scatter:
            scatter.remove()
            self.scatter_manager.pop(label)
            # 更新图例
            self.canvas.ax_left.legend()
            self.canvas.draw_idle()

    def update_left_ylim(self, y):
        self.canvas.ax_left.set_ylim(min(y), max(y))
        self.canvas.draw_idle()

    def update_right_ylim(self, y):
        self.canvas.ax_right.set_ylim(min(y), max(y))
        self.canvas.draw_idle()


    def update_x_formatter(self, formatterFunc):
        """更新 x 轴格式"""
        self.canvas.ax_left.xaxis.set_major_formatter(FuncFormatter(formatterFunc))
        self.canvas.draw_idle()
    
    