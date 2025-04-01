import mplcursors
from matplotlib.backend_bases import PickEvent, KeyEvent
from dataclasses import dataclass
from typing import List, Tuple, Optional
import random

@dataclass
class LineInfo:
    """存储线条相关信息的dataclass
    
    Attributes:
        line: 直线对象
        text: 斜率文本对象
        indices: 点的原始索引元组(i1, i2)
    """
    line: object
    text: object
    indices: Tuple[int, int]

class ScatterManager:
    """管理散点图及其交互功能的类
    
    功能包括：
    - 散点图的绘制、显示/隐藏、颜色更改
    - 两点间斜率线的绘制和删除
    - 鼠标悬停显示点信息
    - 坐标轴格式切换时的自动更新
    
    Args:
        label: 数据标签，用于显示在斜率文本中
        ax: matplotlib的Axes对象
        y_value: y轴数据值列表
        color: 初始颜色，默认为灰色
        delt_T: x轴缩放因子，默认为1
    """
    
    def __init__(self, label: str, ax, y_value: List[float], 
                 color: str = 'gray', delt_T: float = 1):
        """初始化散点管理器"""
        self.label = label
        self.ax = ax
        self.y_value = y_value
        self._color = color
        self._delt_T = delt_T  # x轴索引到实际值的转换因子
        self.scatter = None     # 散点图对象
        self.lines = []        # 存储所有LineInfo对象的列表
        self.selected_points = []  # 临时存储选中的点索引
        self.selected_line = None  # 当前选中的直线对象
        self._visible = True    # 可见性状态

        self.color_map =[
             "red",
             "blue",
             "green",
             "yellow",
             "cyan",
             "magenta",
             "purple",
             "orange",
             "black",
             "brown",
             "gold",
             "skyblue",
             "navy",
             "olive",
             "hotpink",
             "violet",
             "lime"
        ]
        self.color_map.remove(self.color)  # 避免与初始颜色冲突
        self.slope_color = random.choice(self.color_map)  # 随机选择斜率线颜色
        
        
        self._init_plot()      # 初始化绘图
        self._connect_events() # 连接交互事件

    # region 属性管理
    @property
    def delt_T(self) -> float:
        """获取x轴缩放因子"""
        return self._delt_T
    
    @delt_T.setter
    def delt_T(self, value: float):
        """设置x轴缩放因子并更新所有线条位置
        
        Args:
            value: 新的缩放因子值
        """
        if value == self._delt_T:
            return
        self._delt_T = value
        self._update_all_lines()  # 更新所有线条位置和斜率文本

    @property
    def visible(self) -> bool:
        """获取当前可见性状态"""
        return self._visible
    
    @visible.setter
    def visible(self, value: bool):
        """设置可见性状态
        
        Args:
            value: True显示，False隐藏
        """
        if value == self._visible:
            return
        self._visible = value
        self._set_visibility(self._visible)

    @property
    def color(self) -> str:
        """获取当前颜色值"""
        return self._color
    
    @color.setter
    def color(self, value: str):
        """设置颜色并更新所有相关元素
        
        Args:
            value: 新的颜色值
        """
        if value == self._color:
            return
        self._color = value
        self._update_colors()
    # endregion

    # region 初始化方法
    def _init_plot(self):
        """初始化散点图绘制"""
        self.scatter = self.ax.scatter(
            range(len(self.y_value)), 
            self.y_value,
            color=self.color, 
            linestyle='--', 
            linewidth=1,
            alpha=0.3, 
            picker=5,          # 设置可拾取距离
            edgecolors='none',  # 无边缘颜色
            rasterized=True     # 启用栅格化
        )
        self._setup_hover()     # 设置悬停提示

    def _connect_events(self):
        """连接所有必要的事件处理器"""
        self.ax.figure.canvas.mpl_connect('pick_event', self._on_pick)
        self.ax.figure.canvas.mpl_connect('key_press_event', self._on_key_press)
    # endregion

    # region 绘图相关方法
    def _setup_hover(self):
        """配置鼠标悬停显示数据点信息的功能"""
        mplcursors.cursor(self.scatter, hover=2).connect(
            "add", lambda sel: sel.annotation.set_text(
                f"({int(sel.target[0])}, {sel.target[1]:.2f})"
            )
        )

    def _draw_line_between_points(self):
        """在选中的两点间绘制斜率和直线"""
        if len(self.selected_points) != 2:
            return
        
        # 获取选中点的索引和坐标
        i1, i2 = self.selected_points
        x1, x2 = i1 * self.delt_T, i2 * self.delt_T
        y1, y2 = self.y_value[i1], self.y_value[i2]
        
        # 计算斜率（处理除零情况）
        slope = float('inf') if x2 == x1 else (y2 - y1) / (x2 - x1)
        # print(i1,i2)
        # print(x1,x2)
        # print(y1,y2)
        # print(slope)
        # 创建直线和文本
        line = self._create_line(i1, i2,y1, y2)
        text = self._create_slope_text(i1, i2,x1,x2,y1, y2, slope)
        
        # 存储线条信息
        self.lines.append(LineInfo(line, text, (i1, i2)))
        self.ax.figure.canvas.draw_idle()

    def _create_line(self, i1:int, i2:int, y1: float, y2: float):
        """创建两点间的直线对象
        
        Args:
            i1, i2: 两点的索引
            x1, x2: 两点的x坐标
            y1, y2: 两点的y坐标
            
        Returns:
            创建的直线对象
        """
        return self.ax.plot(
            [i1, i2], [y1, y2], 
            color=self.slope_color, 
            linewidth=3,
            picker=5  # 使直线可被选中
        )[0]

    def _create_slope_text(self, i1:int, i2:int, x1: float, x2: float, 
                          y1: float, y2: float, slope: float):
        """创建斜率文本对象
        
        Args:
            x1, x2: 两点的x坐标
            y1, y2: 两点的y坐标
            slope: 计算得到的斜率值
            
        Returns:
            创建的文本对象
        """
        return self.ax.text(
            (i1 + i2)/2, (y1 + y2)/2,  # 文本位置为两点中点
            f'{self.label} 点 {x1:.2f}-点{x2:.2f} 的斜率为: {slope:.2f}', 
            color=self.slope_color, 
            fontsize=8,
            ha='center',  # 水平居中
            va='center'   # 垂直居中
        )
    # endregion

    # region 更新方法
    def _update_all_lines(self):
        """更新所有线条的位置和斜率文本"""
        for line_info in self.lines:
            i1, i2 = line_info.indices
            # 计算新的坐标
            x1, x2 = i1 * self.delt_T, i2 * self.delt_T
            y1, y2 = self.y_value[i1], self.y_value[i2]
            
            # 更新直线位置
            # line_info.line.set_data([x1, x2], [y1, y2])
            
            # 重新计算并更新斜率文本
            slope = float('inf') if x2 == x1 else (y2 - y1) / (x2 - x1)
            line_info.text.set_text(
                f'{self.label} 点 {x1:.2f}-点{x2:.2f} 的斜率为: {slope:.2f}')
            # line_info.text.set_position(((x1 + x2)/2, (y1 + y2)/2))
        
        self.ax.figure.canvas.draw_idle()

    def _update_colors(self):
        """更新所有元素的颜色"""
        self.scatter.set_color(self.color)
        # for line_info in self.lines:
        #     line_info.line.set_color(self.color)
        #     line_info.text.set_color(self.color)
        self.ax.figure.canvas.draw_idle()

    def _set_visibility(self, visible: bool):
        """设置所有元素的可见性
        
        Args:
            visible: True显示，False隐藏
        """
        self.scatter.set_visible(visible)
        for line_info in self.lines:
            line_info.line.set_visible(visible)
            line_info.text.set_visible(visible)
        self.ax.figure.canvas.draw_idle()
    # endregion

    # region 事件处理
    def _on_pick(self, event: PickEvent):
        """统一处理所有坐标轴的pick事件"""
        # print(event.artist.axes)
        # print(event.artist.axes == self.ax)
        # 处理散点点击
        if event.artist == self.scatter:
            self._handle_scatter_pick(event)
        # 处理本管理器创建的线条点击
        elif event.artist in [line_info.line for line_info in self.lines]:
            self._handle_line_pick(event)

    def _handle_scatter_pick(self, event: PickEvent):
        """处理散点被选中事件"""
        self.selected_points.append(event.ind[0])
        if len(self.selected_points) == 2:
            self._draw_line_between_points()
            self.selected_points = []  # 重置选择

    def _handle_line_pick(self, event: PickEvent):
        """处理直线被选中事件"""
        self.selected_line = event.artist

    def _on_key_press(self, event: KeyEvent):
        """处理键盘按键事件"""
        if event.key == 'd' and self.selected_line:
            self._remove_selected_line()

    def _remove_selected_line(self):
        """删除当前选中的直线"""
        for i, line_info in enumerate(self.lines):
            if line_info.line == self.selected_line:
                line_info.line.remove()
                line_info.text.remove()
                del self.lines[i]
                self.ax.figure.canvas.draw_idle()
                self.selected_line = None
                break
    # endregion

    def clear_scatter(self):
        """清除所有绘图元素"""
        if self.scatter:
            self.scatter.remove()
            for line_info in self.lines:
                line_info.line.remove()
                line_info.text.remove()
            self.lines.clear()
            self.ax.figure.canvas.draw_idle()