"""
Blog Post to TTS Cleaner
=========================

A practical, production-ready implementation for cleaning blog posts
before TTS conversion using Claude API.

This module is optimized for:
- Cost efficiency (caching, batching)
- Speed (async processing)
- Quality (context-aware cleaning)
- Reliability (error handling, retries)

Usage:
    from blog_to_tts_cleaner import BlogTTSCleaner

    cleaner = BlogTTSCleaner()
    cleaned = cleaner.clean_post("Your blog content here...")
    print(cleaned)
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass
import asyncio

try:
    from anthropic import Anthropic, AsyncAnthropic, RateLimitError, APIError
    from dotenv import load_dotenv
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install anthropic python-dotenv")
    exit(1)

# Load environment variables
load_dotenv()


@dataclass
class CleaningResult:
    """Result of text cleaning operation."""
    original_text: str
    cleaned_text: str
    changes_made: bool
    profanity_detected: bool
    summary: Optional[str] = None
    cached: bool = False
    processing_time: float = 0.0


class BlogTTSCleaner:
    """
    Production-ready blog post cleaner for TTS conversion.

    Features:
    - Automatic caching to avoid duplicate API calls
    - Retry logic with exponential backoff
    - Support for batch processing
    - Async operations for large volumes
    - Cost tracking
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: str = ".cache/blog_cleaner",
        model: str = "claude-3-5-sonnet-20241022",
        enable_cache: bool = True,
        max_retries: int = 3
    ):
        """
        Initialize the blog cleaner.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            cache_dir: Directory for caching cleaned texts
            model: Claude model to use (sonnet-3.5 recommended for quality)
            enable_cache: Whether to cache results
            max_retries: Maximum retry attempts for failed API calls
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not found. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = Anthropic(api_key=self.api_key)
        self.async_client = AsyncAnthropic(api_key=self.api_key)
        self.model = model
        self.max_retries = max_retries

        # Cache setup
        self.enable_cache = enable_cache
        self.cache_dir = Path(cache_dir)
        if enable_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Stats tracking
        self.stats = {
            "total_processed": 0,
            "cache_hits": 0,
            "api_calls": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
        }

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.sha256(text.encode()).hexdigest()

    def _get_from_cache(self, text: str) -> Optional[CleaningResult]:
        """Retrieve cached result if available."""
        if not self.enable_cache:
            return None

        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text())
                self.stats["cache_hits"] += 1
                result = CleaningResult(
                    original_text=text,
                    cleaned_text=data["cleaned_text"],
                    changes_made=data["changes_made"],
                    profanity_detected=data["profanity_detected"],
                    summary=data.get("summary"),
                    cached=True,
                    processing_time=0.0
                )
                return result
            except (json.JSONDecodeError, KeyError):
                # Corrupted cache, delete it
                cache_file.unlink()
                return None

        return None

    def _save_to_cache(self, text: str, result: CleaningResult):
        """Save result to cache."""
        if not self.enable_cache:
            return

        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.json"

        data = {
            "cleaned_text": result.cleaned_text,
            "changes_made": result.changes_made,
            "profanity_detected": result.profanity_detected,
            "summary": result.summary,
            "model": self.model,
        }

        cache_file.write_text(json.dumps(data, indent=2))

    def _create_cleaning_prompt(self, text: str) -> str:
        """Create the prompt for Claude."""
        return f"""You are a professional content editor preparing blog posts for text-to-speech conversion.

Your task: Remove or replace profanity and inappropriate language while maintaining the author's voice, tone, and meaning.

Guidelines:
- Replace profanity with appropriate alternatives (e.g., "damn" → "darn", "shit" → "shoot")
- Preserve the emotional impact and intent
- Keep the text natural-sounding when read aloud
- Maintain all factual content and key points
- If profanity appears in direct quotes and is essential to the quote's meaning, you may keep it, but note it
- Make the result suitable for a general audience

Blog post to clean:
<text>{text}</text>

Respond with ONLY a valid JSON object (no markdown, no code blocks) in this exact format:
{{
    "cleaned_text": "The cleaned version of the text",
    "changes_made": true or false,
    "profanity_detected": true or false,
    "summary": "Brief description of changes made, or 'No changes needed' if text was clean"
}}"""

    def clean_post(self, text: str) -> CleaningResult:
        """
        Clean a single blog post.

        Args:
            text: The blog post content to clean

        Returns:
            CleaningResult with cleaned text and metadata
        """
        start_time = time.time()

        # Check cache first
        cached_result = self._get_from_cache(text)
        if cached_result:
            return cached_result

        # Clean with Claude
        for attempt in range(self.max_retries):
            try:
                prompt = self._create_cleaning_prompt(text)

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=len(text.split()) * 2 + 500,  # Adaptive max_tokens
                    temperature=0.3,  # Slight creativity for natural rewrites
                    messages=[{"role": "user", "content": prompt}]
                )

                # Track stats
                self.stats["api_calls"] += 1
                self.stats["total_input_tokens"] += response.usage.input_tokens
                self.stats["total_output_tokens"] += response.usage.output_tokens

                # Parse response
                response_text = response.content[0].text.strip()

                # Remove markdown code blocks if present
                if response_text.startswith("```"):
                    response_text = "\n".join(response_text.split("\n")[1:-1])

                result_data = json.loads(response_text)

                result = CleaningResult(
                    original_text=text,
                    cleaned_text=result_data["cleaned_text"],
                    changes_made=result_data["changes_made"],
                    profanity_detected=result_data.get("profanity_detected", False),
                    summary=result_data.get("summary"),
                    cached=False,
                    processing_time=time.time() - start_time
                )

                # Save to cache
                self._save_to_cache(text, result)
                self.stats["total_processed"] += 1

                return result

            except RateLimitError:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Rate limit hit. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    raise

            except APIError as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"API error: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise

            except json.JSONDecodeError as e:
                print(f"Failed to parse Claude response: {e}")
                print(f"Response was: {response_text}")
                # Return original text as fallback
                return CleaningResult(
                    original_text=text,
                    cleaned_text=text,
                    changes_made=False,
                    profanity_detected=False,
                    summary="Failed to parse response",
                    cached=False,
                    processing_time=time.time() - start_time
                )

    def clean_posts_batch(self, texts: List[str]) -> List[CleaningResult]:
        """
        Clean multiple blog posts efficiently.

        Args:
            texts: List of blog post texts to clean

        Returns:
            List of CleaningResults in the same order as input
        """
        results = []

        # First, check cache for all texts
        uncached_indices = []
        uncached_texts = []

        for idx, text in enumerate(texts):
            cached = self._get_from_cache(text)
            if cached:
                results.append((idx, cached))
            else:
                uncached_indices.append(idx)
                uncached_texts.append(text)

        # Process uncached texts
        if uncached_texts:
            # For batch processing, we could send them all at once
            # For now, process individually for better error handling
            for idx, text in zip(uncached_indices, uncached_texts):
                result = self.clean_post(text)
                results.append((idx, result))

        # Sort by original index and return
        results.sort(key=lambda x: x[0])
        return [r[1] for r in results]

    async def _clean_post_async(self, text: str) -> CleaningResult:
        """Async version of clean_post."""
        start_time = time.time()

        # Check cache first
        cached_result = self._get_from_cache(text)
        if cached_result:
            return cached_result

        # Clean with Claude asynchronously
        prompt = self._create_cleaning_prompt(text)

        response = await self.async_client.messages.create(
            model=self.model,
            max_tokens=len(text.split()) * 2 + 500,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        # Track stats
        self.stats["api_calls"] += 1
        self.stats["total_input_tokens"] += response.usage.input_tokens
        self.stats["total_output_tokens"] += response.usage.output_tokens

        # Parse response
        response_text = response.content[0].text.strip()
        if response_text.startswith("```"):
            response_text = "\n".join(response_text.split("\n")[1:-1])

        result_data = json.loads(response_text)

        result = CleaningResult(
            original_text=text,
            cleaned_text=result_data["cleaned_text"],
            changes_made=result_data["changes_made"],
            profanity_detected=result_data.get("profanity_detected", False),
            summary=result_data.get("summary"),
            cached=False,
            processing_time=time.time() - start_time
        )

        # Save to cache
        self._save_to_cache(text, result)
        self.stats["total_processed"] += 1

        return result

    async def clean_posts_async(self, texts: List[str]) -> List[CleaningResult]:
        """
        Clean multiple posts concurrently (fastest method).

        Args:
            texts: List of blog post texts to clean

        Returns:
            List of CleaningResults in the same order as input
        """
        tasks = [self._clean_post_async(text) for text in texts]
        results = await asyncio.gather(*tasks)
        return results

    def get_cost_estimate(self) -> Dict[str, float]:
        """
        Get cost estimate based on usage stats.

        Returns:
            Dict with cost breakdown
        """
        # Pricing as of January 2026
        pricing = {
            "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
            "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
            "claude-opus-4-5-20251101": {"input": 5.00, "output": 25.00},
        }

        model_pricing = pricing.get(
            self.model,
            {"input": 3.00, "output": 15.00}  # Default to Sonnet
        )

        input_cost = (self.stats["total_input_tokens"] / 1_000_000) * model_pricing["input"]
        output_cost = (self.stats["total_output_tokens"] / 1_000_000) * model_pricing["output"]
        total_cost = input_cost + output_cost

        return {
            "input_tokens": self.stats["total_input_tokens"],
            "output_tokens": self.stats["total_output_tokens"],
            "input_cost": round(input_cost, 4),
            "output_cost": round(output_cost, 4),
            "total_cost": round(total_cost, 4),
            "api_calls": self.stats["api_calls"],
            "cache_hits": self.stats["cache_hits"],
            "cache_hit_rate": round(
                self.stats["cache_hits"] / max(1, self.stats["total_processed"]) * 100, 1
            ),
        }

    def print_stats(self):
        """Print usage statistics and cost estimate."""
        costs = self.get_cost_estimate()

        print("\n" + "=" * 60)
        print("Blog TTS Cleaner - Usage Statistics")
        print("=" * 60)
        print(f"Total posts processed: {self.stats['total_processed']}")
        print(f"Cache hits: {self.stats['cache_hits']} ({costs['cache_hit_rate']}%)")
        print(f"API calls made: {self.stats['api_calls']}")
        print(f"Total input tokens: {costs['input_tokens']:,}")
        print(f"Total output tokens: {costs['output_tokens']:,}")
        print(f"\nCost Breakdown:")
        print(f"  Input cost:  ${costs['input_cost']:.4f}")
        print(f"  Output cost: ${costs['output_cost']:.4f}")
        print(f"  Total cost:  ${costs['total_cost']:.4f}")
        print("=" * 60 + "\n")


# Convenience functions for quick usage
def clean_text(text: str) -> str:
    """
    Quick function to clean a single text.

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    cleaner = BlogTTSCleaner()
    result = cleaner.clean_post(text)
    return result.cleaned_text


def clean_texts(texts: List[str]) -> List[str]:
    """
    Quick function to clean multiple texts.

    Args:
        texts: List of texts to clean

    Returns:
        List of cleaned texts
    """
    cleaner = BlogTTSCleaner()
    results = cleaner.clean_posts_batch(texts)
    return [r.cleaned_text for r in results]


# Example usage
if __name__ == "__main__":
    print("Blog to TTS Cleaner - Demo")
    print("=" * 60)

    # Initialize cleaner
    cleaner = BlogTTSCleaner(
        model="claude-3-5-sonnet-20241022",  # Best quality for blog posts
        enable_cache=True
    )

    # Example blog posts
    test_posts = [
        """
        Hey everyone! I just had the most frustrating day dealing with this damn API.
        The documentation is absolute shit and nothing works as expected.
        What the hell were they thinking?
        """,
        """
        This is a perfectly clean blog post with no profanity at all.
        Just sharing some thoughts about technology and programming.
        Everything is great!
        """,
        """
        I was debugging my code when I realized the issue. The damn configuration
        file was pointing to the wrong endpoint. Once I fixed that crap, everything
        started working beautifully. Sometimes the solution is simpler than you think!
        """
    ]

    print("\n1. Cleaning individual posts:")
    print("-" * 60)

    for i, post in enumerate(test_posts, 1):
        print(f"\nPost #{i}:")
        result = cleaner.clean_post(post.strip())

        print(f"  Profanity detected: {result.profanity_detected}")
        print(f"  Changes made: {result.changes_made}")
        if result.changes_made:
            print(f"  Summary: {result.summary}")
        print(f"  Processing time: {result.processing_time:.2f}s")
        print(f"  From cache: {result.cached}")
        print(f"\n  Original: {result.original_text[:100]}...")
        print(f"  Cleaned:  {result.cleaned_text[:100]}...")

    print("\n\n2. Batch processing:")
    print("-" * 60)
    batch_results = cleaner.clean_posts_batch(test_posts)
    print(f"Processed {len(batch_results)} posts")

    print("\n\n3. Async processing (fastest):")
    print("-" * 60)
    async_results = asyncio.run(cleaner.clean_posts_async(test_posts))
    print(f"Processed {len(async_results)} posts asynchronously")

    # Print statistics
    cleaner.print_stats()

    print("\n4. Testing cache (second run should be instant):")
    print("-" * 60)
    start = time.time()
    cached_result = cleaner.clean_post(test_posts[0].strip())
    print(f"From cache: {cached_result.cached}")
    print(f"Time: {time.time() - start:.3f}s")

    print("\n" + "=" * 60)
    print("Demo complete!")
