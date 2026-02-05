#!/usr/bin/env python3
"""
AI News Scraper Agent
Scrapes AI-related news from Techmeme.com and TechCrunch.com,
includes posts from X (Twitter) via xpoz MCP server, clusters by topic,
and outputs formatted listings to Output.html.

Usage:
    python ai_news_scraper.py                    # News + X posts (uses accounts.txt & x_posts.json)
    python ai_news_scraper.py --list-accounts    # Show accounts to fetch via xpoz MCP
    python ai_news_scraper.py -a myaccounts.txt  # Use custom accounts file

Files:
    accounts.txt  - List of X usernames to include (one per line)
    x_posts.json  - X posts fetched via xpoz MCP (auto-filtered to accounts.txt)
    Output.html   - Generated news summary clustered by topic

Workflow with xpoz MCP:
    1. Edit accounts.txt with X usernames you want to follow
    2. Use Claude with xpoz MCP to fetch posts:
       mcp__xpoz-mcp__getTwitterPostsByAuthor for each account
    3. Save results to x_posts.json
    4. Run: python ai_news_scraper.py

The scraper automatically:
    - Reads accounts.txt to know which X accounts to include
    - Filters x_posts.json to only include posts from those accounts
    - Warns about accounts in accounts.txt that have no posts in x_posts.json
    - Clusters all content (news + X posts) by topic
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import re
import argparse
import json
from pathlib import Path

# AI-related keywords for filtering
AI_KEYWORDS = [
    'ai', 'artificial intelligence', 'machine learning', 'ml',
    'deep learning', 'neural network', 'llm', 'gpt', 'chatgpt',
    'claude', 'gemini', 'openai', 'anthropic', 'deepmind',
    'transformer', 'generative ai', 'gen ai', 'copilot',
    'large language model', 'diffusion', 'stable diffusion',
    'midjourney', 'computer vision', 'nlp', 'robotics',
    'nvidia', 'tensor', 'hugging face', 'mistral', 'llama',
    'foundation model', 'ai model', 'ai agent', 'rag',
    'retrieval augmented', 'fine-tuning', 'prompt engineering'
]

# Display names for known X accounts
DISPLAY_NAMES = {
    'sama': 'Sam Altman',
    'openai': 'OpenAI',
    'anthropicai': 'Anthropic',
    'googledeepmind': 'Google DeepMind',
    'demaboris': 'Demis Hassabis',
    'ylecun': 'Yann LeCun',
    'karpathy': 'Andrej Karpathy',
    'aiatmeta': 'AI at Meta',
    'ilyasut': 'Ilya Sutskever',
    'huggingface': 'Hugging Face',
    'moltbook': 'Moltbook',
    'bcherny': 'Boris Cherny',
    'nanobanana': 'Nano Banana',
}

# Known entities for topic extraction (companies, products, people, concepts)
KNOWN_ENTITIES = {
    # Major AI Companies
    'openai': 'OpenAI', 'anthropic': 'Anthropic', 'google': 'Google',
    'deepmind': 'DeepMind', 'meta': 'Meta', 'microsoft': 'Microsoft',
    'nvidia': 'NVIDIA', 'apple': 'Apple', 'amazon': 'Amazon', 'aws': 'AWS',
    'hugging face': 'Hugging Face', 'huggingface': 'Hugging Face',
    'stability ai': 'Stability AI', 'cohere': 'Cohere', 'mistral': 'Mistral',
    'inflection': 'Inflection', 'character ai': 'Character AI',
    'elevenlabs': 'ElevenLabs', 'eleven labs': 'ElevenLabs',
    'runway': 'Runway', 'midjourney': 'Midjourney', 'adobe': 'Adobe',
    'salesforce': 'Salesforce', 'ibm': 'IBM', 'intel': 'Intel', 'amd': 'AMD',
    'tesla': 'Tesla', 'xai': 'xAI', 'perplexity': 'Perplexity',

    # Products & Models
    'gpt-4': 'GPT-4', 'gpt-5': 'GPT-5', 'gpt4': 'GPT-4', 'gpt5': 'GPT-5',
    'chatgpt': 'ChatGPT', 'claude': 'Claude', 'gemini': 'Gemini',
    'llama': 'Llama', 'mistral': 'Mistral', 'copilot': 'Copilot',
    'dall-e': 'DALL-E', 'dalle': 'DALL-E', 'sora': 'Sora',
    'stable diffusion': 'Stable Diffusion', 'flux': 'Flux',
    'whisper': 'Whisper', 'codex': 'Codex',
    'claude code': 'Claude Code', 'cursor': 'Cursor', 'replit': 'Replit',
    'github copilot': 'GitHub Copilot', 'xcode': 'Xcode',

    # People
    'sam altman': 'Sam Altman', 'dario amodei': 'Dario Amodei',
    'demis hassabis': 'Demis Hassabis', 'yann lecun': 'Yann LeCun',
    'andrej karpathy': 'Andrej Karpathy', 'karpathy': 'Andrej Karpathy',
    'ilya sutskever': 'Ilya Sutskever', 'elon musk': 'Elon Musk',
    'sundar pichai': 'Sundar Pichai', 'satya nadella': 'Satya Nadella',
    'jensen huang': 'Jensen Huang', 'mark zuckerberg': 'Mark Zuckerberg',

    # Topics & Concepts
    'funding': 'Funding & Investment', 'investment': 'Funding & Investment',
    'raises': 'Funding & Investment', 'valuation': 'Funding & Investment',
    'series a': 'Funding & Investment', 'series b': 'Funding & Investment',
    'series c': 'Funding & Investment', 'ipo': 'IPO',
    'regulation': 'AI Regulation', 'safety': 'AI Safety',
    'alignment': 'AI Alignment', 'misalignment': 'AI Alignment',
    'ethics': 'AI Ethics', 'bias': 'AI Ethics',
    'autonomous': 'Autonomous Systems', 'robotics': 'Robotics',
    'self-driving': 'Autonomous Vehicles', 'autonomous vehicle': 'Autonomous Vehicles',
    'healthcare': 'AI in Healthcare', 'medical': 'AI in Healthcare',
    'drug discovery': 'AI in Healthcare',
    'agents': 'AI Agents', 'agentic': 'AI Agents',
    'reasoning': 'AI Reasoning', 'chain of thought': 'AI Reasoning',
    'multimodal': 'Multimodal AI', 'vision': 'Computer Vision',
    'voice': 'Voice AI', 'speech': 'Voice AI', 'text-to-speech': 'Voice AI',
    'video': 'Video AI', 'text-to-video': 'Video AI',
    'training': 'Model Training', 'fine-tuning': 'Model Training',
    'inference': 'AI Inference', 'deployment': 'AI Deployment',
    'open source': 'Open Source AI', 'open-source': 'Open Source AI',
}

# Request headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def contains_ai_keyword(text):
    """Check if text contains any AI-related keywords."""
    if not text:
        return False
    text_lower = text.lower()
    for keyword in AI_KEYWORDS:
        # Use word boundary matching for short keywords to avoid false positives
        if len(keyword) <= 3:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                return True
        else:
            if keyword in text_lower:
                return True
    return False


def extract_entities(text):
    """Extract known entities from text for topic clustering."""
    if not text:
        return set()

    text_lower = text.lower()
    found_entities = set()

    for pattern, canonical_name in KNOWN_ENTITIES.items():
        # Use word boundary matching to avoid partial matches
        if len(pattern) <= 3:
            regex = r'\b' + re.escape(pattern) + r'\b'
            if re.search(regex, text_lower):
                found_entities.add(canonical_name)
        else:
            if pattern in text_lower:
                found_entities.add(canonical_name)

    # Also extract capitalized words that might be company/product names (proper nouns)
    # This catches entities not in our known list
    proper_nouns = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)
    for noun in proper_nouns:
        # Skip common words and short words
        if len(noun) > 3 and noun.lower() not in ['the', 'this', 'that', 'with', 'from', 'have', 'been', 'will', 'what', 'when', 'where', 'which', 'would', 'could', 'should', 'about', 'after', 'before', 'being', 'between', 'both', 'each', 'more', 'most', 'other', 'some', 'such', 'than', 'then', 'these', 'they', 'through', 'under', 'very', 'just', 'also', 'into', 'over', 'only', 'well', 'back', 'even', 'still', 'first', 'last', 'long', 'great', 'little', 'much', 'never', 'now', 'old', 'see', 'way', 'who', 'come', 'make', 'like', 'time', 'just', 'know', 'take', 'people', 'year', 'good', 'give', 'day', 'most', 'new', 'want', 'because', 'any', 'find', 'here', 'thing', 'think', 'say', 'she', 'two', 'how', 'our', 'work', 'world', 'life', 'hand', 'part', 'child', 'eye', 'woman', 'place', 'case', 'week', 'company', 'system', 'program', 'question', 'government', 'number', 'night', 'point', 'home', 'water', 'room', 'mother', 'area', 'money', 'story', 'fact', 'month', 'different', 'right', 'study', 'book', 'word', 'business', 'issue', 'side', 'kind', 'head', 'house', 'service', 'friend', 'father', 'power', 'hour', 'game', 'line', 'end', 'member', 'law', 'car', 'city', 'community', 'name', 'president', 'team', 'minute', 'idea', 'body', 'information', 'today', 'read', 'thread', 'finding', 'view', 'view']:
            found_entities.add(noun)

    return found_entities


def normalize_item(item, item_type):
    """Normalize an article or post into a common format for clustering."""
    if item_type == 'article':
        text = f"{item.get('headline', '')} {item.get('description', '')}"
        return {
            'type': 'article',
            'title': item.get('headline', ''),
            'text': text,
            'url': item.get('url', '#'),
            'source': item.get('source', ''),
            'entities': extract_entities(text),
            'original': item
        }
    elif item_type == 'x_post':
        text = item.get('text', '')
        return {
            'type': 'x_post',
            'title': text[:100] + '...' if len(text) > 100 else text,
            'text': text,
            'url': item.get('url', '#'),
            'source': f"@{item.get('username', '')}",
            'entities': extract_entities(text),
            'original': item
        }
    elif item_type == 'x_thread':
        # For threads, combine all post texts
        posts = item.get('posts', [])
        combined_text = ' '.join(p.get('text', '') for p in posts)
        first_text = posts[0].get('text', '') if posts else ''
        return {
            'type': 'x_thread',
            'title': first_text[:100] + '...' if len(first_text) > 100 else first_text,
            'text': combined_text,
            'url': posts[0].get('url', '#') if posts else '#',
            'source': f"@{item.get('username', '')}",
            'entities': extract_entities(combined_text),
            'original': item
        }
    return None


def cluster_by_topic(items, min_cluster_size=2):
    """Cluster items by shared entities/topics.

    Returns a list of clusters, where each cluster is:
    {
        'topic': 'Topic Name',
        'entities': set of shared entities,
        'items': list of items in this cluster
    }

    Items that don't cluster with others go into individual "clusters" of size 1.
    """
    if not items:
        return []

    # Build entity -> items mapping
    entity_to_items = defaultdict(list)
    for i, item in enumerate(items):
        for entity in item.get('entities', set()):
            entity_to_items[entity].append(i)

    # Find clusters: items that share significant entities
    used_items = set()
    clusters = []

    # Sort entities by how many items they appear in (most common first)
    sorted_entities = sorted(entity_to_items.items(), key=lambda x: len(x[1]), reverse=True)

    for entity, item_indices in sorted_entities:
        # Skip if we don't have enough items for a cluster
        available_indices = [i for i in item_indices if i not in used_items]
        if len(available_indices) < min_cluster_size:
            continue

        # Create a cluster for this entity
        cluster_items = [items[i] for i in available_indices]

        # Find additional shared entities among these items
        shared_entities = set.intersection(*[item.get('entities', set()) for item in cluster_items])
        if not shared_entities:
            shared_entities = {entity}

        # Determine the best topic name (prefer specific company/product names over generic topics)
        topic = entity
        for e in shared_entities:
            # Prefer non-generic names
            if e not in ['Funding & Investment', 'AI Safety', 'AI Agents', 'Model Training', 'AI Reasoning']:
                topic = e
                break

        clusters.append({
            'topic': topic,
            'entities': shared_entities,
            'items': cluster_items
        })

        # Mark items as used
        for i in available_indices:
            used_items.add(i)

    # Add remaining unclustered items as individual entries
    for i, item in enumerate(items):
        if i not in used_items:
            clusters.append({
                'topic': None,  # No specific topic, standalone item
                'entities': item.get('entities', set()),
                'items': [item]
            })

    # Sort clusters: multi-item clusters first (by size), then single items
    clusters.sort(key=lambda c: (-len(c['items']), c['topic'] or 'zzz'))

    return clusters


def read_x_accounts(file_path):
    """Read X account usernames from a text file (one per line)."""
    accounts = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Strip whitespace and remove @ if present
                account = line.strip().lstrip('@')
                if account and not account.startswith('#'):  # Skip empty lines and comments
                    accounts.append(account)
        print(f"Loaded {len(accounts)} X accounts from {file_path}")
    except FileNotFoundError:
        print(f"Error: X accounts file not found: {file_path}")
    except Exception as e:
        print(f"Error reading X accounts file: {e}")
    return accounts


def load_x_posts_from_json(file_path):
    """Load X posts from a JSON file (fetched via xpoz MCP).

    Expected JSON format:
    [
        {
            "username": "OpenAI",
            "display_name": "OpenAI",
            "text": "Tweet content...",
            "created_at": "2024-01-15T10:30:00Z",
            "url": "https://x.com/OpenAI/status/123456789",
            "metrics": {
                "like_count": 100,
                "retweet_count": 50,
                "reply_count": 25
            }
        },
        ...
    ]
    """
    posts = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            posts = data
        elif isinstance(data, dict) and 'posts' in data:
            posts = data['posts']
        else:
            print(f"Warning: Unexpected JSON structure in {file_path}")
            return []

        # Normalize field names from xpoz MCP format
        normalized_posts = []
        for post in posts:
            username = post.get('username') or post.get('authorUsername', '')
            # Look up display name from our mapping, falling back to provided name or username
            display_name = DISPLAY_NAMES.get(username.lower()) or post.get('display_name') or post.get('authorName') or username
            normalized = {
                'username': username,
                'display_name': display_name,
                'text': post.get('text', ''),
                'created_at': post.get('created_at') or post.get('createdAt') or post.get('createdAtDate', ''),
                'url': post.get('url') or f"https://x.com/{post.get('authorUsername', '')}/status/{post.get('id', '')}",
                'metrics': post.get('metrics', {
                    'like_count': post.get('likeCount', 0),
                    'retweet_count': post.get('retweetCount', 0),
                    'reply_count': post.get('replyCount', 0)
                })
            }
            normalized_posts.append(normalized)

        print(f"Loaded {len(normalized_posts)} X posts from {file_path}")
        return normalized_posts

    except FileNotFoundError:
        print(f"Error: X posts JSON file not found: {file_path}")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
    except Exception as e:
        print(f"Error reading X posts file: {e}")

    return posts


def fetch_techmeme():
    """Scrape headlines from Techmeme.com."""
    articles = []
    url = 'https://www.techmeme.com/'

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Techmeme uses div.clus for story clusters
        story_clusters = soup.find_all('div', class_='clus')

        for cluster in story_clusters[:30]:  # Limit to top 30 clusters
            # Main headline link
            headline_link = cluster.find('a', class_='ourh')
            if headline_link:
                headline = headline_link.get_text(strip=True)
                link = headline_link.get('href', '')

                # Try to get the source
                source_span = cluster.find('cite')
                source = source_span.get_text(strip=True) if source_span else 'Unknown'

                # Try to get description/summary
                description = ''
                desc_div = cluster.find('div', class_='st')
                if desc_div:
                    description = desc_div.get_text(strip=True)[:200]

                articles.append({
                    'headline': headline,
                    'source': source,
                    'url': link,
                    'description': description
                })

        print(f"Fetched {len(articles)} articles from Techmeme")

    except requests.RequestException as e:
        print(f"Error fetching Techmeme: {e}")

    return articles


def fetch_techcrunch():
    """Scrape AI category from TechCrunch.com."""
    articles = []
    url = 'https://techcrunch.com/category/artificial-intelligence/'

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all headline links (h2 and h3 tags contain the main article links)
        seen_urls = set()
        for headline_tag in soup.find_all(['h2', 'h3']):
            link_tag = headline_tag.find('a')
            if link_tag:
                headline = link_tag.get_text(strip=True)
                link = link_tag.get('href', '')

                # Skip empty headlines or duplicates
                if not headline or link in seen_urls:
                    continue
                seen_urls.add(link)

                # Try to find the parent container for more context
                parent = headline_tag.find_parent(['div', 'article'])
                description = ''
                author = ''

                if parent:
                    # Try to get description/excerpt
                    desc_tag = parent.find('p')
                    if desc_tag:
                        description = desc_tag.get_text(strip=True)[:200]

                    # Try to get author
                    author_tag = parent.find('a', rel='author')
                    if not author_tag:
                        # Try alternative author patterns
                        author_tag = parent.find('a', href=lambda x: x and '/author/' in x)
                    if author_tag:
                        author = author_tag.get_text(strip=True)

                articles.append({
                    'headline': headline,
                    'source': f'TechCrunch{" - " + author if author else ""}',
                    'url': link,
                    'description': description
                })

                if len(articles) >= 20:  # Limit to 20 articles
                    break

        print(f"Fetched {len(articles)} articles from TechCrunch AI category")

    except requests.RequestException as e:
        print(f"Error fetching TechCrunch: {e}")

    return articles


def filter_ai_content(articles):
    """Filter articles to only include AI-related content."""
    filtered = []
    for article in articles:
        # Check headline and description for AI keywords
        combined_text = f"{article.get('headline', '')} {article.get('description', '')}"
        if contains_ai_keyword(combined_text):
            filtered.append(article)
    return filtered


def format_article_html(article):
    """Format a single article as HTML."""
    headline = article.get('headline', 'No headline')
    url = article.get('url', '#')
    source = article.get('source', '')
    description = article.get('description', '').strip()

    html = f'''<div class="article">
    <a href="{url}" target="_blank" class="headline">{headline}</a>
    <span class="source">{source}</span>'''

    if description:
        html += f'\n    <p class="description">{description}</p>'

    html += '\n</div>'
    return html


def format_x_post_html(post, is_thread_part=False):
    """Format a single X post as HTML."""
    username = post.get('username', '')
    display_name = post.get('display_name', username)
    text = post.get('text', '')
    url = post.get('url', '#')
    created_at = post.get('created_at', '')
    metrics = post.get('metrics', {})

    # Format timestamp
    if created_at:
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            time_str = dt.strftime('%b %d, %H:%M')
        except:
            time_str = created_at
    else:
        time_str = ''

    # Format metrics
    likes = metrics.get('like_count', 0)
    retweets = metrics.get('retweet_count', 0)
    replies = metrics.get('reply_count', 0)

    # Convert URLs in text to links
    text_html = re.sub(r'(https?://\S+)', r'<a href="\1" target="_blank">\1</a>', text)

    if is_thread_part:
        # Simplified format for thread posts (no header, compact metrics)
        html = f'''<div class="thread-post">
    <p class="x-text">{text_html}</p>
    <div class="x-metrics-compact">
        <span>{likes} likes</span>
        <a href="{url}" target="_blank" class="x-link">View</a>
    </div>
</div>'''
    else:
        html = f'''<div class="x-post">
    <div class="x-header">
        <a href="https://x.com/{username}" target="_blank" class="x-user">
            <span class="x-display-name">{display_name}</span>
            <span class="x-username">@{username}</span>
        </a>
        <span class="x-time">{time_str}</span>
    </div>
    <p class="x-text">{text_html}</p>
    <div class="x-metrics">
        <span title="Replies">{replies} replies</span>
        <span title="Retweets">{retweets} retweets</span>
        <span title="Likes">{likes} likes</span>
        <a href="{url}" target="_blank" class="x-link">View on X</a>
    </div>
</div>'''
    return html


def detect_threads(posts, time_threshold_minutes=10):
    """Group posts into threads based on author and time proximity.

    Posts from the same author within time_threshold_minutes are grouped as a thread.
    Returns a list of items where each item is either:
    - A single post dict (standalone)
    - A dict with 'is_thread': True and 'posts': [list of posts] (thread)
    """
    if not posts:
        return []

    # Parse timestamps and sort by author then time
    posts_with_dt = []
    for post in posts:
        created_at = post.get('created_at', '')
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        except:
            dt = None
        posts_with_dt.append((post, dt))

    # Group by author
    by_author = defaultdict(list)
    for post, dt in posts_with_dt:
        username = post.get('username', '')
        by_author[username].append((post, dt))

    # Sort each author's posts by time
    for username in by_author:
        by_author[username].sort(key=lambda x: x[1] if x[1] else datetime.min.replace(tzinfo=timezone.utc))

    # Detect threads within each author's posts
    result_items = []

    for username, author_posts in by_author.items():
        if len(author_posts) == 1:
            # Single post, no thread possible
            result_items.append((author_posts[0][1], author_posts[0][0]))
            continue

        # Find threads: consecutive posts within time threshold
        current_thread = [author_posts[0]]

        for i in range(1, len(author_posts)):
            post, dt = author_posts[i]
            prev_post, prev_dt = current_thread[-1]

            # Check if this post is within threshold of previous
            if dt and prev_dt:
                time_diff = abs((dt - prev_dt).total_seconds() / 60)
                if time_diff <= time_threshold_minutes:
                    current_thread.append((post, dt))
                    continue

            # Not part of current thread - finalize current and start new
            if len(current_thread) >= 2:
                # It's a thread
                thread_posts = [p for p, _ in current_thread]
                first_dt = current_thread[0][1]
                result_items.append((first_dt, {'is_thread': True, 'posts': thread_posts, 'username': username}))
            else:
                # Single post
                result_items.append((current_thread[0][1], current_thread[0][0]))

            current_thread = [(post, dt)]

        # Don't forget the last thread/post
        if len(current_thread) >= 2:
            thread_posts = [p for p, _ in current_thread]
            first_dt = current_thread[0][1]
            result_items.append((first_dt, {'is_thread': True, 'posts': thread_posts, 'username': username}))
        else:
            result_items.append((current_thread[0][1], current_thread[0][0]))

    # Sort all items by time (most recent first)
    result_items.sort(key=lambda x: x[0] if x[0] else datetime.min.replace(tzinfo=timezone.utc), reverse=True)

    return [item for _, item in result_items]


def format_thread_html(thread):
    """Format a thread of posts as HTML."""
    posts = thread['posts']
    username = thread['username']

    # Get info from first post
    first_post = posts[0]
    display_name = first_post.get('display_name', username)
    created_at = first_post.get('created_at', '')

    # Format timestamp
    if created_at:
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            time_str = dt.strftime('%b %d, %H:%M')
        except:
            time_str = created_at
    else:
        time_str = ''

    # Aggregate metrics across thread
    total_likes = sum(p.get('metrics', {}).get('like_count', 0) for p in posts)
    total_retweets = sum(p.get('metrics', {}).get('retweet_count', 0) for p in posts)
    total_replies = sum(p.get('metrics', {}).get('reply_count', 0) for p in posts)

    # Build thread posts HTML
    thread_posts_html = '\n'.join(format_x_post_html(p, is_thread_part=True) for p in posts)

    html = f'''<div class="x-thread">
    <div class="x-header">
        <a href="https://x.com/{username}" target="_blank" class="x-user">
            <span class="x-display-name">{display_name}</span>
            <span class="x-username">@{username}</span>
        </a>
        <span class="thread-indicator">Thread ({len(posts)} posts)</span>
        <span class="x-time">{time_str}</span>
    </div>
    <div class="thread-content">
        {thread_posts_html}
    </div>
    <div class="x-metrics thread-metrics">
        <span title="Replies">{total_replies} replies</span>
        <span title="Retweets">{total_retweets} retweets</span>
        <span title="Likes">{total_likes} likes</span>
    </div>
</div>'''
    return html


def format_x_content_html(item):
    """Format either a single post or a thread."""
    if isinstance(item, dict) and item.get('is_thread'):
        return format_thread_html(item)
    else:
        return format_x_post_html(item)


def format_cluster_item_html(normalized_item):
    """Format a normalized item (article or X post/thread) for display in a cluster."""
    item_type = normalized_item['type']
    original = normalized_item['original']
    source = normalized_item['source']

    if item_type == 'article':
        return f'''<div class="cluster-item article-item">
    <span class="item-source">{source}</span>
    {format_article_html(original)}
</div>'''
    elif item_type == 'x_post':
        return f'''<div class="cluster-item x-item">
    {format_x_post_html(original)}
</div>'''
    elif item_type == 'x_thread':
        return f'''<div class="cluster-item x-item">
    {format_thread_html(original)}
</div>'''
    return ''


def format_cluster_html(cluster):
    """Format a topic cluster as HTML."""
    topic = cluster['topic']
    items = cluster['items']
    entities = cluster['entities']

    # Generate items HTML
    items_html = '\n'.join(format_cluster_item_html(item) for item in items)

    # Count by type
    article_count = sum(1 for item in items if item['type'] == 'article')
    x_count = sum(1 for item in items if item['type'] in ('x_post', 'x_thread'))

    if topic and len(items) > 1:
        # Multi-item cluster with a topic
        entity_tags = ' '.join(f'<span class="entity-tag">{e}</span>' for e in sorted(entities)[:5])
        return f'''<div class="topic-cluster">
    <div class="cluster-header">
        <h3 class="cluster-topic">{topic}</h3>
        <span class="cluster-count">{len(items)} items</span>
    </div>
    <div class="cluster-entities">{entity_tags}</div>
    <div class="cluster-items">
        {items_html}
    </div>
</div>'''
    else:
        # Single item, no cluster wrapper needed
        return items_html


def generate_html(techmeme_articles, techcrunch_articles, x_posts=None):
    """Generate an HTML page with all articles and X posts, clustered by topic."""
    today = datetime.now().strftime('%B %d, %Y')
    generated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    x_posts = x_posts or []
    total = len(techmeme_articles) + len(techcrunch_articles) + len(x_posts)

    # Normalize all items for clustering
    all_items = []

    # Add articles
    for article in techmeme_articles:
        normalized = normalize_item(article, 'article')
        if normalized:
            all_items.append(normalized)

    for article in techcrunch_articles:
        normalized = normalize_item(article, 'article')
        if normalized:
            all_items.append(normalized)

    # Detect X threads first, then normalize
    if x_posts:
        x_items = detect_threads(x_posts)
        for item in x_items:
            if isinstance(item, dict) and item.get('is_thread'):
                normalized = normalize_item(item, 'x_thread')
            else:
                normalized = normalize_item(item, 'x_post')
            if normalized:
                all_items.append(normalized)

    # Cluster all items by topic
    clusters = cluster_by_topic(all_items, min_cluster_size=2)

    # Count clusters vs standalone
    multi_clusters = [c for c in clusters if len(c['items']) > 1]
    standalone_items = [c for c in clusters if len(c['items']) == 1]

    # Generate clusters HTML
    if clusters:
        clusters_html = '\n'.join(format_cluster_html(c) for c in clusters)
        content_section = f'''
    <div class="content-summary">
        <p>{total} items total: {len(multi_clusters)} topic clusters, {len(standalone_items)} standalone items</p>
    </div>
    {clusters_html}'''
    else:
        content_section = '<p class="no-articles">No content found.</p>'

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI News Summary - {today}</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }}
        h1 {{
            color: #1a1a1a;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #0066cc;
            margin-top: 30px;
            padding: 10px 0;
            border-bottom: 1px solid #ddd;
        }}
        .subtitle {{
            color: #666;
            font-size: 1.1em;
            margin-top: -5px;
            margin-bottom: 20px;
        }}
        .article {{
            background: white;
            padding: 15px 20px;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .article:hover {{
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        .headline {{
            font-size: 1.1em;
            font-weight: 600;
            color: #0066cc;
            text-decoration: none;
            display: block;
            margin-bottom: 5px;
        }}
        .headline:hover {{
            color: #004499;
            text-decoration: underline;
        }}
        .source {{
            font-size: 0.85em;
            color: #666;
            font-style: italic;
        }}
        .description {{
            font-size: 0.95em;
            color: #555;
            margin: 10px 0 0 0;
            line-height: 1.5;
        }}
        .footer {{
            margin-top: 40px;
            padding: 20px;
            background: #333;
            color: white;
            border-radius: 8px;
            text-align: center;
        }}
        .stats {{
            font-size: 1.2em;
            margin-bottom: 10px;
        }}
        .timestamp {{
            font-size: 0.85em;
            color: #aaa;
        }}
        .no-articles {{
            color: #666;
            font-style: italic;
            padding: 20px;
        }}
        /* X Posts Styles */
        .x-post {{
            background: white;
            padding: 15px 20px;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 3px solid #1da1f2;
        }}
        .x-post:hover {{
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        .x-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .x-user {{
            text-decoration: none;
        }}
        .x-display-name {{
            font-weight: 600;
            color: #333;
        }}
        .x-username {{
            color: #666;
            font-size: 0.9em;
            margin-left: 5px;
        }}
        .x-time {{
            color: #999;
            font-size: 0.85em;
        }}
        .x-text {{
            margin: 10px 0;
            line-height: 1.5;
            color: #333;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .x-text a {{
            color: #1da1f2;
        }}
        .x-metrics {{
            display: flex;
            gap: 15px;
            font-size: 0.85em;
            color: #666;
            margin-top: 10px;
        }}
        .x-link {{
            color: #1da1f2;
            text-decoration: none;
            margin-left: auto;
        }}
        .x-link:hover {{
            text-decoration: underline;
        }}
        /* Thread Styles */
        .x-thread {{
            background: white;
            padding: 15px 20px;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 3px solid #9b59b6;
        }}
        .x-thread:hover {{
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        .thread-indicator {{
            background: #9b59b6;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            margin-left: 10px;
        }}
        .thread-content {{
            border-left: 2px solid #e0e0e0;
            margin-left: 10px;
            padding-left: 15px;
        }}
        .thread-post {{
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        .thread-post:last-child {{
            border-bottom: none;
        }}
        .thread-post .x-text {{
            margin: 5px 0;
        }}
        .x-metrics-compact {{
            display: flex;
            gap: 10px;
            font-size: 0.8em;
            color: #999;
        }}
        .thread-metrics {{
            margin-top: 15px;
            padding-top: 10px;
            border-top: 1px solid #eee;
        }}
        .x-summary {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 15px;
        }}
        /* Topic Cluster Styles */
        .content-summary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 25px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}
        .content-summary p {{
            margin: 0;
            font-size: 1.1em;
            font-weight: 500;
        }}
        .section-divider {{
            height: 3px;
            background: linear-gradient(90deg, #e0e0e0 0%, #bbb 50%, #e0e0e0 100%);
            margin: 40px 0;
            border-radius: 2px;
        }}
        .topic-cluster {{
            background: white;
            border: none;
            border-radius: 16px;
            padding: 25px;
            margin: 30px 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border-top: 4px solid #3498db;
        }}
        .topic-cluster:nth-child(odd) {{
            border-top-color: #9b59b6;
        }}
        .topic-cluster:nth-child(3n) {{
            border-top-color: #e74c3c;
        }}
        .topic-cluster:nth-child(4n) {{
            border-top-color: #2ecc71;
        }}
        .cluster-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }}
        .cluster-topic {{
            margin: 0;
            color: #1a1a1a;
            font-size: 1.4em;
            font-weight: 700;
            letter-spacing: -0.02em;
        }}
        .cluster-count {{
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
        }}
        .cluster-entities {{
            margin-bottom: 20px;
        }}
        .entity-tag {{
            display: inline-block;
            background: #f8f9fa;
            color: #495057;
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 0.82em;
            margin-right: 8px;
            margin-bottom: 8px;
            border: 1px solid #e9ecef;
            font-weight: 500;
        }}
        .cluster-items {{
            border-top: none;
            padding-top: 5px;
        }}
        .cluster-item {{
            margin-bottom: 15px;
        }}
        .cluster-item:last-child {{
            margin-bottom: 0;
        }}
        .cluster-item .article {{
            margin: 0;
            border-left: 3px solid #3498db;
        }}
        .cluster-item .x-post,
        .cluster-item .x-thread {{
            margin: 0;
        }}
        .item-source {{
            display: none;
        }}
        /* Standalone items section */
        .standalone-section {{
            margin-top: 50px;
            padding-top: 30px;
            border-top: 3px solid #e0e0e0;
        }}
        .standalone-header {{
            font-size: 1.3em;
            color: #666;
            margin-bottom: 20px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <h1>AI News Summary - {today}</h1>
    <p class="subtitle">Clustered by Topic</p>
    {content_section}

    <div class="footer">
        <div class="stats">Total: {total} items ({len(techmeme_articles)} Techmeme, {len(techcrunch_articles)} TechCrunch, {len(x_posts)} X posts)</div>
        <div class="timestamp">Generated: {generated}</div>
    </div>
</body>
</html>'''

    return html


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='AI News Scraper - Scrapes AI news from Techmeme, TechCrunch, and X posts via xpoz MCP'
    )
    parser.add_argument(
        '-x', '--x-posts',
        type=str,
        metavar='FILE',
        default='x_posts.json',
        help='Path to JSON file containing X posts (default: x_posts.json)'
    )
    parser.add_argument(
        '-a', '--accounts',
        type=str,
        metavar='FILE',
        default='accounts.txt',
        help='Path to file containing X account usernames (default: accounts.txt)'
    )
    parser.add_argument(
        '--list-accounts',
        action='store_true',
        help='Output the list of accounts for use with xpoz MCP (does not scrape)'
    )
    return parser.parse_args()


def filter_posts_by_recency(posts, max_age_hours=24):
    """Filter posts to only include those from the last N hours.

    Returns (recent_posts, dropped_count)
    """
    if not posts:
        return [], 0

    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    recent = []
    dropped = 0

    for post in posts:
        created_at = post.get('created_at') or post.get('createdAt') or post.get('createdAtDate', '')

        if created_at:
            try:
                # Handle various date formats
                if 'T' in str(created_at):
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    # Date only format (YYYY-MM-DD)
                    dt = datetime.strptime(created_at[:10], '%Y-%m-%d').replace(tzinfo=timezone.utc)

                if dt >= cutoff_time:
                    recent.append(post)
                else:
                    dropped += 1
            except (ValueError, TypeError):
                # If we can't parse the date, include the post
                recent.append(post)
        else:
            # No date, include the post
            recent.append(post)

    return recent, dropped


def filter_posts_by_accounts(posts, accounts):
    """Filter posts to only include those from specified accounts.

    Returns (filtered_posts, found_accounts, missing_accounts)
    """
    if not accounts:
        return posts, set(), set()

    # Normalize account names (lowercase for comparison)
    accounts_lower = {a.lower() for a in accounts}

    filtered = []
    found_accounts = set()

    for post in posts:
        username = post.get('username', '') or post.get('authorUsername', '')
        if username.lower() in accounts_lower:
            filtered.append(post)
            found_accounts.add(username.lower())

    missing_accounts = accounts_lower - found_accounts

    return filtered, found_accounts, missing_accounts


def main():
    """Main function to orchestrate the news scraping workflow."""
    args = parse_arguments()

    # Load accounts from accounts file
    accounts_file = Path(args.accounts)
    if accounts_file.exists():
        accounts = read_x_accounts(args.accounts)
    else:
        accounts = []
        print(f"Note: Accounts file '{args.accounts}' not found. X posts will not be filtered.")

    # Handle --list-accounts mode (for xpoz MCP workflow)
    if args.list_accounts:
        if accounts:
            print("\nAccounts to fetch via xpoz MCP:")
            print("-" * 40)
            for account in accounts:
                print(f"  @{account}")
            print("-" * 40)
            print("\nUse Claude with xpoz MCP to fetch posts from these accounts:")
            print("  1. Call mcp__xpoz-mcp__getTwitterPostsByAuthor for each account")
            print("  2. Save results to x_posts.json")
            print("  3. Run: python ai_news_scraper.py")
        else:
            print(f"No accounts found. Create '{args.accounts}' with one username per line.")
        return

    print("AI News Scraper - Starting...")
    print("-" * 40)

    if accounts:
        print(f"\nUsing {len(accounts)} accounts from {args.accounts}")

    # Fetch from both sources
    print("\nFetching from Techmeme...")
    techmeme_raw = fetch_techmeme()

    print("\nFetching from TechCrunch...")
    techcrunch_raw = fetch_techcrunch()

    # Filter Techmeme for AI content (TechCrunch AI category is already filtered)
    print("\nFiltering for AI content...")
    techmeme_filtered = filter_ai_content(techmeme_raw)
    print(f"Found {len(techmeme_filtered)} AI-related articles from Techmeme")

    # TechCrunch AI category articles are already AI-related
    techcrunch_filtered = techcrunch_raw

    # Load X posts from JSON file
    x_posts_file = Path(args.x_posts)
    x_posts = []
    if x_posts_file.exists():
        x_posts = load_x_posts_from_json(args.x_posts)
        initial_count = len(x_posts)

        # Filter posts to only include those from the last 24 hours
        x_posts, dropped_old = filter_posts_by_recency(x_posts, max_age_hours=24)
        if dropped_old > 0:
            print(f"Dropped {dropped_old} posts older than 24 hours")

        # Filter posts to only include accounts from accounts.txt
        if accounts:
            x_posts, found_accounts, missing_accounts = filter_posts_by_accounts(x_posts, accounts)
            print(f"Using {len(x_posts)} recent posts from accounts in {args.accounts}")

            if missing_accounts:
                print(f"\n⚠️  Missing posts from {len(missing_accounts)} accounts:")
                for account in sorted(missing_accounts):
                    print(f"   - @{account}")
                print(f"   Run xpoz MCP to fetch posts from these accounts.")
    else:
        print(f"\nNote: X posts file '{args.x_posts}' not found. Run with --list-accounts to see which accounts to fetch.")

    # Generate HTML output
    print("\nGenerating HTML page...")
    html_content = generate_html(techmeme_filtered, techcrunch_filtered, x_posts)

    # Write to Output.html
    output_path = Path(__file__).parent / 'Output.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    total = len(techmeme_filtered) + len(techcrunch_filtered) + len(x_posts)
    print(f"\nHTML page written to: {output_path}")
    print("-" * 40)
    print(f"Total items: {total}")
    print(f"  - Techmeme: {len(techmeme_filtered)} articles")
    print(f"  - TechCrunch: {len(techcrunch_filtered)} articles")
    if x_posts:
        print(f"  - X posts: {len(x_posts)} posts")
    print("\nDone! Open Output.html in your browser to view the results.")

    return html_content


if __name__ == '__main__':
    main()
