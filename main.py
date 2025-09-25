import asyncio
import argparse
from agent.main_agent import MainAgent
from utils.logger import setup_logger

async def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='LLM驱动的浏览器代理，用于自动化网络信息收集任务')
    parser.add_argument('--task', type=str, required=True, help='要执行的任务描述')
    parser.add_argument('--log-level', type=str, default='INFO', help='日志级别 (DEBUG, INFO, WARNING, ERROR)')
    args = parser.parse_args()
    
    # 配置日志
    setup_logger(args.log_level)
    
    # 创建并初始化代理
    agent = MainAgent(task=args.task)
    try:
        await agent.initialize()
        # 运行代理执行任务
        result = await agent.run()
        # 输出最终结果
        print("\n" + "="*50)
        print("任务执行结果:")
        print("="*50)
        print(result)
    finally:
        # 确保资源被正确释放
        await agent.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
