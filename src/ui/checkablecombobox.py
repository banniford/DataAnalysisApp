import sys
from PyQt6.QtWidgets import QComboBox, QMainWindow, QApplication, QLineEdit, QToolTip
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# 自定义可勾选的下拉框组件
class CheckableComboBox(QComboBox):
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.checked_order = []  # +++ 新增：记录点击顺序 +++
        
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
        """ 获取所有被勾选的选项文本（按点击顺序） """
        return self.checked_order.copy()  # +++ 返回点击顺序副本 +++

    def checkedItemsStr(self):
        """ 返回所有被勾选的选项文本，去掉'全选'并用分号拼接 """
        # return ';'.join(self.checkedItems()).strip('全选').strip(';')
        return ';'.join(self.checked_order)  # +++ 直接使用顺序列表 +++

    def showPopup(self):
        """ 展示下拉框时调整其尺寸 """
        self.view().setMinimumWidth(2 * self.width() // 2)  # 调整下拉列表宽度
        self.view().setMaximumHeight(200)  # 限制最大高度为200
        super().showPopup()  # 调用父类方法显示下拉框

    def selectItemAction(self, index):
        """ 当用户点击选项时的处理逻辑 """
        item = self.model().item(index.row(), 0)
        text = item.text()
        state = item.checkState()
        
        # +++ 根据勾选状态更新顺序列表 +++
        if state == Qt.CheckState.Checked:
            if text not in self.checked_order:
                self.checked_order.append(text)
        else:
            if text in self.checked_order:
                self.checked_order.remove(text)
        
        # 更新显示的选中项
        self.lineEdit().clear()
        self.lineEdit().setText(self.checkedItemsStr())

    def clear(self) -> None:
        """ 清空下拉框选项并重新添加 '全选' 选项 """
        super().clear()
        self.checked_order.clear()  # +++ 清空顺序列表 +++
        # self.addCheckableItem('全选')

    def remove_diff(self, text: list):
        """ 移除给定列表中的选项 """
        for i in text:
            index = self.findText(i)
            if index != -1:
                self.removeItem(index)
                if i in self.checked_order:  # +++ 同步移除顺序列表项 +++
                    self.checked_order.remove(i)

    def select_all(self):
        """ 选中所有选项 """
        for i in range(self.model().rowCount()):
            item = self.model().item(i, 0)
            if item.checkState() != Qt.CheckState.Checked:  # +++ 仅处理未选中项 +++
                item.setCheckState(Qt.CheckState.Checked)
                text = item.text()
                if text not in self.checked_order:  # +++ 避免重复添加 +++
                    self.checked_order.append(text)
        self.lineEdit().setText(self.checkedItemsStr())

# 创建主窗口类（保持不变）
class Ui_Study(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(500, 500)
        self.setMinimumSize(500, 500)
        
        self.combobox = CheckableComboBox(self)
        self.combobox.move(20, 20)
        self.combobox.resize(200, 30)
        
        self.line_edit = QLineEdit(self)
        self.line_edit.move(20, 80)
        self.line_edit.resize(300, 30)
        
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
    app = QApplication(sys.argv)
    my_ui = Ui_Study()
    sys.exit(app.exec())