# MCP Agent Implementation

This module contains the implementation of a filesystem assistant agent using the Model Context Protocol (MCP) and Google's ADK framework.

## Files

- `agent.py`: Main agent implementation with MCP filesystem toolset integration
- `__init__.py`: Package initialization that exposes the agent module
- `mcp_managed_files/`: Directory containing files managed by the agent

## Agent Details

### Configuration

```python
root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name='filesystem_assistant_agent',
    instruction='Help the user manage their files...',
    tools=[McpToolset(...)]
)
```

### MCP Toolset

The agent uses the `@modelcontextprotocol/server-filesystem` MCP server to provide file operations:

- **List Directory**: View files and folders
- **Read File**: Get file contents
- **Write File**: Create or modify files
- **Delete File**: Remove files
- **Create Directory**: Make new folders

### Target Directory

All file operations are scoped to the `mcp_managed_files/` directory for security and isolation.

## Usage

This agent is designed to be run through the ADK web interface. See the parent directory's README for detailed instructions on running with `adk web`.

## Example Capabilities

The agent can handle requests like:
- "Show me all files in the directory"
- "Create a new file with some content"
- "Read the contents of my_file.txt"
- "Delete old files that are no longer needed"
- "Organize the files by creating subdirectories"
