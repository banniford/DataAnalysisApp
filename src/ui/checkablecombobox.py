import sys
from PyQt6.QtWidgets import QComboBox, QMainWindow, QApplication, QLineEdit, QToolTip
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# 自定义可勾选的下拉框组件
class CheckableComboBox(QComboBox):
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        
        # 创建只读的 QLineEdit 作为下拉框的编辑框
        self.setLineEdit(QLineEdit())
        self.lineEdit().setReadOnly(True)  # 让编辑框内容只读，防止手动输入
        
        # 绑定点击选项的事件处理函数
        self.view().clicked.connect(self.selectItemAction)
        
        # 添加一个“全选”选项
        # self.addCheckableItem('全选')
        # self.addCheckableItem('无')
        
        # 变量用于控制全选和取消全选状态（1 代表全选，0 代表取消全选）
        # self.SelectAllStatus = 1

        

    def addCheckableItem(self, text):
        """ 添加一个可勾选的选项 """
        super().addItem(text)  # 调用父类方法添加选项
        item = self.model().item(self.count() - 1, 0)  # 获取新添加的选项项
        
        # 设置选项可勾选且可用
        item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        item.setCheckState(Qt.CheckState.Unchecked)  # 默认未勾选
        item.setToolTip(text)  # 设置鼠标悬浮提示

    def addCheckableItems(self, texts):
        """ 添加多个可勾选的选项 """
        for text in texts:
            self.addCheckableItem(text)

    def ifChecked(self, index):
        """ 检查指定索引的选项是否被勾选 """
        item = self.model().item(index, 0)
        return item.checkState() == Qt.CheckState.Checked

    def checkedItems(self):
        """ 获取所有被勾选的选项文本 """
        return [self.itemText(i) for i in range(self.count()) if self.ifChecked(i)]

    def checkedItemsStr(self):
        """ 返回所有被勾选的选项文本，去掉'全选'并用分号拼接 """
        # return ';'.join(self.checkedItems()).strip('全选').strip(';')
        return ';'.join(self.checkedItems())

    def showPopup(self):
        """ 展示下拉框时调整其尺寸 """
        self.view().setMinimumWidth(2 * self.width() // 2)  # 调整下拉列表宽度
        self.view().setMaximumHeight(200)  # 限制最大高度为200
        super().showPopup()  # 调用父类方法显示下拉框

    def selectItemAction(self, index):
        """ 当用户点击选项时的处理逻辑 """
        # if index.row() == 0:  # 如果点击的是“全选”
        #     for i in range(self.model().rowCount()):
        #         if self.SelectAllStatus:
        #             self.model().item(i).setCheckState(Qt.CheckState.Checked)  # 全选
        #         else:
        #             self.model().item(i).setCheckState(Qt.CheckState.Unchecked)  # 取消全选
        #     self.SelectAllStatus = (self.SelectAllStatus + 1) % 2  # 切换状态

        # 更新显示的选中项
        self.lineEdit().clear()
        self.lineEdit().setText(self.checkedItemsStr())

    def clear(self) -> None:
        """ 清空下拉框选项并重新添加 '全选' 选项 """
        super().clear()
        # self.addCheckableItem('全选')

    def remove_diff(self, text: list):
        """ 移除给定列表中的选项 """
        for i in text:
            index = self.findText(i)
            if index != -1:
                self.removeItem(index)

    def select_all(self):
        """ 选中所有选项 """
        for i in range(self.model().rowCount()):
            self.model().item(i).setCheckState(Qt.CheckState.Checked)
        self.lineEdit().setText(self.checkedItemsStr())


# 创建主窗口类
class Ui_Study(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 设置窗口大小
        self.resize(500, 500)
        self.setMinimumSize(500, 500)
        
        # 创建 CheckableComboBox 组件（多选下拉框）
        self.combobox = CheckableComboBox(self)
        self.combobox.move(20, 20)  # 设置组件位置
        self.combobox.resize(200, 30)  # 设置组件大小
        
        # 创建 QLineEdit 组件（文本输入框）
        self.line_edit = QLineEdit(self)
        self.line_edit.move(20, 80)
        self.line_edit.resize(300, 30)
        
        # 添加测试数据
        self.combobox.addCheckableItems(['test', 'test1', 'test2'])
        
        # 默认不选中任何选项
        self.combobox.setCurrentIndex(-1)
        
        # 监听下拉框选项变化，并同步到文本输入框
        self.combobox.lineEdit().textChanged.connect(
            lambda: self.line_edit.setText(self.combobox.checkedItemsStr())
        )
        
        # 显示窗口
        self.show()


if __name__ == '__main__':
    # 创建应用实例
    app = QApplication(sys.argv)
    
    # 创建主窗口实例
    my_ui = Ui_Study()
    
    # 运行应用
    sys.exit(app.exec())