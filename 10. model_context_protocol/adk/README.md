# Model Context Protocol (MCP) Agent - ADK Implementation

This directory contains an implementation of an MCP (Model Context Protocol) agent using Google's ADK (Agent Development Kit) framework. The agent demonstrates how to integrate MCP tools with ADK agents to provide filesystem management capabilities.

## Overview

The MCP agent is a filesystem assistant that can help users manage files within a designated directory. It uses the Model Context Protocol to communicate with a filesystem server, enabling file operations like listing, reading, and writing files.

## Architecture

```
adk/
├── mcp_agent/
│   ├── __init__.py          # Package initialization
│   ├── agent.py             # Main agent implementation
│   ├── README.md            # This file
│   └── mcp_managed_files/   # Directory managed by the agent
│       └── my_file.txt      # Sample managed file
```

## Features

- **File Management**: List, read, and write files in the managed directory
- **MCP Integration**: Uses Model Context Protocol for tool communication
- **ADK Framework**: Built on Google's Agent Development Kit
- **Gemini Model**: Powered by Gemini 2.0 Flash model

## Prerequisites

Before running this agent, ensure you have:

1. **Google ADK installed**:
   ```bash
   pip install google-adk
   ```

2. **Node.js and npm** (for the MCP filesystem server):
   ```bash
   # The agent uses npx to run the MCP filesystem server
   # Ensure you have Node.js installed
   node --version
   npm --version
   ```

3. **API Keys**: Make sure you have the necessary API keys configured for the Gemini model.

## Agent Configuration

The agent is configured with the following settings:

- **Model**: `gemini-2.0-flash`
- **Name**: `filesystem_assistant_agent`
- **Target Directory**: `./mcp_managed_files/`
- **MCP Server**: `@modelcontextprotocol/server-filesystem`

## Running with ADK Web Command

To run this MCP agent using the ADK web interface:

### 1. Navigate to the Project Directory

```bash
cd /workspaces/agentic_design_patterns/10.\ model_context_protocol/adk
```

### 2. Start the ADK Web Interface

```bash
adk web
```

This command will:
- Start the ADK web server
- Automatically detect the `mcp_agent` package
- Make the filesystem assistant agent available in the web interface

### 3. Access the Web Interface

Once the server starts, you'll see output similar to:
```
Starting ADK web server...
Server running at http://localhost:8080
```

Open your browser and navigate to `http://localhost:8080` to access the agent interface.

### 4. Interact with the Agent

In the web interface, you can interact with the filesystem assistant agent by:

- **Listing files**: Ask "What files are in the directory?"
- **Reading files**: Ask "Can you read the contents of my_file.txt?"
- **Writing files**: Ask "Please create a new file called 'example.txt' with some sample content"
- **File operations**: Perform various file management tasks

## Example Interactions

Here are some example prompts you can try with the agent:

```
"List all files in the managed directory"
"Read the contents of my_file.txt"
"Create a new file called notes.txt with the content 'Hello, MCP!'"
"Delete the file my_file.txt"
"Show me the directory structure"
```

## Technical Details

### Agent Implementation

The agent (`agent.py`) creates an LlmAgent with:
- Gemini 2.0 Flash model for natural language processing
- MCP toolset for filesystem operations
- Stdio server parameters for MCP communication

### MCP Integration

The agent uses the `McpToolset` with:
- **Command**: `npx`
- **Arguments**: `["-y", "@modelcontextprotocol/server-filesystem", TARGET_FOLDER_PATH]`
- **Protocol**: Standard I/O communication with the MCP server

### Directory Management

The agent operates within the `mcp_managed_files/` directory, which is:
- Automatically created if it doesn't exist
- Used as the root directory for all file operations
- Isolated from the rest of the filesystem for security

## Troubleshooting

### Common Issues

1. **Node.js not found**: Ensure Node.js is installed and accessible via `npx`
2. **Permission errors**: Check file permissions in the target directory
3. **API key issues**: Verify your Gemini API key is properly configured
4. **Port conflicts**: If port 8080 is in use, the ADK web command will use an alternative port

### Debug Mode

To run with debug output:
```bash
adk web --debug
```

### Logs

Check the ADK logs for detailed information about agent execution and MCP communication.

## Customization

### Changing the Target Directory

Modify the `TARGET_FOLDER_PATH` in `agent.py`:
```python
TARGET_FOLDER_PATH = "/path/to/your/custom/directory"
```

### Using Different MCP Servers

Replace the MCP server in the toolset configuration:
```python
McpToolset(
    connection_params=StdioServerParameters(
        command='npx',
        args=["-y", "@modelcontextprotocol/server-custom", TARGET_FOLDER_PATH]
    ),
)
```

### Model Configuration

Change the model or add additional parameters:
```python
root_agent = LlmAgent(
    model="gemini-pro",  # Different model
    temperature=0.7,     # Add temperature control
    # ... other parameters
)
```

## Contributing

When extending this agent:
1. Follow ADK best practices
2. Ensure MCP protocol compatibility
3. Add proper error handling
4. Update this README with new features

## References

- [Google ADK Documentation](https://developers.google.com/adk)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Filesystem Server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)