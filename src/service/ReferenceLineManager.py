# ReferenceLineManager.py
import copy
from ui.mplcanvas import MplCanvas
from typing import Callable
# 用于管理参考线的类
class ReferenceLineManager:
    def __init__(self,
                 name:str, 
                 canvas:MplCanvas, 
                 xpos_list:list, 
                 y_value:list, 
                 left_Zone:int, 
                 right_Zone:int,
                 update_lines_table:Callable):
        self.name = name
        self.canvas = canvas
        self.ax = canvas.ax_right
        self.xpos_list = xpos_list
        self.y_value = y_value
        self.stable_interval=[]
        self._jumps = []  # 内部存储 jumps
        self.t_lines = []  # 主变量参考线
        self.ft_lines = []  # 左侧参考线
        self.bt_lines = []  # 右侧参考线
        self.current_line = None
        self.current_index = None  # 用来标记当前选中的参考线的索引
        self.left_Zone = left_Zone
        self.right_Zone = right_Zone
        self.update_lines_table = update_lines_table

        # 绑定事件
        self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = self.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cid_key = self.canvas.mpl_connect('key_press_event', self.on_key)

    @property
    def jumps(self):
        """获取 jumps 值"""
        return self._jumps

    @jumps.setter
    def jumps(self, value):
        """设置 jumps 值并自动调用更新函数"""
        self._jumps = value
        self.update_stable_interval()  # 当 jumps 更新时，自动调用更新函数

    def set_jumps(self, jumps):
        """手动设置 jumps
        用于初始化时设置 jumps
        比较jumps与当前jumps是否相同，如果不同则更新
        多则增量更新，少则直接替换
        """
        if jumps == self.jumps:
            return
        if len(jumps) > len(self.jumps):
            # 增量更新
            for jump in jumps:
                if jump not in self.jumps:
                    self.add_line(jump)
        else:
            # 直接替换
            self.clear_lines()
            for jump in jumps:
                self.add_line(jump)
        self.jumps = jumps  # 使用 property 的 setter 触发自动更新
        

    def update_jumps(self, act, jump):
        """更新突变点"""
        if act == "d":
            t =  copy.deepcopy(self._jumps)
            t.pop(self.jumps.index(jump))
            self.set_jumps(t)
        elif act == "a":
            t =  copy.deepcopy(self._jumps)
            if jump not in t:
                t.append(jump)
                self.set_jumps(t)
        elif act == "u":
            self.set_jumps(jump)

    def update_stable_interval(self):
        """更新稳定区间"""
        self.stable_interval.clear() # 清空稳定区间
        jumps = copy.deepcopy(self._jumps)
        jumps.sort()  # 排序
        # 检查 jumps 是否为空
        if not jumps:
            # 通知折线管理器,表格更新
            self.update_lines_table(self.stable_interval)
            return

        # 确保第一个突变点不会导致前死区小于0
        first_jump = jumps[0]
        if first_jump - self.left_Zone < 0:
            first_jump = self.left_Zone + 1  # 确保前死区不会小于0

        # 确保第一个突变点加后死区不会越界
        if first_jump + self.right_Zone >= len(self.y_value):
            first_jump = len(self.y_value) - self.right_Zone - 1  # 确保加后死区不越界

        # 更新第一个稳定区间
        self.stable_interval.append([0, first_jump - self.left_Zone])  # 起始到第一个突变点减去左死区

        if len(jumps) == 1:
            self.stable_interval.append([jumps[0] + self.right_Zone, len(self.y_value) - 1])
        else:
            for i in range(1, len(jumps)):
                if jumps[i - 1] + self.right_Zone >= jumps[i] - self.left_Zone:
                    continue
                else:
                    self.stable_interval.append([jumps[i - 1] + self.right_Zone, jumps[i] - self.left_Zone])

            # 确保最后一个突变点加右死区不会越界
            last_jump = jumps[-1]
            if last_jump + self.right_Zone >= len(self.y_value):
                last_jump = len(self.y_value) - self.right_Zone - 1

            self.stable_interval.append([jumps[-1] + self.right_Zone, len(self.y_value) - 1])

        # print(self.stable_interval)
        # 通知折线管理器,表格更新
        self.update_lines_table(self.stable_interval)



    def update_left_zone(self, left_zone):
        """更新左侧区间"""
        self.left_Zone = left_zone
        # 更新所有左侧参考线
        for i, line in enumerate(self.ft_lines):
            xpos = self.t_lines[i].get_xdata()[0]
            line.set_xdata([xpos - self.left_Zone, xpos - self.left_Zone])
        # 更新稳定区间
        self.update_stable_interval()
        self.ax.figure.canvas.draw_idle()  # 仅更新需要修改的部分
    
    def update_right_zone(self, right_zone):
        """更新右侧区间"""
        self.right_Zone = right_zone
        # 更新所有右侧参考线
        for i, line in enumerate(self.bt_lines):
            xpos = self.t_lines[i].get_xdata()[0]
            line.set_xdata([xpos + self.right_Zone, xpos + self.right_Zone])
        # 更新稳定区间
        self.update_stable_interval()
        self.ax.figure.canvas.draw_idle()  # 仅更新需要修改的部分

    def add_line(self, xpos, color='red', linestyle='--', alpha=0.8, picker=5):
        """添加一条参考线"""
        line = self.ax.axvline(x=xpos, color=color, linestyle=linestyle, alpha=alpha, picker=picker)
        self.t_lines.append(line)
        ft_line = self.ax.axvline(x=xpos - self.left_Zone, color='black', linestyle=linestyle, alpha=alpha)
        self.ft_lines.append(ft_line)
        bt_line = self.ax.axvline(x=xpos + self.right_Zone, color='black', linestyle=linestyle, alpha=alpha)
        self.bt_lines.append(bt_line)
        self.ax.figure.canvas.draw_idle()  # 仅更新需要修改的部分

    def on_press(self, event):
        """鼠标按下事件"""
        if event.inaxes != self.ax:
            return

        # 检查是否点击了某条线
        if event.button == 1:  # 左键
            for i, line in enumerate(self.t_lines):
                if line.contains(event)[0]:
                    self.current_line = line
                    self.current_index = i  # 记录当前参考线的索引
                    break

    def on_motion(self, event):
        """鼠标移动事件"""
        if self.current_line is None or event.inaxes != self.ax:
            return

        # 移动参考线
        new_x = event.xdata
        self.current_line.set_xdata([new_x, new_x])

        # 同时移动对应的 ft_lines 和 bt_lines
        if self.current_index is not None:
            self.ft_lines[self.current_index].set_xdata([new_x - self.left_Zone, new_x - self.left_Zone])
            self.bt_lines[self.current_index].set_xdata([new_x + self.right_Zone, new_x + self.right_Zone])

        self.ax.figure.canvas.draw_idle()  # 仅更新需要修改的部分

    def on_release(self, event):
        """鼠标释放事件"""
        if self.current_line is not None:
            # 获取当前线的 X 坐标（一般是个 [x, x]）
            current_x = self.current_line.get_xdata()[0]
            # 1. 找出距离 current_x 最近的点
            snapped_x = min(self.xpos_list, key=lambda px: abs(px - current_x))
            # 2. 将参考线重置到 snapped_x
            self.current_line.set_xdata([snapped_x, snapped_x])

            # 同时更新 ft_lines 和 bt_lines
            if self.current_index is not None:
                self.ft_lines[self.current_index].set_xdata([snapped_x - self.left_Zone, snapped_x - self.left_Zone])
                self.bt_lines[self.current_index].set_xdata([snapped_x + self.right_Zone, snapped_x + self.right_Zone])
            # 同时更新 jumps 中对应的值
            t = copy.deepcopy(self._jumps)
            t[self.current_index] = snapped_x
            self.update_jumps("u",t)
            # 3. 释放 current_line 引用
            self.current_line = None
            self.current_index = None  # 清空索引

            # 4. 刷新画布
            self.ax.figure.canvas.draw_idle()

    def on_key(self, event):
        """键盘事件"""
        if event.key == 'd' and self.current_line is not None:
            # 删除当前选中的参考线
            self.current_line.remove()
            self.t_lines.remove(self.current_line)
            self.ft_lines[self.current_index].remove()
            self.bt_lines[self.current_index].remove()
            self.ft_lines.pop(self.current_index)
            self.bt_lines.pop(self.current_index)
            # 更新jumps
            self.update_jumps(event.key,self._jumps[self.current_index])
            self.current_line = None
            self.current_index = None
            self.ax.figure.canvas.draw_idle()
        elif event.key == 'a':
            # 在jumps中合适的位置添加新的突变点
            # 1. 找出距离 current_x 最近的点
            snapped_x = min(self.xpos_list, key=lambda px: abs(px - event.xdata))
            self.update_jumps(event.key,snapped_x)
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