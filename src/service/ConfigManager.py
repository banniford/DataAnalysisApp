import os
import json
import time
import base64

class ConfigManager:
    def __init__(self):
        self.app_data_dir = os.path.join(os.getenv('APPDATA'), "DataAna")
        self.config_path = os.path.join(self.app_data_dir, "config.json")
        os.makedirs(self.app_data_dir, exist_ok=True)

    def save_session(self, username, duration=86400*7):
        """保存登录时间戳和会话总时长（秒）"""
        data = {
            "username": base64.b64encode(username.encode()).decode(),
            "login_time": time.time(),  # 使用单调时间戳
            "duration": duration
        }
        with open(self.config_path, 'w') as f:
            json.dump(data, f)

    def load_session_data(self):
        """返回完整会话数据（包含用户名和剩余时间）"""
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                return {
                    "username": base64.b64decode(data["username"]).decode(),
                    "remaining": self._calculate_remaining(data)
                }
        except:
            return None

    def _calculate_remaining(self, data):
        """计算剩余时间"""
        elapsed = time.time() - data["login_time"]
        return max(round(data["duration"] - elapsed), 0)