# Website Description Categorizer

An AI-powered tool that analyzes website descriptions and automatically categorizes them into predefined categories using Claude AI.

## Features

- **AI-Powered Analysis**: Uses Claude Sonnet 4 for intelligent categorization
- **Multiple Categories**: Supports 14 predefined website categories
- **Confidence Scoring**: Provides confidence level (High/Medium/Low) for each categorization
- **Reasoning**: Explains why a particular category was chosen
- **Flexible Input**: Analyze from file or interactive input
- **Easy to Extend**: Simple to add new categories

## Supported Categories

1. **Lesson Booking** - Book lessons (piano, physical therapy, gym training, etc.)
2. **Event Planner** - Plan events (weddings, parties, bar mitzvahs, etc.)
3. **Art Gallery** - Showcase art (sculptures, paintings, etc.)
4. **Blog** - Publish content with subscriptions and notifications
5. **E-commerce** - Online shopping and product sales
6. **Portfolio** - Professional work showcase
7. **Restaurant** - Menus, reservations, and ordering
8. **Social Network** - User connections and content sharing
9. **Educational Platform** - Courses and learning materials
10. **News/Magazine** - News articles and journalism
11. **Corporate** - Business information and services
12. **Real Estate** - Property listings and searches
13. **Healthcare** - Medical services and appointments
14. **Other** - Anything that doesn't fit above

## Prerequisites

- Python 3.7+
- Anthropic API key

## Setup

1. **Install the Anthropic library**:
   ```bash
   pip install anthropic
   ```

2. **Set your API key**:
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

### Option 1: Analyze from a Text File

Create a text file with your website description:

```bash
python website_categorizer.py examples/piano_school.txt
```

### Option 2: Interactive Mode

Run without arguments and paste your description:

```bash
python website_categorizer.py
```

Then type or paste the website description and press `Ctrl+D` (Mac/Linux) or `Ctrl+Z` (Windows).

### Option 3: Use as a Python Module

```python
from website_categorizer import categorize_website

description = """
A platform for booking yoga classes and meditation sessions.
Users can view instructor schedules, book individual or group sessions,
and make payments online.
"""

result = categorize_website(description)

print(f"Category: {result['category']}")
print(f"Confidence: {result['confidence']}")
print(f"Reasoning: {result['reasoning']}")
```

## Example Output

```
======================================================================
CATEGORIZATION RESULTS
======================================================================

📁 Category:    Lesson Booking
📊 Confidence:  High
💭 Reasoning:   The website describes a platform for booking piano lessons with instructors, scheduling sessions, and managing calendars - core features of a lesson booking system.

======================================================================
```

## Example Files

The `examples/` directory contains sample website descriptions:

- `piano_school.txt` - Lesson Booking example
- `wedding_planner.txt` - Event Planner example
- `modern_art_gallery.txt` - Art Gallery example
- `tech_blog.txt` - Blog example

Try them out:
```bash
python website_categorizer.py examples/piano_school.txt
python website_categorizer.py examples/wedding_planner.txt
python website_categorizer.py examples/modern_art_gallery.txt
python website_categorizer.py examples/tech_blog.txt
```

## Adding Custom Categories

To add new categories, edit the `CATEGORIES` dictionary in `website_categorizer.py`:

```python
CATEGORIES = {
    "Your Category Name": "Description of this category",
    # ... existing categories
}
```

## Return Value Structure

The `categorize_website()` function returns a dictionary:

```python
{
    "category": "Lesson Booking",           # The chosen category
    "confidence": "High",                   # High/Medium/Low
    "reasoning": "Brief explanation...",    # Why this category was chosen
    "raw_response": "Full AI response..."   # Complete response from Claude
}
```

## Use Cases

- **Web Development Agencies**: Quickly categorize client website requests
- **Market Research**: Analyze and categorize competitor websites
- **Content Management**: Auto-tag website descriptions in databases
- **Portfolio Organization**: Categorize projects automatically
- **SEO Analysis**: Understand website types at scale

## Troubleshooting

**Error: "ANTHROPIC_API_KEY not set"**
- Make sure you've set the environment variable: `export ANTHROPIC_API_KEY=your_key`

**Error: "File not found"**
- Check the file path is correct
- Use absolute paths if relative paths aren't working

**Incorrect categorization**
- Provide more detailed descriptions
- Check if the category exists in the predefined list
- Consider if "Other" is the most appropriate category

## Advanced Usage

### Batch Processing Multiple Files

```python
from website_categorizer import categorize_from_file
import glob

for file_path in glob.glob("descriptions/*.txt"):
    result = categorize_from_file(file_path)
    print(f"{file_path}: {result['category']} ({result['confidence']})")
```

### Custom API Key

```python
from website_categorizer import categorize_website

result = categorize_website(
    description="Your website description here",
    api_key="your_custom_api_key"
)
```

## Notes

- The categorizer uses Claude Sonnet 4, which provides excellent accuracy
- Processing typically takes 1-3 seconds per description
- Costs approximately $0.001-0.003 per categorization (check current Anthropic pricing)
- Internet connection required for API calls

## License

MIT
