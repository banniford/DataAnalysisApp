

class LineManager:
    def __init__(self,label, ax, y_value,color):
        self.label = label
        self.ax = ax
        self.y_value = y_value
        self.lines = []  # 存储所有折线对象
        self._stable_interval = []  # 稳定区间
        self.color = color


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
            self.add_line(range(len(self.y_value)), self.y_value, color=self.color,linewidth=1)
            return
        for i in self._stable_interval:
            self.add_line(range(i[0],i[1]), self.y_value[i[0]:i[1]], color=self.color,linewidth=1)

    

    def add_line(self, x, y, **kwargs):
        """添加一条折线"""
        # if 'label' not in kwargs:  # 如果没有设置标签，则自动生成一个
        #     kwargs['label'] = f"Line {len(self.lines) + 1}"
        if len(self.lines) <= 1:
            line, = self.ax.plot(x, y, label = self.label,**kwargs)
        else:
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

