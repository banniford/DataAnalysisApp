import sys

from control.HandleFunc import MainWindow
from PyQt6.QtWidgets import QApplication

# 注意修改./ui/picturetoolUI.py 文件中.ico的路径为 ./ 以main文件为起始地址
if __name__ == '__main__':
    app = QApplication([])
    Window = MainWindow()
    Window.show()
    sys.exit(app.exec())