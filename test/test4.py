import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

class MyMplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)

        # 生成一些示例数据
        self.x = [1, 2, 3, 4, 5]
        self.y1 = [1, 4, 9, 16, 25]
        self.y2 = [1, 2, 3, 4, 5]
        
        # 绘制两条曲线，并设置pickable为True
        self.line1, = self.ax.plot(self.x, self.y1, label='y = x^2', picker=True)
        self.line2, = self.ax.plot(self.x, self.y2, label='y = x', picker=True)
        
        self.ax.legend()

        # 绑定pick事件
        self.mpl_connect('pick_event', self.on_pick)

    def on_pick(self, event):
        # 检测被点击的对象
        artist = event.artist
        if isinstance(artist, plt.Line2D):
            print(f"你点击了曲线: {artist.get_label()}")
            artist.set_linewidth(3)  # 改变被点击曲线的线宽
            self.draw()  # 重绘图形

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Matplotlib 和 PyQt 集成')

        # 创建MplCanvas实例
        self.canvas = MyMplCanvas()

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        # 设置主窗口的中心部件
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.show()

# 运行PyQt应用
app = QApplication(sys.argv)
window = MyMainWindow()
sys.exit(app.exec())
