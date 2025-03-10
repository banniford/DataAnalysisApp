import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib import font_manager
from matplotlib import rcParams
import mplcursors  # 引入mplcursors库

# 字体加载
font_path = "../assets/font/SourceHanSansSC-Bold.otf"
font_manager.fontManager.addfont(font_path)
prop = font_manager.FontProperties(fname=font_path)

# 字体设置
rcParams['font.sans-serif'] = prop.get_name()  # 根据名称设置字体
rcParams['axes.unicode_minus'] = False  # 使坐标轴刻度标签正常显示正负号

class MyMplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(10, 5), dpi=100)
        super().__init__(self.fig)

        # 创建主坐标轴和右侧坐标轴
        self.ax_left = self.fig.add_subplot(111)
        self.ax_right = self.ax_left.twinx()
        # 强制设置坐标轴层级（重要！）
        # self.ax_left.set_zorder(3)  # 左侧坐标轴在上层
        # self.ax_right.set_zorder(2)
        # self.ax_left.patch.set_visible(False)  # 使左侧坐标轴背景透明

        # 生成示例数据
        self.x = [1, 2, 3, 4, 5]
        self.y1 = [1, 4, 9, 16, 25]  # 左侧Y轴数据
        self.y2 = [1, 2, 3, 4, 5]    # 右侧Y轴数据
        
        # 在绘制曲线时添加zorder和picker参数
        self.line1, = self.ax_left.plot(
            self.x, self.y1, 
            'b-', label='y = x²', 
            picker=True  # 扩大点击检测范围
        )
        self.line2, = self.ax_right.plot(
            self.x, self.y2, 
            'r-', label='y = x', 
            picker=True
        )



        # 设置坐标轴样式
        self.ax_left.set_xlabel('X轴')
        self.ax_left.set_ylabel('左侧Y轴（平方）', color='b')
        self.ax_right.set_ylabel('右侧Y轴（线性）', color='r')
        
        # 设置刻度颜色匹配曲线
        self.ax_left.tick_params(axis='y', colors='b')
        self.ax_right.tick_params(axis='y', colors='r')

        # 合并图例
        lines = [self.line1, self.line2]
        self.ax_left.legend(
            lines, 
            [line.get_label() for line in lines],
            loc='upper left'
        )

        # 绑定pick事件
        # self.mpl_connect('pick_event', self.on_pick)
        self.mpl_connect('button_press_event', self.button_press_event)

    def button_press_event(self, event):
        if event.inaxes is not None:
            for line in [self.line1, self.line2]:
                contains, _ = line.contains(event)
                if contains:
                    print(f"点击曲线: {line.get_label()}")
                    # 切换线宽（点击后加粗/恢复）
                    current_lw = line.get_linewidth()
                    new_lw = 3 if current_lw < 3 else 1.5
                    line.set_linewidth(new_lw)
                    self.draw_idle()
                    break

    def on_pick(self, event):
        artist = event.artist
        print(f"点击对象: {artist}")
        if isinstance(artist, plt.Line2D):
            print(f"点击曲线: {artist.get_label()}")
            # 切换线宽（点击后加粗/恢复）
            current_lw = artist.get_linewidth()
            new_lw = 3 if current_lw < 3 else 1.5
            artist.set_linewidth(new_lw)
            self.draw()

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('双Y轴示例')
        self.setGeometry(100, 100, 800, 600)

        # 创建画布并设置布局
        self.canvas = MyMplCanvas()
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec())
