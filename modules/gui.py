import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from PIL import Image, ImageTk
import threading
import cv2

from .key_wizard import KeyWizard
from .line_notifier import LineNotifier

class TextRedirector:
    """
    Redirect console output to a Tkinter Text widget.
    """
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, string):
        self.buffer += string
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)
        
    def flush(self):
        pass

class KeyWizardGUI:
    """
    Main GUI class for the Key Wizard application.
    """
    def __init__(self, root):
        """
        Initialize the GUI.
        
        Args:
            root (tk.Tk): Root Tkinter window
        """
        self.root = root
        self.root.title("Key Wizard - Visual Interface")
        self.root.geometry("900x700")  # 增加寬度以容納新按鈕
        self.root.minsize(900, 700)
        
        # 修正這裡：先定義 _on_closing 方法，再設置協議
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 設定版本號
        self.version = "3.1"
        
        # 設定日誌
        self.logger = logging.getLogger('key_wizard')
        
        # Script directory
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # LINE Notifier
        self.line_notifier = LineNotifier()
        
        # Initialize wizard and thread
        self.wizard = None
        self.wizard_thread = None
        
        # Setup GUI
        self._setup_styles()
        self._create_widgets()
        self._load_sample_images()
        
        # Redirect stdout
        sys.stdout = TextRedirector(self.log_text)
    
    def _on_closing(self):
        """
        Handle application closing.
        確保在關閉應用程式時，所有線程都被正確停止
        """
        # 停止精靈
        if self.wizard:
            self.wizard.stop()
        
        # 如果有活動線程，等待其結束
        if self.wizard_thread and self.wizard_thread.is_alive():
            self.wizard_thread.join(1.0)
        
        # 恢復標準輸出
        sys.stdout = sys.__stdout__
        
        # 銷毀主窗口
        self.root.destroy()
    
    def _setup_styles(self):
        """
        Configure Tkinter styles.
        """
        self.style = ttk.Style()
        self.style.configure("TButton", font=('微軟正黑體', 10))
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", font=('微軟正黑體', 10), background="#f0f0f0")
    
    def _create_widgets(self):
        """
        Create and layout GUI widgets.
        """
        # 其餘代碼保持不變
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Control frame
        control_frame = ttk.Frame(main_frame, padding="5")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 按鈕組
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.LEFT, padx=5)
        
        self.start_button = ttk.Button(button_frame, text="啟動精靈", command=self._start_wizard)
        self.start_button.pack(side=tk.TOP, padx=5, pady=2)
        
        self.stop_button = ttk.Button(button_frame, text="停止精靈", command=self._stop_wizard, state=tk.DISABLED)
        self.stop_button.pack(side=tk.TOP, padx=5, pady=2)
        
        # 功能設定組
        settings_frame = ttk.LabelFrame(control_frame, text="設定")
        settings_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # 直接點擊模式選項
        self.direct_click_var = tk.BooleanVar(value=True)
        self.direct_click_check = ttk.Checkbutton(
            settings_frame, 
            text="直接點擊模式", 
            variable=self.direct_click_var
        )
        self.direct_click_check.pack(anchor=tk.W, padx=5, pady=2)
        
        # 說明文字
        settings_label = ttk.Label(
            settings_frame, 
            text="直接點擊模式可解決輸入法問題",
            font=("微軟正黑體", 8)
        )
        settings_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Line通知按鈕
        self.line_notify_button = ttk.Button(settings_frame, text="發送Line訊息", command=self._send_line_message)
        self.line_notify_button.pack(anchor=tk.W, padx=5, pady=5)
        
        # 狀態顯示
        status_container = ttk.Frame(control_frame)
        status_container.pack(side=tk.LEFT, padx=20, fill=tk.BOTH, expand=True)
        
        status_label = ttk.Label(status_container, text="狀態:")
        status_label.pack(anchor=tk.W)
        
        self.status_var = tk.StringVar(value="準備就緒")
        status_display = ttk.Label(status_container, textvariable=self.status_var, font=("微軟正黑體", 10, "bold"))
        status_display.pack(anchor=tk.W)
        
        # 其餘部分保持不變
        # Image preview frame
        image_frame = ttk.LabelFrame(main_frame, text="偵測到的圖片", padding="5")
        image_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Image containers
        image_container_frame = ttk.Frame(image_frame)
        image_container_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Image labels
        self.img_labels = {}
        img_names = ["target", "button", "approved", "stop"]
        img_texts = ["目標圖片", "按鈕圖片", "核准圖片", "停止圖片"]
        
        for i, (name, text) in enumerate(zip(img_names, img_texts)):
            frame = ttk.Frame(image_container_frame)
            frame.grid(row=0, column=i, padx=10, pady=5)
            
            label = ttk.Label(frame, text=text)
            label.pack()
            
            img_label = ttk.Label(frame, background="white")
            img_label.pack(padx=5, pady=5)
            
            self.img_labels[name] = img_label
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="運行日誌", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Log text widget
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 狀態欄
        self.status_bar = ttk.Label(self.root, text=f"版本: {self.version} | 作者: yanchen", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _start_wizard(self):
        """
        Start the wizard in a separate thread.
        """
        if not self.wizard or not self.wizard_thread or not self.wizard_thread.is_alive():
            # 將設定傳遞給精靈
            self.wizard = KeyWizard(
                gui=self, 
                line_notifier=self.line_notifier,
                direct_click_mode=self.direct_click_var.get()
            )
            self.wizard_thread = threading.Thread(target=self.wizard.start)
            self.wizard_thread.daemon = True
            self.wizard_thread.start()
            
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.direct_click_check.config(state=tk.DISABLED)  # 啟動時禁用設定選項
            self.status_var.set("精靈運行中...")
    
    def _stop_wizard(self):
        """
        Stop the wizard.
        """
        if self.wizard and self.wizard_thread and self.wizard_thread.is_alive():
            # 更新設定
            self.wizard.direct_click_mode = self.direct_click_var.get()
            self.wizard.stop(reason="手動停止")
            self.wizard_thread.join(1.0)
            
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.direct_click_check.config(state=tk.NORMAL)  # 停止時允許設定
        self.status_var.set("已停止")
    
    def _send_line_message(self):
        """
        Open a dialog to send a Line message
        """
        try:
            # 彈出輸入對話框，讓用戶輸入訊息內容
            message = simpledialog.askstring(
                "Line 訊息", 
                "請輸入訊息內容:", 
                parent=self.root
            )
            
            if message:
                # 發送訊息
                result = self.line_notifier.send_message(message)
                
                if result:
                    messagebox.showinfo("Line 訊息", "訊息發送成功！")
                    self.log_text.config(state=tk.NORMAL)
                    self.log_text.insert(tk.END, f"Line訊息已發送: {message}\n")
                    self.log_text.see(tk.END)
                    self.log_text.config(state=tk.DISABLED)
                else:
                    messagebox.showerror("Line 訊息", "訊息發送失敗，請檢查 Line Notify 設定")
        
        except Exception as e:
            messagebox.showerror("錯誤", f"發送訊息時發生錯誤: {str(e)}")
            self.logger.error(f"Line message send error: {e}")
    
    def _load_sample_images(self):
        """
        Load and display sample images.
        """
        img_paths = {
            "target": os.path.join(self.script_dir, "keep.png"),
            "button": os.path.join(self.script_dir, "btn.png"),
            "approved": os.path.join(self.script_dir, "approved.png"),
            "stop": os.path.join(self.script_dir, "stop.png")
        }
        
        for key, path in img_paths.items():
            if os.path.exists(path):
                try:
                    img = Image.open(path)
                    img.thumbnail((100, 100))
                    tk_img = ImageTk.PhotoImage(img)
                    self.img_labels[key].configure(image=tk_img)
                    self.img_labels[key].image = tk_img
                except Exception as e:
                    self.logger.error(f"Error loading image {path}: {str(e)}")
    
    def update_status(self, text):
        """
        Update status display.
        
        Args:
            text (str): Status text to display
        """
        self.status_var.set(text)
    
    def update_image(self, name, image):
        """
        Update image display.
        
        Args:
            name (str): Image label name
            image (np.ndarray): OpenCV image
        """
        if image is not None:
            try:
                # Convert OpenCV image to PIL format
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(image_rgb)
                
                # Resize for display
                pil_img.thumbnail((100, 100))
                
                # Convert to Tkinter format
                tk_img = ImageTk.PhotoImage(pil_img)
                
                # Update image
                self.img_labels[name].configure(image=tk_img)
                self.img_labels[name].image = tk_img
            except Exception as e:
                self.logger.error(f"Error updating image: {str(e)}")
