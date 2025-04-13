import sys
from PyQt6.QtWidgets import QDialog
from control.HandleFunc import MainWindow
from PyQt6.QtWidgets import QApplication
from service.Login import Login
from service.ConfigManager import ConfigManager  # 新增导入

# 注意修改./ui/picturetoolUI.py 文件中.ico的路径为 ./ 以main文件为起始地址
# app.py
if __name__ == '__main__':
    app = QApplication([])
    cm = ConfigManager()
    
    # 检查有效会话
    if session_data := cm.load_session_data():
        if session_data["remaining"] > 0:
            Window = MainWindow()
            Window.start_session_timer(session_data["remaining"])
            Window.show()
            sys.exit(app.exec())
    
    # 需要重新登录
    login = Login()
    if login.exec() == QDialog.DialogCode.Accepted:
        Window = MainWindow()
        Window.start_session_timer(cm.load_session_data()["remaining"])
        Window.show()
        sys.exit(app.exec())