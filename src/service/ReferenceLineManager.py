import matplotlib.pyplot as plt
class ReferenceLineManager:
    def __init__(self, ax: plt.Axes):
        self.ax = ax
        self.t_lines = []
        self.ft_lines = []
        self.bt_lines = []
        self.current_line = None

        # 绑定事件
        self.cid_press = ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = ax.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = ax.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cid_key = ax.figure.canvas.mpl_connect('key_press_event', self.on_key)
    
    def add_line(self, pos , xpos, color='red', linestyle='--', alpha=0.8, picker=5):
        """添加一条参考线"""
        if pos == 't':
            line = self.ax.axvline(x=xpos, color=color, linestyle=linestyle, alpha=alpha, picker=picker)
            self.t_lines.append(line)
        elif pos == 'ft':
            line = self.ax.axvline(x=xpos, color=color, linestyle=linestyle, alpha=alpha)
            self.ft_lines.append(line)
        elif pos == 'bt':
            line = self.ax.axvline(x=xpos, color=color, linestyle=linestyle, alpha=alpha)
            self.bt_lines.append(line)
        self.ax.figure.canvas.draw_idle()  # 仅更新需要修改的部分
    
    def on_press(self, event):
        """鼠标按下事件"""
        if event.inaxes != self.ax:
            return
        
        # 检查是否点击了某条线
        if event.button == 1:  # 左键
            for line in self.t_lines:
                if line.contains(event)[0]:
                    self.current_line = line
                    break
    
    def on_motion(self, event):
        """鼠标移动事件"""
        if self.current_line is None or event.inaxes != self.ax:
            return
        
        # 移动参考线
        self.current_line.set_xdata([event.xdata, event.xdata])
        self.ax.figure.canvas.draw_idle()  # 仅更新需要修改的部分
    
    def on_release(self, event):
        """鼠标释放事件"""
        self.current_line = None
    
    def on_key(self, event):
        """键盘事件"""
        if event.key == 'd' and self.current_line is not None:
            # 删除当前选中的参考线
            self.current_line.remove()
            self.t_lines.remove(self.current_line)
            self.current_line = None
            self.ax.figure.canvas.draw_idle()
        elif event.key == 'a':
            # 添加新参考线
            self.add_line('t', event.xdata)
        elif event.key == 'c':
            # 删除所有参考线
            for line in self.t_lines:
                line.remove()
            self.t_lines.clear()
            for line in self.ft_lines:
                line.remove()
            self.ft_lines.clear()
            for line in self.bt_lines:
                line.remove()
            self.bt_lines.clear()
            self.ax.figure.canvas.draw_idle()

    def clear_lines(self):
        for line in self.t_lines:
            line.remove()
        self.t_lines.clear()
        for line in self.ft_lines:
            line.remove()
        self.ft_lines.clear()
        for line in self.bt_lines:
            line.remove()
        self.bt_lines.clear()
        self.ax.figure.canvas.draw_idle()