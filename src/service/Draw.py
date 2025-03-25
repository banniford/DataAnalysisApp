# Draw.py
from ui.mplcanvas import MplWidget
import mplcursors  # 引入mplcursors库
from matplotlib.widgets import Slider
from PyQt6.QtWidgets import QMainWindow
from service.ReferenceLineManager import ReferenceLineManager
from service.LineManager import LineManager
from matplotlib.ticker import FuncFormatter
from service.ReportTable import ReportTable
from service.DataAnalysis import DataAnalysis
from service.ScatterManager import ScatterManager
import copy,random

class Draw:
    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window
        self.main_ui = main_window.main_ui
        self.data_analysis = DataAnalysis(self)
        self.report_table = ReportTable(main_window,self.data_analysis)

        self.color_map = {
            "红色": "red",
            "蓝色": "blue",
            "绿色": "green",
            "黄色": "yellow",
            "青色": "cyan",
            "品红": "magenta",
            "紫色": "purple",
            "橙色": "orange",
            "黑色": "black",
            "棕色": "brown",
            "金色": "gold",
            "天蓝": "skyblue",
            "深蓝": "navy",
            "橄榄绿": "olive",
            "桃红": "hotpink",
            "紫罗兰": "violet",
            "黄绿色": "lime"
        }
        
        # 获取 MplWidget 对象
        self.mpl_widget = self.main_window.findChild(MplWidget, "mplWidget")  # "mplWidget" 是你在 Qt Designer 中设置的 objectName
        # 访问 canvas 属性并绘图
        self.canvas = self.mpl_widget.canvas
        self.reset()
        # 添加滑块
        self.slider = self.add_threshold_slider(self.main_ui.doubleSpinBox_2.value(),self.main_ui.doubleSpinBox_3.value()) 
        # 绑定事件
        self.slider.on_changed(lambda val: self.update_jumps())
        # 更新阈值
        self.main_ui.doubleSpinBox_2.valueChanged.connect(self.update_slider_threshold)
        self.main_ui.doubleSpinBox_3.valueChanged.connect(self.update_slider_threshold)
        self.main_ui.spinBox_3.valueChanged.connect(lambda val: self.update_jumps())
        # Matplotlib 自动计算比较合适的边距和间隔。
        self.canvas.fig.tight_layout()

    def reset(self):
        # 绘制新的数据
        self.canvas.ax_left.cla()  # 清除当前轴上的所有内容
        self.canvas.ax_right.cla()
        # 重新计算轴的限制并自动调整视图
        self.canvas.ax_left.relim()  # 重新计算数据的限制
        self.canvas.ax_left.autoscale_view()  # 自动调整视图的范围
        self.reference_line_manager = {}
        self.line_manager = {}
        self.scatter_manager = {}
        self.scatter_visible = True
        # 添加title和label
        self.canvas.ax_left.set_title("数据分析(点击拖动参考线，按D删除，按C清空，按A添加)",
                                      pad=12)  # 向上移动标题（单位是 points，默认是 6）
        self.canvas.ax_left.set_xlabel("数据点位")
        # 增加背景网格
        self.canvas.ax_left.grid(True, linestyle='-', alpha=0.8)
        self.canvas.ax_right.grid(False)
        # 左侧坐标轴在最上层
        self.canvas.ax_left.set_zorder(1)
        # 清空表格
        self.report_table.clear_all_columns()
        # Matplotlib 自动计算比较合适的边距和间隔。
        self.canvas.fig.tight_layout()
    
    def set_scatter_visible(self):
        """设置散点图可见"""
        if self.scatter_visible:
            for scatter in self.scatter_manager.values():
                scatter.visible=False
            self.scatter_visible = False
        else:
            for scatter in self.scatter_manager.values():
                scatter.visible= True
            self.scatter_visible = True
        self.canvas.draw_idle()

    def set_reference_line_visible(self):
        """设置参考线可见"""
        master_var = self.main_ui.comboBox2_3.currentText()
        if not master_var:
            return
        reference_line_manager = self.reference_line_manager.get(master_var)
        if reference_line_manager:
            if reference_line_manager.visible:
                reference_line_manager.visible = False
            else:
                reference_line_manager.visible = True
            self.canvas.draw_idle()
    
    def create_line_manager(self, label, y_value, color,ax)->LineManager:
        """创建折线管理器"""
        if label not in self.line_manager:
            self.line_manager[label] = LineManager(label,
                                                   ax,
                                                y_value,
                                                    color)
        return self.line_manager[label]
    
    def create_reference_line_manager(self, name,xpos_list,y_value,left_Zone,right_Zone)->ReferenceLineManager:
        """创建参考线管理器"""
        if name not in self.reference_line_manager:
            self.reference_line_manager[name] = ReferenceLineManager(name,
                                                                     self.canvas, 
                                                                     xpos_list, 
                                                                     y_value, 
                                                                     left_Zone, 
                                                                     right_Zone, 
                                                                     self.update_lines,
                                                                     self.update_table)
            self.main_ui.spinBox_1.valueChanged.connect(lambda val: self.reference_line_manager[name].update_left_zone(val))
            self.main_ui.spinBox_2.valueChanged.connect(lambda val: self.reference_line_manager[name].update_right_zone(val))
        return self.reference_line_manager[name]
    
    def create_scatter_manager(self, label, ax, y_value, color='gray'):
        """创建散点图管理器"""
        if label not in self.scatter_manager:
            self.scatter_manager[label] = ScatterManager(label,ax, y_value, color)
        return self.scatter_manager[label]
    
    def add_threshold_slider(self, initial_threshold,max_threshold):
        """添加阈值调整滑块"""
        ax_slider = self.canvas.fig.add_axes([0.2, 0.003, 0.6, 0.01], facecolor='lightgoldenrodyellow')
        slider = Slider(ax_slider, '突变识别阈值', 0.0, max_threshold, valinit=initial_threshold)
        return slider
    
    def update_slider_threshold(self):
        """更新阈值"""
        # 添加
        initial_threshold = self.main_ui.doubleSpinBox_2.value()
        max_threshold = self.main_ui.doubleSpinBox_3.value()
        if initial_threshold > max_threshold:
            self.main_window.msg("最小阈值不能大于最大阈值")
            return
        # 删除滑块
        self.canvas.fig.delaxes(self.slider.ax)
        self.slider = self.add_threshold_slider(initial_threshold,max_threshold)
        self.slider.on_changed(lambda val: self.update_jumps())
        
    def draw_reference_line(self, name, jumps):
        """绘制参考线"""
        # 创建参考线管理器
        reference_line_manager = self.reference_line_manager.get(name)
        if not reference_line_manager:
            return
        # 绘制参考线
        reference_line_manager.set_jumps(jumps)

    def clear_reference_line(self, name):
        """清除参考线"""
        reference_line_manager = self.reference_line_manager.get(name)
        if reference_line_manager:
            reference_line_manager.clear_lines()
    
    def update_jumps(self):
        """根据新阈值更新突变点和参考线"""
        master_var = self.main_ui.comboBox2_3.currentText()
        if not master_var:
            return
        v = self.data_analysis.get_var_value(master_var)
        reference_line_manager = self.create_reference_line_manager(
                                            master_var, 
                                            range(len(v)),
                                            v,
                                            self.main_ui.spinBox_1.value(),
                                            self.main_ui.spinBox_2.value())
        
        # 删除所有现有参考线
        reference_line_manager.clear_lines()
        # 重新检测突变点
        jumps = self.data_analysis.pandas_detect_jumps(
                                                master_var,
                                                self.main_ui.spinBox_3.value(), 
                                                self.slider.val)
        self.draw_reference_line(master_var,jumps)
        self.canvas.draw_idle()

    def update_lines(self,stable_interval):
        # 创建折线管理器
        v = self.data_analysis.get_var_value(self.main_ui.comboBox2_3.currentText())
        line_manager = self.create_line_manager(self.main_ui.comboBox2_3.currentText(),
                                                v,
                                                "red",
                                                self.canvas.ax_left)
        # 更新稳定区间
        line_manager.stable_interval = stable_interval
        
        for var in self.main_window.slave_var:
            self._line(var, stable_interval,self.canvas.ax_right)

    def update_table(self,stable_interval):
        # 设置稳定区间
        self.data_analysis.set_stable_interval(self.main_ui.comboBox2_3.currentText(), stable_interval)
        cal_list = copy.deepcopy(self.main_window.slave_var)
        cal_list.insert(0,self.main_ui.comboBox2_3.currentText())
        # 计算所有主/从变量平均值
        for var in cal_list:
            self.data_analysis.cal_avg(cal_list[0],var)
        # 计算所有主/从变量最大最小值
        for var in cal_list:
            self.data_analysis.cal_max_min(cal_list[0],var)
        # 更新表格为当前主变量和从变量
        self.report_table.update_table(cal_list)

    def draw_master(self, master_var):
        """绘制主变量"""
        color = self._line(master_var, [],self.canvas.ax_left)
        self._scatter(master_var,color,self.canvas.ax_left)
        

    def clear_master(self, master_var):
        self.clear_scatter(master_var)
        self.clear_reference_line(master_var)
        self.clear_lines(master_var)
        self.report_table.clear_all_rows()

    def draw_slave(self, slave_var):
        """绘制从变量"""
        color = self._line(slave_var, [],self.canvas.ax_right)
        self._scatter(slave_var,color,self.canvas.ax_right)

    def clear_slave(self, slave_var):
        self.clear_scatter(slave_var)
        self.clear_lines(slave_var)

    def _scatter(self, label,color,ax = None):
        """添加散点图"""
        v = self.data_analysis.get_var_value(label)
        scatter = self.create_scatter_manager(label, ax, v, color)
        # 更新图例
        self.canvas.ax_left.legend(loc = "upper left")
        self.canvas.ax_right.legend(loc = "upper right")
        self.canvas.fig.tight_layout()
        # 添加到管理器
        self.scatter_manager[label] = scatter
        self.canvas.draw_idle()

    def _line(self, label, stable_interval,ax):
        """添加一条折线"""
        # 创建折线管理器
        # 颜色列表，除了红色，蓝色的其他随机颜色
        color_name = random.choice(list(self.color_map.keys()))
        cur_color = self.color_map[color_name]
        v = self.data_analysis.get_var_value(label)
        line_manager = self.create_line_manager(label,
                                                v,
                                                cur_color,
                                                ax)
        # 设置稳定区间
        line_manager.stable_interval = stable_interval
        return cur_color
    
    def clear_lines(self, var):
        """清除折线"""
        line_manager = self.line_manager.get(var)
        if line_manager:
            line_manager.clear_lines()
            self.line_manager.pop(var)
        # 更新图例
        self.canvas.ax_left.legend(loc = "upper left")
        self.canvas.ax_right.legend(loc = "upper right")
        self.canvas.fig.tight_layout()
        self.canvas.draw_idle()
            

    def clear_scatter(self, label):
        scatter = self.scatter_manager.get(label)
        if scatter:
            scatter.clear_scatter()
            del self.scatter_manager[label]
            # 更新图例
            self.canvas.ax_left.legend(loc = "upper left")
            self.canvas.ax_right.legend(loc = "upper right")
            self.canvas.draw_idle()

    def update_left_ylim(self):
        y = self.data_analysis.get_var_value(self.main_ui.comboBox2_3.currentText())
        self.canvas.ax_left.set_ylim(min(y), max(y))
        self.canvas.draw_idle()

    def update_right_ylim(self):
        y = self.data_analysis.get_var_value(self.main_ui.comboBox2_4.currentText())
        self.canvas.ax_right.set_ylim(min(y), max(y))
        self.canvas.draw_idle()


    def update_x_formatter(self, formatterFunc):
        """更新 x 轴格式"""
        self.canvas.ax_left.xaxis.set_major_formatter(FuncFormatter(formatterFunc))
        self.canvas.draw_idle()
    
    