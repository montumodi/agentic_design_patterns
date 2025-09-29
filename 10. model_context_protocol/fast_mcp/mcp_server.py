from fastmcp import FastMCP, Client

mcp_server = FastMCP()

@mcp_server.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp_server.run(
    transport="http",
    host="127.0.0.1",
    port=8000
)