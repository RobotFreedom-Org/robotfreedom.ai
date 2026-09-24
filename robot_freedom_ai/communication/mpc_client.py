import asyncio
import json
import websockets

# MCP message helper
def make_request(method, params=None, request_id=1):
    """Create a JSON-RPC 2.0 request for MCP."""
    return json.dumps({
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params or {}
    })

async def call_mcp_tool(uri, tool_name, arguments):
    """
    Connect to MCP server via WebSocket and call a tool.
    
    :param uri: WebSocket URI of the MCP server (e.g., ws://localhost:8080/mcp)
    :param tool_name: Name of the MCP tool to call
    :param arguments: Dictionary of arguments for the tool
    """
    try:
        async with websockets.connect(uri) as ws:
            print(f"Connected to MCP server at {uri}")

            # Example: list available tools
            await ws.send(make_request("tools/list", {}))
            tools_response = await ws.recv()
            print("Available tools:", tools_response)

            # Call the specified tool
            await ws.send(make_request("tools/call", {
                "name": tool_name,
                "arguments": arguments
            }, request_id=2))

            # Wait for tool response
            response = await ws.recv()
            print("Tool response:", response)

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed unexpectedly: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Example usage
    # Replace with your MCP server WebSocket endpoint and tool details

    HOST = "localhost"
    PORT = 8765
    file_path = "mpc_client.py" 
    asyncio.run(call_mcp_tool(
        uri="ws://localhost:8765",
        tool_name="read_file",   
        arguments={"path": file_path}
    ))
    
    """
    PORT = 8765
    asyncio.run(call_mcp_tool(
        uri="ws://localhost:8765",
        tool_name="math.add",  # Example tool name
        arguments={"a": 5, "b": 7}
    ))
    """ 

