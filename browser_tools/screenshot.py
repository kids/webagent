"""页面截图相关工具函数"""
import logging
import os
from datetime import datetime
from browser_core.chrome_driver import ChromeDriver
from config.settings import Settings

# 全局浏览器实例
browser = None
settings = Settings()

def set_browser_instance(driver_instance: ChromeDriver):
    """设置全局浏览器实例"""
    global browser
    browser = driver_instance

def take_screenshot(description: str = "") -> dict:
    """
    截取当前页面的屏幕截图并保存
    
    参数:
        description: 可选的截图描述，用于文件名
        
    返回:
        包含操作结果的字典，包括是否成功、截图路径、当前URL和消息
    """
    if not browser:
        return {"success": False, "message": "浏览器实例未初始化", "screenshot_path": None, "current_url": None}
    
    try:
        # 确保截图目录存在
        screenshot_dir = os.path.join(settings.DATA_DIR, "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        
        # 生成唯一的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if description:
            # 清理描述中的特殊字符以用于文件名
            safe_desc = "".join([c for c in description if c.isalnum() or c in " _-"]).strip()
            filename = f"screenshot_{timestamp}_{safe_desc}.png"
        else:
            filename = f"screenshot_{timestamp}.png"
        
        file_path = os.path.join(screenshot_dir, filename)
        
        # 截取并保存截图
        success = browser.take_screenshot(file_path)
        current_url = browser.get_current_url()
        
        if success:
            message = f"已保存截图至 {file_path}"
            if description:
                message += f"，描述: {description}"
        else:
            message = "截图保存失败"
        
        return {
            "success": success,
            "current_url": current_url,
            "screenshot_path": file_path if success else None,
            "message": message
        }
    except Exception as e:
        logging.error(f"截取页面截图时发生错误: {str(e)}")
        return {
            "success": False,
            "current_url": browser.get_current_url() if browser else None,
            "screenshot_path": None,
            "message": f"截图失败: {str(e)}"
        }
