import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class LLMConfig:
    """LLM模型配置"""
    model_name: str = os.getenv("LLM_MODEL_NAME", "gpt-4o")
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    base_url: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    temperature: float = 0.2
    max_tokens: int = 4096

@dataclass
class BrowserConfig:
    """浏览器配置"""
    driver_path: Optional[str] = None  # 如果未指定，将使用系统默认
    headless: bool = False  # 默认显示浏览器窗口，方便人工接管
    default_search_engine: str = "https://www.google.com/search?q="
    user_agent: Optional[str] = None

@dataclass
class AppConfig:
    """应用程序全局配置"""
    llm: LLMConfig = LLMConfig()
    browser: BrowserConfig = BrowserConfig()
    data_dir: str = "data"
    output_dir: str = os.path.join("data", "outputs")
    log_dir: str = os.path.join("data", "logs")
    screenshot_dir: str = os.path.join("data", "screenshots")

# 初始化配置
config = AppConfig()

# 确保数据目录存在
for dir_path in [config.data_dir, config.output_dir, config.log_dir, config.screenshot_dir]:
    os.makedirs(dir_path, exist_ok=True)
