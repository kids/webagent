import asyncio
import time
from typing import List, Dict, Any, Callable, Awaitable, Optional
from dataclasses import dataclass
from llm.client import LLMClient, ToolDefinition, LLMResponse
from browser_core.chrome_driver import ChromeDriver
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class AgentState:
    """Agent的状态信息"""
    task: str
    context: List[Dict[str, str]] = None
    current_url: str = ""
    is_human_in_control: bool = False
    last_action: Optional[str] = None
    last_result: Optional[str] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = []

class ToolExecutor:
    """工具执行器，负责调用实际的工具函数"""
    
    def __init__(self, browser: ChromeDriver):
        self.browser = browser
        self.tools = {}
        
    def register_tool(self, name: str, func: Callable[..., Awaitable[Any]], description: str, parameters: Dict[str, str]):
        """注册工具函数"""
        self.tools[name] = {
            "func": func,
            "description": description,
            "parameters": parameters
        }
    
    def get_tool_definitions(self) -> List[ToolDefinition]:
        """获取所有工具的定义，用于传递给LLM"""
        return [
            ToolDefinition(
                name=name,
                description=tool["description"],
                parameters=tool["parameters"]
            ) for name, tool in self.tools.items()
        ]
    
    async def execute(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """执行指定的工具"""
        if tool_name not in self.tools:
            return f"错误：未知工具 '{tool_name}'"
        
        try:
            logger.info(f"执行工具: {tool_name}, 参数: {parameters}")
            tool_func = self.tools[tool_name]["func"]
            result = await tool_func(**parameters)
            
            # 限制结果长度，避免上下文过长
            if isinstance(result, str) and len(result) > 2000:
                result = result[:2000] + "...\n[结果已截断]"
                
            return f"工具 '{tool_name}' 执行成功: {result}"
        except Exception as e:
            error_msg = f"工具 '{tool_name}' 执行失败: {str(e)}"
            logger.error(error_msg)
            return error_msg

class MainAgent:
    """LLM驱动的中央代理，负责协调工具调用和任务执行"""
    
    def __init__(self, task: str):
        self.state = AgentState(task=task)
        self.llm_client = LLMClient()
        self.browser = ChromeDriver()
        self.tool_executor = ToolExecutor(self.browser)
        self.max_iterations = 50  # 最大迭代次数，防止无限循环
    
    async def initialize(self):
        """初始化代理"""
        # 启动浏览器
        await self.browser.start()
        # 注册工具（实际使用时会从browser_tools导入并注册）
        await self._register_tools()
        # 向LLM注册工具定义
        self.llm_client.register_tools(self.tool_executor.get_tool_definitions())
    
    async def _register_tools(self):
        """注册所有可用工具"""
        # 这里只是示例，实际实现时会从browser_tools包中导入真实工具
        # 导航工具
        from browser_tools.navigation import go_to_url, back, forward
        self.tool_executor.register_tool(
            "go_to_url",
            go_to_url,
            "导航到指定的URL",
            {"url": "字符串，要导航到的URL地址"}
        )
        self.tool_executor.register_tool(
            "back",
            back,
            "导航到浏览器历史记录中的上一页",
            {}
        )
        self.tool_executor.register_tool(
            "forward",
            forward,
            "导航到浏览器历史记录中的下一页",
            {}
        )
        
        # 提取工具
        from browser_tools.extraction import get_page_content, extract_text_by_selector
        self.tool_executor.register_tool(
            "get_page_content",
            get_page_content,
            "获取当前页面的内容",
            {"selector": "可选字符串，CSS选择器，用于指定要获取内容的元素，不指定则获取整个页面"}
        )
        self.tool_executor.register_tool(
            "extract_text_by_selector",
            extract_text_by_selector,
            "通过CSS选择器提取页面中特定元素的文本",
            {"selector": "字符串，CSS选择器，用于指定要提取文本的元素"}
        )
        
        # 交互工具
        from browser_tools.interaction import click, type_text, scroll_down, scroll_up
        self.tool_executor.register_tool(
            "click",
            click,
            "点击页面中的元素",
            {"selector": "字符串，CSS选择器，用于指定要点击的元素"}
        )
        self.tool_executor.register_tool(
            "type_text",
            type_text,
            "在页面元素中输入文本",
            {
                "selector": "字符串，CSS选择器，用于指定要输入文本的元素",
                "text": "字符串，要输入的文本内容"
            }
        )
        self.tool_executor.register_tool(
            "scroll_down",
            scroll_down,
            "向下滚动页面",
            {"pixels": "可选整数，要滚动的像素数，默认为500"}
        )
        self.tool_executor.register_tool(
            "scroll_up",
            scroll_up,
            "向上滚动页面",
            {"pixels": "可选整数，要滚动的像素数，默认为500"}
        )
        
        # 截图工具
        from browser_tools.screenshot import take_screenshot
        self.tool_executor.register_tool(
            "take_screenshot",
            take_screenshot,
            "对当前页面进行截图",
            {"description": "可选字符串，对截图的描述"}
        )
        
        # 人工接管工具
        from browser_tools.human_handoff import request_human_intervention
        self.tool_executor.register_tool(
            "request_human_intervention",
            request_human_intervention,
            "请求人工介入处理，当遇到无法自动处理的情况（如登录、验证码）时使用",
            {"reason": "字符串，说明需要人工介入的原因和需要完成的操作"}
        )
    
    async def _get_current_observation(self) -> str:
        """获取当前浏览器状态作为观察结果"""
        url = await self.browser.get_current_url()
        title = await self.browser.get_title()
        
        # 更新状态中的当前URL
        self.state.current_url = url
        
        # 简单的页面摘要，而不是完整内容，避免上下文过长
        summary = f"当前页面: {title} (URL: {url})\n"
        
        # 检查是否处于人工控制状态
        if self.state.is_human_in_control:
            summary += "状态: 等待人工操作完成\n"
        
        return summary
    
    async def run(self) -> str:
        """运行代理，执行任务直到完成或达到最大迭代次数"""
        logger.info(f"开始执行任务: {self.state.task}")
        
        for iteration in range(self.max_iterations):
            logger.info(f"迭代 {iteration + 1}/{self.max_iterations}")
            
            # 获取当前观察结果
            observation = await self._get_current_observation()
            logger.info(f"当前观察: {observation}")
            
            # 将观察结果添加到上下文
            self.state.context.append({"role": "system", "content": f"观察: {observation}"})
            
            # 调用LLM获取下一步行动
            llm_response = await self.llm_client.generate_response(
                user_task=self.state.task,
                context=self.state.context
            )
            
            # 记录LLM的思考过程
            if llm_response.content:
                logger.info(f"LLM思考: {llm_response.content}")
                self.state.context.append({"role": "assistant", "content": llm_response.content})
            
            # 检查任务是否完成
            if llm_response.is_finished:
                logger.info("任务已完成")
                # 请求最终结果整理
                final_response = await self.llm_client.generate_response(
                    user_task=self.state.task,
                    context=self.state.context,
                    is_final=True
                )
                return final_response.content or "任务已完成，但未返回具体结果。"
            
            # 处理工具调用
            if llm_response.tool_call:
                tool_name = llm_response.tool_call.get("name")
                parameters = llm_response.tool_call.get("parameters", {})
                
                # 执行工具
                tool_result = await self.tool_executor.execute(tool_name, parameters)
                logger.info(f"工具执行结果: {tool_result}")
                
                # 将工具结果添加到上下文
                self.state.context.append({
                    "role": "system", 
                    "content": f"工具调用结果: {tool_result}"
                })
                
                # 特殊处理人工接管后的状态
                if tool_name == "request_human_intervention":
                    self.state.is_human_in_control = False  # 人工操作已完成
            else:
                # 如果LLM没有返回工具调用，可能需要进一步提示
                logger.warning("LLM没有返回工具调用指令")
                self.state.context.append({
                    "role": "user", 
                    "content": "请提供具体的工具调用指令来继续完成任务。"
                })
            
            # 短暂延迟，避免操作过快
            await asyncio.sleep(1)
        
        # 如果达到最大迭代次数仍未完成
        logger.warning(f"已达到最大迭代次数 ({self.max_iterations})，任务可能未完成")
        # 请求最终结果整理
        final_response = await self.llm_client.generate_response(
            user_task=self.state.task,
            context=self.state.context,
            is_final=True
        )
        return final_response.content or f"已达到最大迭代次数 ({self.max_iterations})，任务可能未完成。"
    
    async def shutdown(self):
        """关闭代理，清理资源"""
        await self.browser.stop()
        await self.llm_client.close()
        logger.info("代理已关闭")
