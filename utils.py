from openai import OpenAI
import json
from pathlib import Path
import yaml
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client
def get_config(name:str)->dict:
    """ 
        获取配置信息 该函数用于读取config目录下的配置文件，并返回指定名称的配置信息。 Args: name (str, optional): 配置项名称，默认为None 
        Returns: Dict: 返回指定名称的配置信息，如果未找到则返回None 
    """ 
    # 读取config目录下的config.yaml文件 
    # 使用 pathlib 构建可靠路径 
    config_path = Path(__file__).parent/ "config" / "config.yaml" 
    with open(config_path, encoding="utf-8") as f: 
        config = yaml.load(f, Loader=yaml.FullLoader) 
    return config.get(name)

def create_llm_client():
    """
    创建并返回一个LLM客户端实例
    
    该函数根据配置获取基础URL和API密钥，如果API密钥为空则使用默认值，
    并相应调整基础URL，最后返回配置好的OpenAI客户端实例。
    
    Returns:
        OpenAI: 配置好的OpenAI客户端实例
    """
    base_url=get_config("base_url")
    api_key=get_config("api_key")
    
    # 如果API密钥为空，则设置为默认值"NONE"，并将基础URL调整为包含/v1路径
    if api_key is None or api_key == "": 
        api_key="NONE"
        base_url=base_url+'/v1'
        
    return OpenAI(api_key=api_key,base_url=base_url)

async def connect_to_stdio_server(server_script_path: str,exit_stack):
        """Connect to an MCP server
        
        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
            
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        
        stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await exit_stack.enter_async_context(ClientSession(stdio, write))
        
        return session
        


if __name__=='__main__':
    print(get_config("base_url"))
    create_llm_client()