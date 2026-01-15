#!/usr/bin/env python3
"""
Text File Summarizer Agent
Uses the Claude Agent SDK to read and summarize text files
"""

from claude_agent_sdk import query, ClaudeAgentOptions
import asyncio
import sys


async def summarize_file(file_path: str):
    """
    Read a text file and generate a summary using Claude Agent SDK

    Args:
        file_path: Path to the text file to summarize
    """
    # Configure the agent options
    options = ClaudeAgentOptions(
        allowed_tools=["Read"],  # Allow the built-in Read tool
        system_prompt="""You are a text summarization assistant. Your job is to read files and create brief summaries that are SHORTER than the original text.

Rules:
- Only output the summary, nothing else
- Keep summaries to 3-5 sentences maximum
- Focus only on the main points and key takeaways
- Do NOT include the original file content
- Do NOT add explanations about what you're doing
- Be concise and direct""",
        permission_mode="acceptEdits"  # Automatically accept file read permissions
    )

    # Create the prompt for the agent
    prompt = f"Read {file_path} and provide ONLY a brief 3-5 sentence summary. Do not include the original text. Just the summary."

    print(f"\n{'='*60}")
    print(f"Text File Summarizer Agent")
    print(f"{'='*60}")
    print(f"Reading file: {file_path}\n")

    # Query the agent
    async for message in query(prompt=prompt, options=options):
        print(message, end="", flush=True)

    print(f"\n\n{'='*60}\n")


async def main():
    """Main entry point for the summarizer agent"""
    if len(sys.argv) < 2:
        print("Usage: python text_summarizer_agent.py <file_path>")
        print("\nExample:")
        print("  python text_summarizer_agent.py sample.txt")
        sys.exit(1)

    file_path = sys.argv[1]
    await summarize_file(file_path)


if __name__ == "__main__":
    asyncio.run(main())
