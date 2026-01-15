# Simple Text Summarizer - Setup Instructions

A straightforward Python script that reads text files and generates concise summaries using Claude.

## Prerequisites

1. **Install the Anthropic Python library**:
   ```bash
   pip install anthropic
   ```

2. **Set your Anthropic API key**:
   ```bash
   export ANTHROPIC_API_KEY=your-api-key-here
   ```

   Get your API key from: https://console.anthropic.com/

## Usage

Run the summarizer with a text file path:

```bash
python simple_summarizer.py <file_path>
```

### Examples

Summarize the sample text file:
```bash
python simple_summarizer.py sample.txt
```

Summarize any other text file:
```bash
python simple_summarizer.py /path/to/your/file.txt
```

## Expected Output

```
============================================================
Text File Summarizer
============================================================
File: sample.txt
Original size: 2156 characters

Summary:
------------------------------------------------------------
[3-5 sentence summary of the file content]
------------------------------------------------------------
Summary size: 450 characters
============================================================
```

## How It Works

1. Reads the text file from the provided path
2. Sends the content to Claude with instructions to create a 3-5 sentence summary
3. Displays the summary with character count comparison
4. Limits output to 300 tokens maximum to ensure brevity

## Customization

Edit `simple_summarizer.py` to:

- **Change summary length**: Modify the prompt to request more or fewer sentences
- **Adjust max tokens**: Change `max_tokens` parameter (default: 300)
- **Use different model**: Change the `model` parameter

## Troubleshooting

**Error: "ANTHROPIC_API_KEY not set"**
- Export your API key: `export ANTHROPIC_API_KEY=your-key`

**Error: "Module not found: anthropic"**
- Install the library: `pip install anthropic`

**Summary is too long**
- Reduce the `max_tokens` parameter in the code
- Make the prompt more explicit about length requirements
