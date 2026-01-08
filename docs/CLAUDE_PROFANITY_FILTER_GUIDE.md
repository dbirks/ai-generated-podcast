# Claude API Profanity Filter Implementation Guide

## Overview

This guide provides comprehensive information about using Claude API for profanity filtering and text cleaning, specifically for blog post processing before TTS (Text-to-Speech) conversion.

---

## Table of Contents

1. [Claude SDKs Overview](#claude-sdks-overview)
2. [Can Claude Be Used for Profanity Filtering?](#can-claude-be-used-for-profanity-filtering)
3. [Installation & Setup](#installation--setup)
4. [Implementation Approaches](#implementation-approaches)
5. [Code Examples](#code-examples)
6. [Best Practices](#best-practices)
7. [Pricing Considerations](#pricing-considerations)
8. [Performance Optimization](#performance-optimization)

---

## Claude SDKs Overview

### What's the Difference Between Claude Code SDK and Claude Agent SDK?

**They're actually the same thing now.** The Claude Code SDK has been renamed to the **Claude Agent SDK** to better reflect its broader capabilities beyond just coding tasks.

**Key Relationship:**
- **Claude Code** = Ready-to-use CLI tool for software development (what you're using right now)
- **Claude Agent SDK** = Framework for building custom AI agents for any domain
- **Anthropic Python SDK** = Core API library for interacting with Claude models

**Which SDK to Use for Profanity Filtering?**

For profanity filtering and text cleaning, you should use the **Anthropic Python SDK** (`anthropic` package), which provides direct access to the Claude API.

- ✅ Use: `anthropic` Python SDK for text processing
- ❌ Don't use: Claude Code SDK (it's a CLI tool, not for programmatic text processing)
- ❌ Don't use: Claude Agent SDK (overkill for simple text cleaning)

---

## Can Claude Be Used for Profanity Filtering?

### Short Answer: **YES**

Claude can be effectively used for profanity detection and text cleaning through:

1. **Content Moderation API Pattern** - Using structured prompts to detect inappropriate content
2. **Text Rewriting** - Intelligently replacing profanity while preserving meaning
3. **Batch Processing** - Efficient processing of multiple texts

### Advantages Over Traditional Libraries

| Feature | Claude API | Traditional Libraries (e.g., better-profanity) |
|---------|------------|-----------------------------------------------|
| **Context Understanding** | ✅ Understands context, intent, tone | ❌ Simple word matching |
| **False Positives** | ✅ Low (context-aware) | ❌ High (e.g., "Scunthorpe problem") |
| **Natural Rewrites** | ✅ Preserves meaning & style | ❌ Only censors with asterisks |
| **Multilingual** | ✅ Supports many languages | ⚠️ Limited language support |
| **Custom Categories** | ✅ Easily customizable | ❌ Fixed word lists |
| **Cost** | ⚠️ Per-token pricing | ✅ Free/one-time cost |
| **Speed** | ⚠️ API latency (~1-2s) | ✅ Instant (local) |

### When to Use Claude vs. Traditional Libraries

**Use Claude when:**
- You need context-aware filtering (e.g., "That movie killed it!" should pass)
- You want natural-sounding rewrites, not just asterisks
- You're processing blog posts or long-form content
- You need multilingual support
- You want custom moderation categories

**Use Traditional Libraries when:**
- You need instant, real-time filtering
- Budget is extremely tight
- You're processing millions of short texts
- Simple word-based filtering is sufficient

---

## Installation & Setup

### 1. Install the Anthropic Python SDK

```bash
pip install anthropic python-dotenv
```

### 2. Get an API Key

1. Visit https://console.anthropic.com/
2. Create an account or log in
3. Go to API Keys section
4. Generate a new API key

### 3. Set Up Environment Variables

Create a `.env` file in your project root:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

**Security Best Practice:** Never commit your API key to version control!

Add to your `.gitignore`:
```
.env
*.key
*_key.txt
```

### 4. Basic Connection Test

```python
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Test the connection
response = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.content[0].text)
```

---

## Implementation Approaches

### Approach 1: Detection Only

Best for: Flagging content for human review

```python
def detect_profanity(text: str) -> bool:
    # Returns True/False if profanity is detected
    # See code examples for full implementation
    pass
```

**Use Case:** Pre-screening user-generated content

### Approach 2: Censoring with Asterisks

Best for: Quick censoring while maintaining original structure

```python
def censor_profanity(text: str) -> str:
    # Returns: "What the f*** is this?"
    # See code examples for full implementation
    pass
```

**Use Case:** Chat filters, comment sections

### Approach 3: Intelligent Rewriting (RECOMMENDED for Blog Posts)

Best for: Natural-sounding text suitable for TTS

```python
def clean_text_preserve_meaning(text: str) -> str:
    # Returns: "What on earth is this?"
    # See code examples for full implementation
    pass
```

**Use Case:** Blog post cleaning, article preparation, TTS preprocessing

### Approach 4: Batch Processing

Best for: Processing multiple blog posts efficiently

```python
def batch_clean_texts(texts: list[str]) -> list[str]:
    # Process multiple texts in one API call
    # See code examples for full implementation
    pass
```

**Use Case:** Bulk processing of blog archives

---

## Code Examples

See `claude_profanity_filter_examples.py` for complete, runnable examples including:

1. ✅ Basic profanity detection
2. ✅ Censoring with asterisks
3. ✅ Intelligent text cleaning (preserves meaning)
4. ✅ Batch processing for efficiency
5. ✅ Advanced content moderation
6. ✅ Async processing for large volumes
7. ✅ Smart blog post cleaning for TTS

---

## Best Practices

### 1. Model Selection

**For Profanity Filtering:**
- **Claude 3 Haiku** - Fast, cost-effective for simple detection/censoring
- **Claude 3.5 Sonnet** - Better quality for intelligent rewrites
- **Claude Opus 4.5** - Overkill for this use case (save your money)

**Recommendation:** Use **Haiku** for detection, **Sonnet 3.5** for blog post rewrites.

### 2. Prompt Engineering Best Practices

#### ✅ DO:
- Use temperature=0 for consistent results
- Request JSON output for structured responses
- Provide clear guidelines and examples
- Use XML tags to separate content: `<text>...</text>`
- Specify the exact behavior you want

#### ❌ DON'T:
- Use high temperature (adds randomness)
- Ask vague questions like "Is this bad?"
- Mix instructions with content
- Forget to handle edge cases

### 3. Error Handling

Always implement proper error handling:

```python
import anthropic

try:
    result = client.messages.create(...)
except anthropic.RateLimitError:
    # Implement exponential backoff
    time.sleep(60)
    retry()
except anthropic.APIConnectionError as e:
    # Handle network issues
    log_error(e)
except anthropic.APIStatusError as e:
    # Handle API errors (500s, etc.)
    log_error(f"API Error {e.status_code}")
```

### 4. Caching for Repeated Prompts

If you're using the same system prompt repeatedly, use prompt caching:

```python
response = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=1000,
    system=[
        {
            "type": "text",
            "text": "You are a content moderation expert...",
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[{"role": "user", "content": text}]
)
```

**Savings:** Cache reads cost only 10% of base input token price!

### 5. Content Safety

**Important:** Claude has built-in safety features that may refuse to process extremely explicit content, even for moderation purposes. This aligns with Anthropic's Acceptable Use Policy.

**Solutions:**
- Frame your request as "content moderation" or "content cleaning"
- Don't ask Claude to generate profanity
- Focus on detection and replacement, not analysis

### 6. Testing & Validation

Create a test suite with edge cases:

```python
test_cases = [
    # Clean text
    ("This is perfectly fine.", False),
    # Obvious profanity
    ("This is f***ing terrible.", True),
    # Context matters - should PASS
    ("The assassination attempt killed his campaign.", False),
    # Masked profanity
    ("This is bull$hit", True),
    # Non-English
    ("Merde! C'est terrible!", True),  # French profanity
]

for text, should_flag in test_cases:
    result = detect_profanity(text)
    assert result['has_profanity'] == should_flag
```

### 7. Rate Limiting

Anthropic API has rate limits:
- **Tier 1** (Free): 50 requests/minute
- **Tier 2+** (Paid): Higher limits based on usage

**Best Practices:**
- Implement exponential backoff
- Use batch processing when possible
- Cache results for repeated texts

---

## Pricing Considerations

### Current Pricing (January 2026)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Best For |
|-------|----------------------|------------------------|----------|
| **Claude 3 Haiku** | $0.25 | $1.25 | Detection, censoring |
| **Claude 3.5 Sonnet** | $3.00 | $15.00 | Intelligent rewrites |
| **Claude Opus 4.5** | $5.00 | $25.00 | Not needed for this |

### Cost Estimation for Blog Post Cleaning

**Assumptions:**
- Average blog post: 1,000 words ≈ 1,333 tokens
- Cleaning response: ~500 tokens
- Using Claude 3.5 Sonnet for quality

**Cost per blog post:**
- Input: 1,333 tokens × $3.00 / 1M = $0.004
- Output: 500 tokens × $15.00 / 1M = $0.0075
- **Total: ~$0.012 per blog post** (about 1.2 cents)

**Monthly Cost Examples:**

| Volume | Model | Monthly Cost |
|--------|-------|--------------|
| 10 posts/month | Sonnet 3.5 | $0.12 |
| 100 posts/month | Sonnet 3.5 | $1.20 |
| 1,000 posts/month | Sonnet 3.5 | $12.00 |
| 1,000 posts/month | Haiku | $2.00 |

### Cost Optimization Tips

#### 1. Use Batch Processing

Process multiple posts in one API call:

```python
# Instead of 10 API calls at $0.012 each = $0.12
# Use 1 batch call = ~$0.015 (saves ~88%)
batch_clean_texts([post1, post2, ..., post10])
```

**Savings:** Up to 50% reduction in costs

#### 2. Use Prompt Caching

For repeated system prompts:

```python
# First call: Full cost
# Subsequent calls: 90% off cached portion
```

**Savings:** Up to 90% on input tokens for repeated prompts

#### 3. Use Batch API (50% Discount)

For non-urgent processing:

```python
# Regular API: $3.00 input / $15.00 output
# Batch API: $1.50 input / $7.50 output (50% off)
```

**Savings:** 50% discount for asynchronous processing

#### 4. Right-Size Your Model

| If you need... | Use this model | Not this |
|----------------|----------------|----------|
| Simple detection | Haiku ($0.25) | Sonnet ($3.00) |
| Natural rewrites | Sonnet 3.5 | Opus 4.5 |
| Asterisk censoring | Haiku | Anything else |

**Savings:** 12x cost reduction (Haiku vs Sonnet)

#### 5. Filter Before Processing

Pre-filter with a simple library first:

```python
from better_profanity import profanity

# Quick local check (free)
if not profanity.contains_profanity(text):
    return text  # Skip API call

# Only call Claude for flagged texts
return clean_with_claude(text)
```

**Savings:** 50-90% reduction if most content is clean

### ROI Comparison

**Traditional Approach:**
- Hire human editor: $50-100/hour
- Time per blog: ~5-10 minutes
- Cost per blog: $4-17

**Claude API Approach:**
- Cost per blog: $0.012
- Time: ~2-3 seconds
- **Savings: 99%+ vs. human editing**

---

## Performance Optimization

### 1. Async Processing for Multiple Texts

```python
import asyncio
from anthropic import AsyncAnthropic

async def process_all_posts(posts: list[str]) -> list[str]:
    tasks = [async_clean_text(post) for post in posts]
    results = await asyncio.gather(*tasks)
    return results

# Process 100 posts concurrently
cleaned = asyncio.run(process_all_posts(blog_posts))
```

**Speed:** Process 100 posts in ~3-5 seconds (vs. 300+ seconds serially)

### 2. Implement Local Caching

```python
import hashlib
import json
from pathlib import Path

CACHE_DIR = Path(".cache/profanity_filters")
CACHE_DIR.mkdir(exist_ok=True)

def get_cached_or_clean(text: str) -> str:
    # Create hash of text
    text_hash = hashlib.md5(text.encode()).hexdigest()
    cache_file = CACHE_DIR / f"{text_hash}.json"

    # Check cache
    if cache_file.exists():
        return json.loads(cache_file.read_text())["cleaned_text"]

    # Clean with Claude
    result = clean_text_preserve_meaning(text)

    # Save to cache
    cache_file.write_text(json.dumps(result))

    return result["cleaned_text"]
```

**Speed:** Instant retrieval for previously processed texts

### 3. Progressive Enhancement

Start with fast, cheap filtering, escalate if needed:

```python
def smart_clean(text: str) -> str:
    # Level 1: Free local library (instant)
    if not profanity.contains_profanity(text):
        return text

    # Level 2: Try simple censoring with Haiku (fast, cheap)
    result = censor_with_haiku(text)
    if result['acceptable']:
        return result['text']

    # Level 3: Intelligent rewrite with Sonnet (slower, better)
    return clean_with_sonnet(text)
```

### 4. Streaming for Long Texts

For very long blog posts, use streaming:

```python
stream = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4000,
    stream=True,
    messages=[{"role": "user", "content": prompt}]
)

# Process response as it arrives
for event in stream:
    if event.type == "content_block_delta":
        print(event.delta.text, end="", flush=True)
```

---

## Integration Example: Blog Post Pipeline

Here's a complete pipeline for cleaning blog posts before TTS:

```python
import os
from pathlib import Path
from anthropic import Anthropic
import json

class BlogPostCleaner:
    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.cache_dir = Path(".cache/cleaned_posts")
        self.cache_dir.mkdir(exist_ok=True)

    def clean_post(self, post_content: str, post_id: str) -> dict:
        """Clean a blog post for TTS conversion."""

        # Check cache
        cache_file = self.cache_dir / f"{post_id}.json"
        if cache_file.exists():
            return json.loads(cache_file.read_text())

        # Clean with Claude
        prompt = f"""Clean this blog post for text-to-speech conversion.
        Remove profanity while preserving the author's voice and meaning.

        <post>{post_content}</post>

        Respond with JSON:
        {{
            "cleaned_text": "<TTS-ready version>",
            "changes_made": <boolean>,
            "summary": "<what was changed>"
        }}"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        result = json.loads(response.content[0].text)

        # Cache result
        cache_file.write_text(json.dumps(result, indent=2))

        return result

    def process_blog_archive(self, posts: list[dict]) -> list[dict]:
        """Process multiple blog posts efficiently."""
        cleaned_posts = []

        for post in posts:
            result = self.clean_post(
                post_content=post['content'],
                post_id=post['id']
            )

            cleaned_posts.append({
                'id': post['id'],
                'title': post['title'],
                'original_content': post['content'],
                'cleaned_content': result['cleaned_text'],
                'changes_made': result['changes_made']
            })

        return cleaned_posts

# Usage
cleaner = BlogPostCleaner()

posts = [
    {'id': '1', 'title': 'My Post', 'content': '...'},
    {'id': '2', 'title': 'Another Post', 'content': '...'},
]

cleaned = cleaner.process_blog_archive(posts)

# Generate TTS from cleaned content
for post in cleaned:
    if post['changes_made']:
        print(f"Cleaned: {post['title']}")
    # generate_tts(post['cleaned_content'])
```

---

## Troubleshooting

### Issue: "API Key Not Found"

**Solution:**
```python
# Check if .env is loaded
from dotenv import load_dotenv
load_dotenv()

# Verify key is set
import os
print(os.environ.get("ANTHROPIC_API_KEY"))  # Should not be None
```

### Issue: "Rate Limit Exceeded"

**Solution:**
```python
import time
from anthropic import RateLimitError

def clean_with_retry(text: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return clean_text(text)
        except RateLimitError:
            wait_time = 2 ** attempt  # Exponential backoff
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

### Issue: Claude Refuses to Process Content

**Solution:**
- Frame as "content moderation" not "content generation"
- Ensure you're cleaning, not asking Claude to create profanity
- Review Anthropic's Acceptable Use Policy

### Issue: Results Not Consistent

**Solution:**
```python
# Use temperature=0 for deterministic results
response = client.messages.create(
    model="claude-3-haiku-20240307",
    temperature=0,  # Add this
    ...
)
```

---

## Additional Resources

- **Official Docs:** https://docs.anthropic.com/
- **Content Moderation Guide:** https://platform.claude.com/docs/en/about-claude/use-case-guides/content-moderation
- **Python SDK:** https://github.com/anthropics/anthropic-sdk-python
- **Pricing:** https://platform.claude.com/docs/en/about-claude/pricing
- **API Reference:** https://docs.anthropic.com/en/api

---

## Summary

### Quick Decision Matrix

| Your Need | Recommended Solution | Cost | Speed |
|-----------|---------------------|------|-------|
| **Detect only** | Claude Haiku | $0.001/post | 1-2s |
| **Censor with asterisks** | Claude Haiku | $0.002/post | 1-2s |
| **Natural rewrites** | Claude Sonnet 3.5 | $0.012/post | 2-3s |
| **Bulk processing** | Batch API + Haiku | 50% off | 5-10s |
| **Real-time chat** | better-profanity library | Free | <0.1s |

### Key Takeaways

1. ✅ Claude is excellent for context-aware profanity filtering
2. ✅ Best approach: Intelligent rewrites with Claude 3.5 Sonnet
3. ✅ Cost: ~$0.01-0.02 per blog post (very affordable)
4. ✅ Use batch processing and caching for optimization
5. ✅ Combine with local libraries for best ROI
6. ✅ Perfect for blog post → TTS pipeline

---

**Need Help?** Check the code examples in `claude_profanity_filter_examples.py` for complete, runnable implementations.
