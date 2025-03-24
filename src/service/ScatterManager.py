import mplcursors  # 引入mplcursors库

class ScatterManager:
    def __init__(self, ax, y_value, color='gray'):
        self.ax = ax
        self.y_value = y_value
        self._color = color
        self.scatter = None
        self.draw_scatter()
        self._visible = True

    @property
    def visible(self):
        return self._visible
    
    @visible.setter
    def visible(self, value):
        if value == self._visible:
            return
        self._visible = value
        if self._visible:
            self.scatter.set_visible(True)
        else:
            self.scatter.set_visible(False)

    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, value):
        if value == self._color:
            return
        self._color = value
        self.clear_scatter()
        self.draw_scatter()

    def draw_scatter(self, linestyle='--',linewidth=1, alpha=0.3, picker=5):
        self.scatter=self.ax.scatter(range(len(self.y_value)), 
                        self.y_value,
                        color=self.color, 
                        linestyle=linestyle, 
                        linewidth=linewidth,
                        alpha=alpha, 
                        picker=picker,
                        edgecolors='none',  # 关闭边缘
                        rasterized=True     # 启用栅格化
                        )
        # 添加鼠标悬停显示数据点数值的功能
        mplcursors.cursor(self.scatter, hover=2).connect(
            "add", lambda sel: sel.annotation.set_text(
                f"({int(sel.target[0])}, {sel.target[1]:.2f})"
            )
        )
        # 更新图例
        self.ax.figure.canvas.draw_idle()

    def clear_scatter(self):
        if self.scatter:
            self.scatter.remove()
            self.ax.figure.canvas.draw_idle()