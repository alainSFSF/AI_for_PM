#!/usr/bin/env python3
"""
Simple Text File Summarizer
Reads a text file and generates a concise summary using Claude API
"""

import anthropic
import os
import sys


def summarize_file(file_path: str):
    """
    Read a text file and generate a brief summary

    Args:
        file_path: Path to the text file to summarize
    """
    # Read the file
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Check if API key is set
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("Set it with: export ANTHROPIC_API_KEY=your-api-key")
        sys.exit(1)

    # Initialize the Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    # Create the summary prompt
    prompt = f"""Read the following text and provide a brief summary in 3-5 sentences.
Focus only on the main points. Output ONLY the summary, nothing else.

Text to summarize:
{content}

Summary:"""

    print(f"\n{'='*60}")
    print(f"Text File Summarizer")
    print(f"{'='*60}")
    print(f"File: {file_path}")
    print(f"Original size: {len(content)} characters\n")
    print("Summary:")
    print("-" * 60)

    # Get the summary from Claude
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,  # Limit output to keep it concise
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    summary = message.content[0].text
    print(summary)
    print("-" * 60)
    print(f"Summary size: {len(summary)} characters")
    print(f"{'='*60}\n")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python simple_summarizer.py <file_path>")
        print("\nExample:")
        print("  python simple_summarizer.py sample.txt")
        sys.exit(1)

    file_path = sys.argv[1]
    summarize_file(file_path)


if __name__ == "__main__":
    main()
