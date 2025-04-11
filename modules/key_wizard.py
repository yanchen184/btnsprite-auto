import cv2
import numpy as np
import pyautogui
import time
import os
import logging
from datetime import datetime
import threading

from .line_notifier import LineNotifier

# LineNotifier is now imported from line_notifier module

class KeyWizard:
    """
    The main class for key wizard functionality.
    Handles screen scanning, image recognition, and automated actions.
    """
    def __init__(self, gui=None, line_notifier=None, direct_click_mode=True):
        """
        Initialize the Key Wizard with default configuration.
        
        Args:
            gui (object, optional): Optional GUI interface for status updates.
        """
        self.gui = gui
        
        # Get current script directory
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Path to template images
        self.template_path = os.path.join(self.script_dir, "keep.png")
        self.btn_path = os.path.join(self.script_dir, "btn.png")
        self.approved_path = os.path.join(self.script_dir, "approved.png")
        self.stop_path = os.path.join(self.script_dir, "stop.png")
        
        # 初始化日誌
        self.logger = logging.getLogger('key_wizard')
        
        # Line notifier
        self.line_notifier = line_notifier or LineNotifier()
        
        # 輸入文字
        self.input_text = "keep"
        self.alt_input_text = "KEEP"  # 大寫替代選項
        self.direct_click_mode = direct_click_mode  # 如果為真，則直接點擊而不輸入文字
        self.confidence_threshold = 0.8
        self.scan_interval = 2  # Seconds between scans
        self.running = False
        
        # Safety pause after startup
        pyautogui.PAUSE = 0.5
        
        self.logger.info("Key Wizard initialized")
    
    def _log_button_press(self):
        """
        Log the button press with timestamp.
        """
        try:
            button_log_path = os.path.join(self.script_dir, "button_press.log")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(button_log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"{current_time} - Button pressed\n")
            self.logger.info(f"Button press logged at {current_time}")
        except Exception as e:
            self.logger.error(f"Error logging button press: {str(e)}")
    
    def _send_line_notification(self, reason="偵測到停止圖片"):
        """
        Send LINE notification when stop image is detected or program stops.
        
        Args:
            reason (str): Reason for sending notification
        """
        try:
            # Send notification through LineNotifier
            result = self.line_notifier.notify_program_stopped(reason)
            
            # Log the attempt
            if result:
                self.logger.info(f"LINE notification sent: {reason}")
                print(f"已發送LINE通知: {reason}")
            else:
                self.logger.warning("LINE notification not sent (check configuration)")
                print("無法發送LINE通知，請檢查Line Notify設定")
            
        except Exception as e:
            self.logger.error(f"Error sending LINE notification: {str(e)}")
            print(f"發送LINE通知時發生錯誤: {str(e)}")
    
    def _load_templates(self):
        """
        Load template images for matching.
        
        Returns:
            bool: True if templates loaded successfully, False otherwise.
        """
        required_images = {
            "template": self.template_path,
            "button": self.btn_path
        }
        
        for name, path in required_images.items():
            if not os.path.exists(path):
                self.logger.error(f"{name.capitalize()} image not found: {path}")
                return False
        
        try:
            self.template_img = cv2.imread(self.template_path)
            self.btn_img = cv2.imread(self.btn_path)
            
            # Optional images
            self.approved_img = cv2.imread(self.approved_path) if os.path.exists(self.approved_path) else None
            self.stop_img = cv2.imread(self.stop_path) if os.path.exists(self.stop_path) else None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading templates: {str(e)}")
            return False
    
    def _locate_on_screen(self, template, confidence=0.8):
        """
        Locate template image on screen.
        
        Args:
            template: Template image to find
            confidence: Matching confidence threshold
            
        Returns:
            tuple or None: Location of matched template
        """
        try:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= confidence:
                h, w = template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                return (center_x, center_y, w, h)
            return None
                
        except Exception as e:
            self.logger.error(f"Image recognition error: {str(e)}")
            return None
    
    def _process_action(self):
        """
        Process screen actions based on image recognition.
        
        Returns:
            bool: True if an action was performed, False otherwise.
        """
        # Check stop image
        if self.stop_img is not None:
            stop_pos = self._locate_on_screen(self.stop_img, self.confidence_threshold)
            if stop_pos:
                self.logger.info("Stop image found")
                self.logger.info("Stop image found, stopping wizard")
                print("找到停止圖片，正在停止程序...")
                self.stop("偵測到停止圖片")
                return True
        
        # Check approved image
        if self.approved_img is not None:
            approved_pos = self._locate_on_screen(self.approved_img, self.confidence_threshold)
            if approved_pos:
                x, y, w, h = approved_pos
                pyautogui.click(x, y)
                time.sleep(1)
                return True
                    
        # Find target and button
        target_pos = self._locate_on_screen(self.template_img, self.confidence_threshold)
        
        if target_pos:
            btn_result = self._locate_on_screen(self.btn_img, self.confidence_threshold)
            
            if btn_result:
                btn_x, btn_y, btn_w, btn_h = btn_result
                # 直接點擊按鈕模式
                if self.direct_click_mode:
                    print(f"直接點擊按鈕，位置: ({btn_x}, {btn_y})")
                    pyautogui.click(btn_x, btn_y)
                    logging.info(f"Clicked button at ({btn_x}, {btn_y})")
                else:
                    # 先將輸入法切換為英文模式
                    print(f"將嘗試輸入文字: {self.input_text}")
                    
                    # 點擊輸入框
                    pyautogui.click(btn_x, btn_y)
                    time.sleep(0.5)
                    
                    # 檢查當前輸入法
                    pyautogui.hotkey('alt', 'shift')  # 嘗試切換輸入法為英文
                    time.sleep(0.2)
                    
                    # 輸入文字
                    pyautogui.typewrite(self.input_text)
                    time.sleep(0.2)
                    
                    # 如果第一次失敗，嘗試使用替代文字
                    pyautogui.typewrite(['backspace'] * len(self.input_text))  # 清除可能的錯誤輸入
                    pyautogui.typewrite(self.alt_input_text)
                    time.sleep(0.2)
                    
                    # 點擊確認按鈕
                    pyautogui.click(btn_x, btn_y)
                
                pyautogui.click(btn_x, btn_y)
                self._log_button_press()
                
                time.sleep(1)
                return True
        
        return False
    
    def start(self):
        """
        Start the key wizard scanning loop.
        """
        if not self._load_templates():
            self.logger.error("Failed to load templates")
            return
            
        self.running = True
        scan_count = 0
        
        try:
            while self.running:
                scan_count += 1
                if self._process_action():
                    self.logger.info("Action completed successfully")
                
                time.sleep(self.scan_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Key Wizard stopped by user")
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
        finally:
            self.running = False
    
    def stop(self, reason="手動停止"):
        """
        Stop the Key Wizard.
        
        Args:
            reason (str): Reason for stopping
        """
        if self.running:
            self.running = False
            self.logger.info(f"Key Wizard stopping: {reason}")
            print(f"按鍵精靈正在停止: {reason}")
            
            # Send Line notification about stopping
            self._send_line_notification(reason)

# Export both classes at the end of the file
__all__ = ['KeyWizard', 'LineNotifier']