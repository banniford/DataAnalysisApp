from PyQt6.QtWidgets import QDialog
from ui.Ui_login import Ui_Dialog
from datetime import datetime
from service.ConfigManager import ConfigManager  # 新增导入

class Login(QDialog):
    def __init__(self):
        """登录窗口类"""
        super().__init__()
        self.config = ConfigManager()  # 新增配置管理器实例
        self.main_ui = Ui_Dialog()
        self.main_ui.setupUi(self)
        self.main_ui.pushButton.clicked.connect(self.authenticate)  # 连接登录按钮事件
        self.main_ui.lineEdit_1.setFocus()  # 设置用户名输入框为默认焦点
        self.main_ui.lineEdit_1.setPlaceholderText("请输入用户名")
        self.main_ui.lineEdit_2.setPlaceholderText("请输入密码")  # 设置密码输入框提示文本
        self.main_ui.label_3.setText("")  # 清空提示标签文本

        # 新增：自动填充用户名
        if session_data := self.config.load_session_data():
            self.main_ui.lineEdit_1.setText(session_data["username"])
    

    def authenticate(self):
        """验证密码"""
        username = self.main_ui.lineEdit_1.text().strip()
        password = self.main_ui.lineEdit_2.text().strip()
        # 生成期望密码
        expected_pwd = self.generate_dynamic_password(username)
        # print(f"期望密码: {expected_pwd}")
        # print(f"输入密码: {password}")

        if password == expected_pwd:
            self.config.save_session(username)  # 保存配置
            self.accept()  # 关闭登录对话框
        else:
            self.main_ui.lineEdit_2.clear()
            self.main_ui.label_3.setText("密码错误，请重新输入！")
            self.main_ui.label_3.setStyleSheet("color: red;")  # 设置错误提示颜色为红色

    # --------------------------
    # 密码生成核心逻辑
    # --------------------------
    def keyboard_left_shift(self,username):
        """将用户名按QWERTY键盘左移一位"""
        keyboard_map = {
            # 第一行（qwertyuiop）
            'q': 'q', 'w': 'q', 'e': 'w', 'r': 'e', 't': 'r', 
            'y': 't', 'u': 'y', 'i': 'u', 'o': 'i', 'p': 'o',
            # 第二行（asdfghjkl）
            'a': 'a', 's': 'a', 'd': 's', 'f': 'd', 'g': 'f',
            'h': 'g', 'j': 'h', 'k': 'j', 'l': 'k',
            # 第三行（zxcvbnm）
            'z': 'z', 'x': 'z', 'c': 'x', 'v': 'c', 
            'b': 'v', 'n': 'b', 'm': 'n',
            # 大写字母转换为小写处理
            'Q': 'q', 'W': 'q', 'E': 'w', 'R': 'e', 'T': 'r',
            'Y': 't', 'U': 'y', 'I': 'u', 'O': 'i', 'P': 'o',
            'A': 'a', 'S': 'a', 'D': 's', 'F': 'd', 'G': 'f',
            'H': 'g', 'J': 'h', 'K': 'j', 'L': 'k',
            'Z': 'z', 'X': 'z', 'C': 'x', 'V': 'c',
            'B': 'v', 'N': 'b', 'M': 'n'
        }
        shifted = []
        for char in username:
            shifted.append(keyboard_map.get(char, char))  # 未知字符保持原样
        return ''.join(shifted)
    
    def generate_time_code(self):
        """生成时间码（年、月、日、时、分的最后一位）"""
        now = datetime.now()
        time_components = [
            now.year,    # 年，取最后一位
            now.month,   # 月
            now.day,     # 日
            now.hour,    # 时
        ]
        code = []
        for comp in time_components:
            str_comp = str(comp).zfill(2)  # 统一补零成两位数
            code.append(str_comp[-1])     # 取最后一位
        return ''.join(code)
    
    
    def generate_dynamic_password(self,username):
        """生成动态密码"""
        shifted_username = self.keyboard_left_shift(username)
        time_code = self.generate_time_code()
        return f"{shifted_username}{time_code}"