"""人工接管相关工具函数"""
import logging
import time
import os
from browser_core.chrome_driver import ChromeDriver
from browser_tools.screenshot import take_screenshot

# 全局浏览器实例
browser = None

def set_browser_instance(driver_instance: ChromeDriver):
    """设置全局浏览器实例"""
    global browser
    browser = driver_instance

def request_human_intervention(reason: str) -> dict:
    """
    请求人工介入操作浏览器
    
    当LLM遇到无法处理的情况（如登录、验证码、复杂弹窗等）时，
    调用此工具暂停自动化流程，等待用户手动操作，完成后继续自动化。
    
    参数:
        reason: 需要人工介入的原因描述
        
    返回:
        包含操作结果的字典，包括是否成功、用户操作后的URL和消息
    """
    if not browser:
        return {"success": False, "message": "浏览器实例未初始化", "current_url": None}
    
    try:
        current_url = browser.get_current_url()
        logging.info(f"请求人工介入 - 原因: {reason}，当前URL: {current_url}")
        
        # 截取当前状态的截图
        screenshot_result = take_screenshot(f"human_handoff_before_{reason}")
        
        # 显示人工介入提示
        print("\n" + "="*80)
        print(f"⚠️ 需要人工介入 ⚠️")
        print(f"原因: {reason}")
        print(f"当前页面: {current_url}")
        if screenshot_result["success"]:
            print(f"当前页面截图已保存至: {screenshot_result['screenshot_path']}")
        print("\n请在浏览器中完成必要操作，完成后按以下说明继续:")
        print("- 输入 'done' 并按回车继续自动化流程")
        print("- 输入 'abort' 并按回车终止任务")
        print("- 输入 'help' 并按回车查看帮助")
        print("="*80 + "\n")
        
        # 等待用户输入
        user_input = ""
        while user_input.lower() not in ["done", "abort"]:
            user_input = input("请输入指令 (done/abort/help): ").strip()
            
            if user_input.lower() == "help":
                print("\n帮助信息:")
                print("- 完成所需操作后输入 'done' 继续自动化")
                print("- 输入 'abort' 终止当前任务")
                print("- 操作期间可以自由浏览、登录或进行任何必要的交互")
                print("- 确保在输入 'done' 前已导航到希望自动化继续的页面\n")
        
        # 处理用户输入
        if user_input.lower() == "abort":
            print("\n任务已被用户终止。")
            return {
                "success": False,
                "aborted": True,
                "current_url": browser.get_current_url(),
                "message": "任务已被用户终止"
            }
        
        # 用户完成操作，获取新状态
        new_url = browser.get_current_url()
        take_screenshot(f"human_handoff_after_{reason}")
        
        print(f"\n已恢复自动化流程，当前页面: {new_url}")
        print("="*80 + "\n")
        
        return {
            "success": True,
            "aborted": False,
            "previous_url": current_url,
            "current_url": new_url,
            "message": f"人工介入完成，已从 {current_url} 导航到 {new_url}"
        }
        
    except Exception as e:
        logging.error(f"人工介入过程中发生错误: {str(e)}")
        return {
            "success": False,
            "current_url": browser.get_current_url() if browser else None,
            "message": f"人工介入失败: {str(e)}"
        }
