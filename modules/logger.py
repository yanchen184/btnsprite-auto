"""
Logging configuration for the btnSprite application.
"""

import os
import logging

def setup_logging():
    """設置全局日誌配置"""
    # 獲取腳本目錄
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 日誌文件路徑
    log_path = os.path.join(script_dir, "key_wizard.log")
    
    # 配置日誌
    logger = logging.getLogger('key_wizard')
    
    # 避免重複添加處理器
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # 文件處理器
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加處理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger