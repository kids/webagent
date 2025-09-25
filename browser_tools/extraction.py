"""页面内容提取相关工具函数"""
import logging
from browser_core.chrome_driver import ChromeDriver
from browser_core.page_parser import PageParser

# 全局实例
browser = None
parser = PageParser()

def set_browser_instance(driver_instance: ChromeDriver):
    """设置全局浏览器实例"""
    global browser
    browser = driver_instance

def get_page_content(selector: str = None) -> dict:
    """
    获取当前页面的内容，可以指定CSS选择器来获取特定部分
    
    参数:
        selector: 可选的CSS选择器，用于指定要提取的页面部分
        
    返回:
        包含操作结果的字典，包括是否成功、提取的内容和消息
    """
    if not browser:
        return {"success": False, "message": "浏览器实例未初始化", "content": None}
    
    try:
        page_source = browser.get_page_source()
        if not page_source:
            return {"success": False, "message": "无法获取页面源码", "content": None}
        
        current_url = browser.get_current_url()
        
        if selector:
            content = parser.find_elements_by_selector(page_source, selector)
            message = f"已提取选择器 {selector} 的内容"
        else:
            # 获取元数据和页面文本
            metadata = parser.extract_metadata(page_source)
            content = {
                "metadata": metadata,
                "text_preview": parser.extract_text(page_source)[:5000],  # 限制预览文本长度
                "full_length": len(page_source)
            }
            message = "已提取页面内容"
        
        return {
            "success": True,
            "current_url": current_url,
            "content": content,
            "message": message
        }
    except Exception as e:
        logging.error(f"提取页面内容时发生错误: {str(e)}")
        return {
            "success": False,
            "current_url": browser.get_current_url() if browser else None,
            "content": None,
            "message": f"提取内容失败: {str(e)}"
        }

def find_elements_by_selector(selector: str) -> dict:
    """
    根据CSS选择器查找页面元素
    
    参数:
        selector: 要查找的CSS选择器
        
    返回:
        包含操作结果的字典，包括是否成功、找到的元素列表和消息
    """
    if not browser:
        return {"success": False, "message": "浏览器实例未初始化", "elements": None}
    
    try:
        page_source = browser.get_page_source()
        if not page_source:
            return {"success": False, "message": "无法获取页面源码", "elements": None}
        
        elements = parser.find_elements_by_selector(page_source, selector)
        current_url = browser.get_current_url()
        
        return {
            "success": True,
            "current_url": current_url,
            "elements": elements,
            "message": f"找到 {len(elements)} 个匹配 {selector} 的元素"
        }
    except Exception as e:
        logging.error(f"查找元素 {selector} 时发生错误: {str(e)}")
        return {
            "success": False,
            "current_url": browser.get_current_url() if browser else None,
            "elements": None,
            "message": f"查找元素失败: {str(e)}"
        }

def extract_text_by_selector(selector: str) -> dict:
    """
    根据CSS选择器提取页面文本
    
    参数:
        selector: 要提取文本的CSS选择器
        
    返回:
        包含操作结果的字典，包括是否成功、提取的文本和消息
    """
    if not browser:
        return {"success": False, "message": "浏览器实例未初始化", "text": None}
    
    try:
        page_source = browser.get_page_source()
        if not page_source:
            return {"success": False, "message": "无法获取页面源码", "text": None}
        
        text = parser.extract_text(page_source, selector)
        current_url = browser.get_current_url()
        
        return {
            "success": True,
            "current_url": current_url,
            "text": text,
            "message": f"已提取选择器 {selector} 的文本内容"
        }
    except Exception as e:
        logging.error(f"提取选择器 {selector} 的文本时发生错误: {str(e)}")
        return {
            "success": False,
            "current_url": browser.get_current_url() if browser else None,
            "text": None,
            "message": f"提取文本失败: {str(e)}"
        }

def extract_links() -> dict:
    """
    提取当前页面中的所有链接
    
    返回:
        包含操作结果的字典，包括是否成功、提取的链接列表和消息
    """
    if not browser:
        return {"success": False, "message": "浏览器实例未初始化", "links": None}
    
    try:
        page_source = browser.get_page_source()
        if not page_source:
            return {"success": False, "message": "无法获取页面源码", "links": None}
        
        current_url = browser.get_current_url()
        links = parser.extract_links(page_source, current_url)
        
        return {
            "success": True,
            "current_url": current_url,
            "links": links,
            "message": f"已提取 {len(links)} 个链接"
        }
    except Exception as e:
        logging.error(f"提取页面链接时发生错误: {str(e)}")
        return {
            "success": False,
            "current_url": browser.get_current_url() if browser else None,
            "links": None,
            "message": f"提取链接失败: {str(e)}"
        }

def get_current_url() -> dict:
    """
    获取当前页面的URL地址
    
    返回:
        包含操作结果的字典，包括是否成功、当前URL和消息
    """
    if not browser:
        return {"success": False, "message": "浏览器实例未初始化", "url": None}
    
    try:
        current_url = browser.get_current_url()
        return {
            "success": True,
            "url": current_url,
            "message": "已获取当前页面URL"
        }
    except Exception as e:
        logging.error(f"获取当前URL时发生错误: {str(e)}")
        return {
            "success": False,
            "url": None,
            "message": f"获取URL失败: {str(e)}"
        }
