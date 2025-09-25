"""浏览器操作工具包，提供LLM可调用的各种浏览器操作函数"""

from .navigation import go_to_url, go_back, go_forward
from .extraction import get_page_content, find_elements_by_selector, extract_text_by_selector, extract_links, get_current_url
from .interaction import click_element, type_text, scroll_page
from .screenshot import take_screenshot
from .human_handoff import request_human_intervention

# 工具函数列表，用于传递给LLM
TOOL_FUNCTIONS = [
    go_to_url,
    go_back,
    go_forward,
    get_page_content,
    find_elements_by_selector,
    extract_text_by_selector,
    extract_links,
    get_current_url,
    click_element,
    type_text,
    scroll_page,
    take_screenshot,
    request_human_intervention
]

def get_tool_metadata():
    """获取所有工具的元数据，用于LLM理解可用工具"""
    tools = []
    for func in TOOL_FUNCTIONS:
        # 简单提取函数文档字符串作为描述
        description = func.__doc__ or "No description available"
        # 提取函数参数信息
        params = []
        sig = func.__annotations__
        for param, param_type in sig.items():
            if param != 'return':
                params.append({
                    'name': param,
                    'type': param_type.__name__,
                    'description': f"{param} parameter of type {param_type.__name__}"
                })
        
        tools.append({
            'name': func.__name__,
            'description': description.strip(),
            'parameters': params
        })
    return tools
