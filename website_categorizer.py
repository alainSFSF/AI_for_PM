#!/usr/bin/env python3
"""
Website Description Categorizer
Analyzes website descriptions and categorizes them using Claude AI
"""

import anthropic
import os
import sys


# Define website categories
CATEGORIES = {
    "Lesson Booking": "Websites that enable users to book a lesson or appointment, such as a piano lesson, physical therapy session, gym training session",
    "Event Planner": "Websites that enable users to plan an event, such as a wedding, a party, bar mitzvah",
    "Conference": "Websites that enable users to attend a conference, such as a tech conference, a business conference, a music conference",
    "Art Gallery": "A website that showcases pieces of art like sculptures, paintings and more",
    "Blog": "A website that enables an author to publish blogs and readers to subscribe and get notified of new content",
    "E-commerce": "A website that sells products or services online with shopping cart functionality",
    "Portfolio": "A website that showcases a professional's work, projects, or achievements",
    "Restaurant": "A website for a restaurant with menu, reservations, and ordering capabilities",
    "Social Network": "A platform for users to connect, share content, and interact with each other",
    "Educational Platform": "A website offering courses, tutorials, or learning materials",
    "News/Magazine": "A website that publishes news articles, journalism, or magazine content",
    "Corporate Website": "An elaborate website with many pages for Product, Services, Team, Pricing, Use Cases, Customer Testimonials, and more",
    "Small Business Website": "A business website showcasing company information, services, and contact details",
    "Real Estate": "A website for listing, searching, and viewing properties for sale or rent",
    "Healthcare": "A website for medical services, appointment booking, or health information",
    "Other": "Does not fit into the predefined categories"
}


def categorize_website(description: str, api_key: str = None) -> dict:
    """
    Categorize a website based on its description using Claude AI.

    Args:
        description: Text description of the website
        api_key: Anthropic API key (optional, can use env variable)

    Returns:
        Dictionary with category, confidence, and reasoning
    """
    # Get API key from parameter or environment
    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set. Please set it in your environment or pass it as a parameter.")

    # Initialize Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    # Create the categorization prompt
    categories_list = "\n".join([f"{i+1}. {cat}: {desc}" for i, (cat, desc) in enumerate(CATEGORIES.items())])

    prompt = f"""You are a website categorization expert. Analyze the following website description and categorize it into ONE of the predefined categories.

Website Description:
{description}

Available Categories:
{categories_list}

Instructions:
1. Read the website description carefully
2. Choose the MOST appropriate category from the list above
3. If none fit well, choose "Other"
4. Provide a brief explanation for your choice

Respond in the following format:
Category: [category name]
Confidence: [High/Medium/Low]
Reasoning: [brief explanation]"""

    # Call Claude API
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Parse the response
    response_text = message.content[0].text

    # Extract category, confidence, and reasoning
    result = {
        "category": "Other",
        "confidence": "Low",
        "reasoning": "",
        "raw_response": response_text
    }

    for line in response_text.split('\n'):
        if line.startswith('Category:'):
            result["category"] = line.replace('Category:', '').strip()
        elif line.startswith('Confidence:'):
            result["confidence"] = line.replace('Confidence:', '').strip()
        elif line.startswith('Reasoning:'):
            result["reasoning"] = line.replace('Reasoning:', '').strip()

    return result


def categorize_from_file(file_path: str) -> dict:
    """
    Read a text file and categorize the website description within it.

    Args:
        file_path: Path to the text file containing the website description

    Returns:
        Dictionary with category, confidence, and reasoning
    """
    try:
        with open(file_path, 'r') as f:
            description = f.read().strip()

        if not description:
            raise ValueError("File is empty")

        return categorize_website(description)

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def main():
    """Main entry point for the categorizer"""
    print("\n" + "=" * 70)
    print("Website Description Categorizer")
    print("=" * 70 + "\n")

    if len(sys.argv) < 2:
        print("Usage: python website_categorizer.py <file_path>")
        print("\nExample:")
        print("  python website_categorizer.py website_description.txt")
        print("\nOr run in interactive mode:")
        print("  python website_categorizer.py")
        print("\n" + "=" * 70 + "\n")

        # Interactive mode
        print("Interactive Mode - Enter website description")
        print("-" * 70)
        print("(Type your description and press Ctrl+D or Ctrl+Z when done)\n")

        try:
            description = sys.stdin.read().strip()
            if not description:
                print("No description provided. Exiting.")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\nExiting.")
            sys.exit(0)

        result = categorize_website(description)
    else:
        # File mode
        file_path = sys.argv[1]
        print(f"Analyzing file: {file_path}\n")
        result = categorize_from_file(file_path)

    # Display results
    print("=" * 70)
    print("CATEGORIZATION RESULTS")
    print("=" * 70)
    print(f"\n📁 Category:    {result['category']}")
    print(f"📊 Confidence:  {result['confidence']}")
    print(f"💭 Reasoning:   {result['reasoning']}")
    print("\n" + "=" * 70)
    print("\nFull Response:")
    print("-" * 70)
    print(result['raw_response'])
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
