import os
import logging

def create_bat_file():
    """
    Create a .bat file to run the key wizard.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bat_path = os.path.join(script_dir, "run_key_wizard.bat")
        
        with open(bat_path, "w", encoding='utf-8') as bat_file:
            bat_file.write('@echo off\n')
            bat_file.write('echo 啟動 Key Wizard 視覺化版本...\n')
            bat_file.write('cd /d "%~dp0"\n')
            bat_file.write('python "main.py"\n')
            bat_file.write('pause\n')
        
        print(f"已創建批次檔: {bat_path}")
        return True
    except Exception as e:
        print(f"創建批次檔失敗: {str(e)}")
        return False

def check_images():
    """
    Check if the required images exist.
    
    Returns:
        bool: True if required images found, False otherwise
    """
    logger = logging.getLogger('key_wizard')
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    required_images = {
        "目標圖片": "keep.png",
        "按鈕圖片": "btn.png"
    }
    
    optional_images = {
        "核准圖片": "approved.png",
        "停止圖片": "stop.png"
    }
    
    # Check required images
    for name, filename in required_images.items():
        path = os.path.join(script_dir, filename)
        if not os.path.exists(path):
            print(f"警告: 找不到{name} '{filename}'")
            print(f"請將 '{filename}' 放在以下目錄: {script_dir}")
            return False
        print(f"找到{name}: {path}")
    
    # Check optional images
    for name, filename in optional_images.items():
        path = os.path.join(script_dir, filename)
        if not os.path.exists(path):
            print(f"注意: 找不到{name} '{filename}'")
            print(f"如果需要對應功能，請將 '{filename}' 放在以下目錄: {script_dir}")
    
    return True