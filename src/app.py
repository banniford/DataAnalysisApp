import sys
from PyQt6.QtWidgets import QDialog
from control.HandleFunc import MainWindow
from PyQt6.QtWidgets import QApplication
from service.Login import Login

# 注意修改./ui/picturetoolUI.py 文件中.ico的路径为 ./ 以main文件为起始地址
if __name__ == '__main__':
    app = QApplication([])
    Window = MainWindow()
    login = Login()
    # 显示登录窗口
    if login.exec() == QDialog.DialogCode.Accepted:
        # 登录成功后才显示主窗口
        Window.show()
        sys.exit(app.exec())
    else:
        # 登录失败直接退出
        sys.exit()