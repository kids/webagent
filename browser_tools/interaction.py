"""页面交互相关工具函数"""
import logging
from selenium.webdriver.common.by import By
from browser_core.chrome_driver import ChromeDriver

# 全局浏览器实例
browser = None

def set_browser_instance(driver_instance: ChromeDriver):
    """设置全局浏览器实例"""
    global browser
    browser = driver_instance

def click_element(selector: str, selector_type: str = "css") -> dict:
    """
    点击页面上的指定元素
    
    参数:
        selector: 元素的选择器字符串
        selector_type: 选择器类型，可选值为 "css" 或 "xpath"，默认为 "css"
        
    返回:
        包含操作结果的字典，包括是否成功、当前URL和消息
    """
    if not browser:
        return {"success": False, "message": "浏览器实例未初始化", "current_url": None}
    
    try:
        # 确定选择器类型
        by = By.CSS_SELECTOR if selector_type.lower() == "css" else By.XPATH
        
        success = browser.click_element(selector, by)
        current_url = browser.get_current_url()
        
        return {
            "success": success,
            "current_url": current_url,
            "message": f"已点击选择器 {selector} 的元素" if success else f"无法点击选择器 {selector} 的元素"
        }
    except Exception as e:
        logging.error(f"点击元素 {selector} 时发生错误: {str(e)}")
        return {
            "success": False,
            "current_url": browser.get_current_url() if browser else None,
            "message": f"点击元素失败: {str(e)}"
        }

def type_text(selector: str, text: str, selector_type: str = "css") -> dict:
    """
    在页面元素中输入文本
    
    参数:
        selector: 元素的选择器字符串
        text: 要输入的文本内容
        selector_type: 选择器类型，可选值为 "css" 或 "xpath"，默认为 "css"
        
    返回:
        包含操作结果的字典，包括是否成功、当前URL和消息
    """
    if not browser:
        return {"success": False, "message": "浏览器实例未初始化", "current_url": None}
    
    try:
        # 确定选择器类型
        by = By.CSS_SELECTOR if selector_type.lower() == "css" else By.XPATH
        
        success = browser.type_text(selector, text, by)
        current_url = browser.get_current_url()
        
        return {
            "success": success,
            "current_url": current_url,
            "message": f"已在选择器 {selector} 的元素中输入文本" if success else f"无法在选择器 {selector} 的元素中输入文本"
        }
    except Exception as e:
        logging.error(f"在元素 {selector} 中输入文本时发生错误: {str(e)}")
        return {
            "success": False,
            "current_url": browser.get_current_url() if browser else None,
            "message": f"输入文本失败: {str(e)}"
        }

def scroll_page(direction: str = "down", pixels: int = None) -> dict:
    """
    滚动页面
    
    参数:
        direction: 滚动方向，可选值为 "down"（向下）或 "up"（向上），默认为 "down"
        pixels: 可选参数，指定滚动的像素数，不指定则滚动到页面底部或顶部
        
    返回:
        包含操作结果的字典，包括是否成功、当前URL和消息
    """
    if not browser:
        return {"success": False, "message": "浏览器实例未初始化", "current_url": None}
    
    try:
        if direction.lower() not in ["down", "up"]:
            return {
                "success": False,
                "current_url": browser.get_current_url(),
                "message": f"无效的滚动方向: {direction}，必须是 'down' 或 'up'"
            }
        
        success = browser.scroll(direction.lower(), pixels)
        current_url = browser.get_current_url()
        
        if pixels:
            message = f"已向{direction}滚动 {pixels} 像素" if success else f"无法向{direction}滚动 {pixels} 像素"
        else:
            pos = "底部" if direction.lower() == "down" else "顶部"
            message = f"已滚动到页面{pos}" if success else f"无法滚动到页面{pos}"
        
        return {
            "success": success,
            "current_url": current_url,
            "message": message
        }
    except Exception as e:
        logging.error(f"页面滚动时发生错误: {str(e)}")
        return {
            "success": False,
            "current_url": browser.get_current_url() if browser else None,
            "message": f"页面滚动失败: {str(e)}"
        }
