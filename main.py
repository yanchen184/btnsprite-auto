#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
BtnSprite - 視覺化按鍵精靈

作者: yanchen
版本: 3.1
"""

import tkinter as tk
import logging

from modules.gui import KeyWizardGUI
from modules.utils import check_images, create_bat_file

def main():
    """程序主入口"""
    logger = logging.getLogger('key_wizard')
    logger.info("===== 啟動btnSprite視覺化按鍵精靈 =====")
    
    print("======== Python 按鍵精靈 - 視覺化版 ========")
    print("版本: 3.1")
    print("功能: 自動識別圖片並執行按鍵操作，支援視覺化介面")
    print("更新: 1. 修正按鈕點擊問題")
    print("      2. 增強LINE通知功能，在程序停止時發送通知")
    print("      3. 優化代碼結构")
    print("=========================================")
    
    # 建立啟動批次檔
    create_bat_file()
    
    # 檢查必要的圖片是否存在
    check_images()
    
    # 啟動GUI
    root = tk.Tk()
    app = KeyWizardGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()