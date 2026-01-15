# Text Summarizer Agent - Setup Instructions

This agent uses the Claude Agent SDK to read text files and generate summaries.

## Prerequisites

1. **Install Claude Code CLI** (required for the SDK runtime):
   ```bash
   curl -fsSL https://claude.ai/install.sh | bash
   ```

2. **Install Python Agent SDK**:
   ```bash
   pip install claude-agent-sdk
   ```

3. **Set your Anthropic API key**:
   ```bash
   export ANTHROPIC_API_KEY=your-api-key-here
   ```

   Get your API key from: https://console.anthropic.com/

## Usage

Run the agent with a text file path:

```bash
python text_summarizer_agent.py <file_path>
```

### Examples

Summarize the sample text file:
```bash
python text_summarizer_agent.py sample.txt
```

Summarize any other text file:
```bash
python text_summarizer_agent.py /path/to/your/file.txt
```

## How It Works

1. The agent receives a file path as a command-line argument
2. It uses the Claude Agent SDK's built-in `Read` tool to access the file
3. Claude reads the file content and generates a concise summary
4. The summary is displayed in the terminal

## Agent Configuration

The agent is configured with:
- **Allowed Tools**: `Read` (built-in file reading tool)
- **System Prompt**: Optimized for creating clear, concise summaries
- **Permission Mode**: `acceptEdits` (automatically accepts read permissions)

## Customization

You can modify the agent by editing `text_summarizer_agent.py`:

- **Change the summary style**: Edit the `system_prompt` in `ClaudeAgentOptions`
- **Add more tools**: Include additional tools in the `allowed_tools` list
- **Adjust permissions**: Change `permission_mode` to control how the agent handles permissions

## Troubleshooting

**Error: "ANTHROPIC_API_KEY not set"**
- Make sure you've exported your API key: `export ANTHROPIC_API_KEY=your-key`

**Error: "Module not found: claude_agent_sdk"**
- Install the SDK: `pip install claude-agent-sdk`

**Error: "Claude Code CLI not found"**
- Install Claude Code CLI using the installation command above

## Learn More

- [Claude Agent SDK Documentation](https://platform.claude.com/docs/en/agent-sdk/overview)
- [Custom Tools Guide](https://platform.claude.com/docs/en/agent-sdk/custom-tools)
- [Python SDK Reference](https://platform.claude.com/docs/en/agent-sdk/python)
