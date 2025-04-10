import logging
from datetime import datetime
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

class LineNotifier:
    """
    Line messaging API notifier
    """
    def __init__(self, channel_access_token=None, user_id=None):
        self.channel_access_token = "LINE_NOTIFY_TOKEN"  # 替換為您的LINE Notify令牌
        self.default_user_id = "USER_ID"  # 替換為您的LINE用戶ID
        
        # 初始化Line Bot API
        self.line_bot_api = LineBotApi(self.channel_access_token)
        self.logger = logging.getLogger('key_wizard')
    
    def send_message(self, message, user_id=None):
        try:
            recipient = user_id or self.default_user_id
            
            # 檢查是否有有效的令牌和用戶ID
            if self.channel_access_token == "LINE_NOTIFY_TOKEN":
                self.logger.warning("Line通知未配置:缺少有效的令牌")
                return False
            
            # 發送訊息
            messages = TextSendMessage(text=message)
            self.line_bot_api.push_message(recipient, messages)
            
            self.logger.info(f"已發送LINE訊息: {message}")
            return True
            
        except Exception as e:
            self.logger.error(f"發送LINE訊息時發生錯誤: {e}")
            return False
    
    def notify_program_stopped(self, reason="自動停止"):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"btnSprite 程序通知\n時間: {current_time}\n狀態: 程序已{reason}。"
        
        return self.send_message(message)