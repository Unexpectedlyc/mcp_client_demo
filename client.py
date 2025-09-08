import asyncio
import json
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession

from utils import (
    connect_to_stdio_server,
    connect_to_sse_server,
    connect_to_streamablehttp_server,
    get_config,
    create_llm_client,
)


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm_client = create_llm_client()

    async def connect_to_server(self):
        """Connect to an MCP server"""
        if get_config("mcp_type") == "stdio":
            server_script_path = get_config("server_script_path")
            self.session = await connect_to_stdio_server(
                server_script_path, self.exit_stack
            )
        elif get_config("mcp_type") == "sse":
            url = get_config("mcp_url")
            self.session = await connect_to_sse_server(url, self.exit_stack)
        elif get_config("mcp_type") == "streamablehttp":
            url = get_config("mcp_url")
            self.session = await connect_to_streamablehttp_server(url, self.exit_stack)
        else:
            raise ValueError("Invalid mcp_type")

        await self.session.initialize()
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [{"role": "user", "content": query}]

        response = await self.session.list_tools()
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in response.tools
        ]

        # Initial API call
        response = self.llm_client.chat.completions.create(
            model=get_config("model"),
            max_tokens=get_config("max_tokens") or 8096,
            messages=messages,
            tools=available_tools,
            tool_choice="auto",
        )

        # Process response and handle tool calls
        final_text = []
        # Extract the function information of the first tool call from the response object, including the function name and arguments
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls is not None:
            messages.append(
                {"role": "assistant", "content": response.choices[0].message.content}
            )
            for function_call in tool_calls:
                function_call = function_call.model_dump()
                function_call = function_call.get("function")
                # Get the name of the tool function
                tool_name = function_call.get("name")
                # Parse the arguments of the tool function, converting the JSON string to a Python object
                tool_args = json.loads(function_call.get("arguments"))
                # Make API call to tool
                tool_response = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                messages.append({"role": "user", "content": tool_response.content})
        else:
            final_text.append(response.choices[0].message.content)
        # Get next response
        response = self.llm_client.chat.completions.create(
            model=get_config("model"),
            max_tokens=get_config("max_tokens") or 8096,
            messages=messages,
        )

        final_text.append(response.choices[0].message.content)
        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    client = MCPClient()
    try:
        await client.connect_to_server()
        a = await client.process_query("获取当前时间")
        print("\n" + a)
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
