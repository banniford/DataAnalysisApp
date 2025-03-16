import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton

class LineManager:
    def __init__(self,ax, y_value):
        self.ax = ax
        self.y_value = y_value
        self.lines = []  # 存储所有折线对象
        self._stable_interval = []  # 稳定区间


    @property
    def stable_interval(self):
        return self._stable_interval
    
    @stable_interval.setter
    def stable_interval(self, value):
        # 设置稳定区间
        self._stable_interval = value
        # 清除所有折线
        self.clear_lines()
        # 重新绘制稳定区间
        if self._stable_interval==[]:
            self.add_line(range(len(self.y_value)), self.y_value, color='red',alpha=0.5)
            return
        for i in self._stable_interval:
            self.add_line(range(i[0],i[1]), self.y_value[i[0]:i[1]], color='red',alpha=0.5)

    

    def add_line(self, x, y, **kwargs):
        """添加一条折线"""
        # if 'label' not in kwargs:  # 如果没有设置标签，则自动生成一个
        #     kwargs['label'] = f"Line {len(self.lines) + 1}"
        line, = self.ax.plot(x, y, **kwargs)
        self.lines.append(line)
        self.ax.figure.canvas.draw_idle()
        return line

    def remove_line(self, line):
        """删除一条折线"""
        if line in self.lines:
            line.remove()
            self.lines.remove(line)
            self.ax.figure.canvas.draw_idle()

    def clear_lines(self):
        """清除所有折线"""
        for line in self.lines:
            line.remove()
        self.lines.clear()
        self.ax.figure.canvas.draw_idle()  

    def update_line(self, line, x, y):
        """更新某条折线的数据"""
        line.set_data(x, y)
        self.ax.relim()  # 重新计算数据范围
        self.ax.autoscale_view()  # 自动调整视图范围
        self.ax.figure.canvas.draw_idle()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建画布
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.setCentralWidget(self.canvas)

        # 初始化折线管理器
        self.line_manager = LineManager(self.ax)

        # 添加按钮
        self.button_add = QPushButton("添加折线")
        self.button_remove = QPushButton("删除最后一条折线")
        self.button_clear = QPushButton("清除所有折线")
        self.button_update = QPushButton("更新第一条折线")

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.button_add)
        layout.addWidget(self.button_remove)
        layout.addWidget(self.button_clear)
        layout.addWidget(self.button_update)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 绑定按钮事件
        self.button_add.clicked.connect(self.add_line)
        self.button_remove.clicked.connect(self.remove_line)
        self.button_clear.clicked.connect(self.clear_lines)
        self.button_update.clicked.connect(self.update_line)

    def add_line(self):
        """添加一条折线"""
        x = np.linspace(0, 10, 100)
        y = np.sin(x + len(self.line_manager.lines) * 2)  # 每条折线的相位不同
        self.line_manager.add_line(x, y, label=f"Line {len(self.line_manager.lines) + 1}")

    def remove_line(self):
        """删除最后一条折线"""
        if self.line_manager.lines:
            self.line_manager.remove_line(self.line_manager.lines[-1])

    def clear_lines(self):
        """清除所有折线"""
        self.line_manager.clear_lines()

    def update_line(self):
        """更新第一条折线的数据"""
        if self.line_manager.lines:
            x = np.linspace(0, 10, 100)
            y = np.cos(x)  # 更新为余弦曲线
            self.line_manager.update_line(self.line_manager.lines[0], x, y)
            self.ax.relim()  # 重新计算数据范围
            self.ax.autoscale_view()  # 自动调整视图范围


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
