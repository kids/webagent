import asyncio
import json
from typing import Any, Dict, List, Optional, Callable, Awaitable
from pydantic import BaseModel
import aiohttp
from config.settings import config
from config.prompts import SYSTEM_PROMPT, TOOL_CALL_FORMAT

class ToolDefinition(BaseModel):
    """工具定义模型，用于描述可供LLM调用的工具"""
    name: str
    description: str
    parameters: Dict[str, Any]

class LLMResponse(BaseModel):
    """LLM响应模型"""
    content: Optional[str] = None
    tool_call: Optional[Dict[str, Any]] = None
    is_finished: bool = False

class LLMClient:
    """LLM API客户端，支持异步函数调用"""
    
    def __init__(self):
        self.api_key = config.llm.api_key
        self.base_url = config.llm.base_url
        self.model_name = config.llm.model_name
        self.temperature = config.llm.temperature
        self.max_tokens = config.llm.max_tokens
        self.session = aiohttp.ClientSession()
        self.tools: List[ToolDefinition] = []
        
    async def close(self):
        """关闭HTTP会话"""
        await self.session.close()
    
    def register_tools(self, tools: List[ToolDefinition]):
        """注册可供LLM调用的工具"""
        self.tools = tools
    
    def _format_tools_for_prompt(self) -> str:
        """将工具定义格式化为适合提示词的字符串"""
        if not self.tools:
            return "没有可用工具"
            
        tools_str = "可用工具列表：\n"
        for tool in self.tools:
            tools_str += f"- {tool.name}: {tool.description}\n"
            tools_str += "  参数：\n"
            for param_name, param_info in tool.parameters.items():
                tools_str += f"    {param_name}: {param_info}\n"
        return tools_str
    
    async def _call_openai_api(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """调用OpenAI兼容的API"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        async with self.session.post(url, headers=headers, json=payload) as response:
            if response.status != 200:
                raise Exception(f"LLM API调用失败: {await response.text()}")
            return await response.json()
    
    async def generate_response(
        self, 
        user_task: str, 
        context: List[Dict[str, str]],
        is_final: bool = False
    ) -> LLMResponse:
        """
        生成LLM响应
        
        参数:
            user_task: 用户的原始任务
            context: 对话上下文，包含之前的观察和工具调用结果
            is_final: 是否请求最终回答
        
        返回:
            LLMResponse对象，包含响应内容和可能的工具调用
        """
        # 构建系统提示词
        system_message = SYSTEM_PROMPT
        
        # 如果有工具，添加工具信息
        if self.tools and not is_final:
            system_message += "\n\n" + self._format_tools_for_prompt()
            system_message += "\n\n" + TOOL_CALL_FORMAT
        
        # 构建消息列表
        messages = [{"role": "system", "content": system_message}]
        # 添加用户任务
        messages.append({"role": "user", "content": f"任务：{user_task}"})
        # 添加上下文
        messages.extend(context)
        
        # 如果是请求最终回答，提示LLM整理结果
        if is_final:
            messages.append({
                "role": "user", 
                "content": "请根据以上信息，整理最终结果，确保格式清晰、内容完整。"
            })
        
        # 调用LLM API
        try:
            response = await self._call_openai_api(messages)
            content = response["choices"][0]["message"]["content"]
            
            # 检查是否包含工具调用
            tool_call = None
            if "<tool_call>" in content and "</tool_call>" in content:
                start = content.find("<tool_call>") + len("<tool_call>")
                end = content.find("</tool_call>")
                tool_call_str = content[start:end].strip()
                
                try:
                    tool_call = json.loads(tool_call_str)
                    # 提取纯文本内容（不包含工具调用部分）
                    content = content[:start - len("<tool_call>")] + content[end + len("</tool_call>"):]
                    content = content.strip()
                except json.JSONDecodeError:
                    # 如果解析失败，将整个内容视为普通文本
                    content = content
                    tool_call = None
            
            # 判断是否完成任务
            is_finished = is_final or ("任务已完成" in content and not tool_call)
            
            return LLMResponse(
                content=content,
                tool_call=tool_call,
                is_finished=is_finished
            )
        except Exception as e:
            return LLMResponse(
                content=f"调用LLM时发生错误: {str(e)}",
                tool_call=None,
                is_finished=False
            )
