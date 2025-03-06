import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建画布
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.setCentralWidget(self.canvas)

        # 添加按钮
        self.button_draw = QPushButton("立即刷新画布 (draw)")
        self.button_draw_idle = QPushButton("异步刷新画布 (draw_idle)")

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.button_draw)
        layout.addWidget(self.button_draw_idle)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 绑定按钮事件
        self.button_draw.clicked.connect(self.update_plot_draw)
        self.button_draw_idle.clicked.connect(self.update_plot_draw_idle)

    def update_plot_draw(self):
        """立即刷新画布"""
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        self.ax.clear()
        self.ax.plot(x, y)
        self.ax.figure.canvas.draw()  # 立即刷新画布

    def update_plot_draw_idle(self):
        """异步刷新画布"""
        x = np.linspace(0, 10, 100)
        y = np.cos(x)
        self.ax.clear()
        self.ax.plot(x, y)
        self.ax.figure.canvas.draw_idle()  # 异步刷新画布


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
