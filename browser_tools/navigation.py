"""浏览器导航相关工具函数"""
import logging
from browser_core.chrome_driver import ChromeDriver

# 全局浏览器驱动实例
browser = None

def set_browser_instance(driver_instance: ChromeDriver):
    """设置全局浏览器实例"""
    global browser
    browser = driver_instance

def go_to_url(url: str) -> dict:
    """
    导航到指定的URL地址
    
    参数:
        url: 需要导航到的网页URL
        
    返回:
        包含操作结果的字典，包括是否成功、当前URL和消息
    """
    if not browser:
        return {"success": False, "message": "浏览器实例未初始化", "current_url": None}
    
    try:
        success = browser.navigate(url)
        current_url = browser.get_current_url()
        return {
            "success": success,
            "current_url": current_url,
            "message": f"已导航到 {url}" if success else f"导航到 {url} 失败"
        }
    except Exception as e:
        logging.error(f"导航到URL {url} 时发生错误: {str(e)}")
        return {
            "success": False,
            "current_url": browser.get_current_url(),
            "message": f"导航失败: {str(e)}"
        }

def go_back() -> dict:
    """
    导航到浏览器历史记录中的上一页
    
    返回:
        包含操作结果的字典，包括是否成功、当前URL和消息
    """
    if not browser:
        return {"success": False, "message": "浏览器实例未初始化", "current_url": None}
    
    try:
        previous_url = browser.get_current_url()
        success = browser.go_back()
        current_url = browser.get_current_url()
        return {
            "success": success,
            "current_url": current_url,
            "message": f"已从 {previous_url} 后退到 {current_url}" if success else "后退操作失败"
        }
    except Exception as e:
        logging.error(f"后退操作发生错误: {str(e)}")
        return {
            "success": False,
            "current_url": browser.get_current_url(),
            "message": f"后退失败: {str(e)}"
        }

def go_forward() -> dict:
    """
    导航到浏览器历史记录中的下一页
    
    返回:
        包含操作结果的字典，包括是否成功、当前URL和消息
    """
    if not browser:
        return {"success": False, "message": "浏览器实例未初始化", "current_url": None}
    
    try:
        previous_url = browser.get_current_url()
        success = browser.go_forward()
        current_url = browser.get_current_url()
        return {
            "success": success,
            "current_url": current_url,
            "message": f"已从 {previous_url} 前进到 {current_url}" if success else "前进操作失败"
        }
    except Exception as e:
        logging.error(f"前进操作发生错误: {str(e)}")
        return {
            "success": False,
            "current_url": browser.get_current_url(),
            "message": f"前进失败: {str(e)}"
        }
