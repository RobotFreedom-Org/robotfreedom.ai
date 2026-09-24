import asyncio
import json
import websockets

# Server configuration
HOST = "localhost"
PORT = 8765

async def read_file(path: str): 
    try:
        with open(path, "r", encoding="utf-8") as f:
            return {"content": [f.read()], "isError":False}
    except Exception as e: 
        return {"content": [str(e)], "isError":True}
    
# Custom exception for protocol errors
class ProtocolError(Exception):
    pass

async def ping_pong(message: str) -> str:
    """
    Process incoming JSON messages and return a JSON response.
    """
    try:
        data = json.loads(message)
        if not isinstance(data, dict):
            raise ProtocolError("Message must be a JSON object.")

        command = data.get("command")
        payload = data.get("payload", {})

        if command == "ping":
            return json.dumps({"status": "ok", "response": "pong"})
        
        elif command == "echo":
            return json.dumps({"status": "ok", "response": payload})
        else:
            return json.dumps({"status": "error", "error": f"Unknown command: {command}"})

    except json.JSONDecodeError:
        return json.dumps({"status": "error", "error": "Invalid JSON"})
    except ProtocolError as e:
        return json.dumps({"status": "error", "error": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "error": f"Internal server error: {e}"})

async def my_path_handler(data):  
        args = data["params"]["arguments"]
        filepath = args.get("path") 
        content =  await read_file(filepath) 
        return json.dumps(content)

async def tools_list_handler(websocket):  
        """
        list_files
        query
        insert
        delete
        query_wikipedia
        query_youtube

        send_email
        music
        ping_pong
        
        read_file
        """
        return {"tools":[
                 {
                   "name": "read_file",
                   "title": "Read File",
                   "description": "Read a file from remote server",
                   "inputSchema": {
                     "type": "object",
                     "properties": {
                       "path": {
                         "type": "string",
                         "description": "The file name."
                       }
                     },
                     "required": ["path"]
                   }
                 } ,
                 {
                   "name": "get_weather",
                   "title": "Weather Information Provider",
                   "description": "Get current weather information for a location",
                   "inputSchema": {
                     "type": "object",
                     "properties": {
                       "location": {
                         "type": "string",
                         "description": "City name or zip code"
                       }
                     },
                     "required": ["location"]
                   }
                 } 
               ]}

async def handler(websocket):

    """
    * **Tools**: Executable functions that AI applications can invoke to perform actions (e.g., file operations, API calls, database queries)
    * **Resources**: Data sources that provide contextual information to AI applications (e.g., file contents, database records, API responses)
    * **Prompts**: Reusable templates that help structure interactions with language models (e.g., system prompts, few-shot examples)
    """ 
    print(websocket)
    websocket = json.loads(websocket)
    if websocket["method"] == "tools/list":
        return await tools_list_handler(websocket)
        #await websocket.close() 
    elif websocket["method"]== "tools/get":
        return await my_path_handler(websocket)
        
        #await websocket.close()
    elif websocket["method"]== "tools/call":
        return await my_path_handler(websocket)
        #await websocket.close() 
    elif websocket["method"] == "resources/list":
        await my_path_handler(websocket)
        #await websocket.close() 
    elif websocket["method"] == "resources/get":
        await my_path_handler(websocket)
        #await websocket.close() 
    elif websocket["method"] == "prompts/list":
        await my_path_handler(websocket)
        #await websocket.close() 
    elif websocket["method"] == "prompts/get":
        await my_path_handler(websocket)
        #await websocket.close() 

    elif websocket["method"] == "tasks/list":
        await my_path_handler(websocket)
       # await websocket.close() 
    elif websocket["method"] == "tasks/get":
        await my_path_handler(websocket)
        #await websocket.close() 


    else:
        print(f"No handler for path {websocket["method"]}. Bye bye")
        await websocket.close()

async def client_handler(websocket):
    """
    Handle a connected client.
    """
    async for message in websocket:
        response = await handler(message)
        await websocket.send(json.dumps(response))

async def main():
    """
    Start the WebSocket server.
    """
    async with websockets.serve(client_handler, HOST, PORT):
        print(f"Server running on ws://{HOST}:{PORT}")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")
""" 
import asyncio
import websockets
import json

async def test_client():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"command": "ping"}))
        print("Ping response:", await ws.recv())

        await ws.send(json.dumps({"command": "echo", "payload": {"msg": "Hello"}}))
        print("Echo response:", await ws.recv())

asyncio.run(test_client())
""" 
 