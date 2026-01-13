# Parallel Processing Research for AI-Generated Podcast

**Research Date:** 2026-01-13
**Issue:** #3 - Batch processing multiple articles in parallel

## Executive Summary

This document explores using Claude Code's Task agents and background processing capabilities to parallelize the podcast episode creation workflow, enabling batch processing of 5-10 articles simultaneously.

**Key Findings:**
- ✅ Claude Code supports background Bash commands via `run_in_background=True`
- ❌ Task tool does NOT support background execution (feature request pending)
- ⚠️ OpenAI TTS API has rate limits (50 RPM for Tier 1) that constrain parallelism
- 💡 Hybrid approach recommended: parallel scraping/cleaning, sequential TTS generation

---

## 1. Claude Code Background Processing

### Bash Tool with `run_in_background`

The Bash tool supports background execution for long-running commands:

```python
# Start a background task
Bash({
  command: "uv run main.py scrape https://example.com/post",
  run_in_background: True
})
# Returns: "Command running in background with ID: bash_5"

# Check output later
BashOutput({ bash_id: "bash_5" })

# Kill if needed
KillShell({ shell_id: "bash_5" })
```

**Key Features:**
- Background tasks run in separate shells with unique IDs
- Can monitor output, check status, and terminate as needed
- Use `/bashes` command in interactive mode to view all background shells
- Keyboard shortcut: `Ctrl+B` (press twice in tmux) to background a command

**Use Cases:**
- Long-running builds
- Server processes
- Data processing pipelines
- File operations that don't require immediate feedback

### Task Tool Limitations

**Current Status:** Task tool executes **synchronously only** - it blocks the orchestrator until completion.

**Feature Request Status:**
- GitHub Issue [#9905](https://github.com/anthropics/claude-code/issues/9905) requested background agent execution
- Closed as duplicate of #5236 (long-standing request)
- **No async Task execution available as of 2026-01-13**

**What Was Requested:**
```python
# PROPOSED (not available yet)
Task({
  subagent_type: "scraper",
  prompt: "Scrape article from URL",
  run_in_background: True  # ❌ NOT SUPPORTED
})
```

**Workaround:** Use background Bash commands to run Python scripts, not Task agents.

---

## 2. OpenAI TTS API Rate Limits

### Usage Tier Structure

OpenAI organizes accounts into usage tiers based on cumulative spending. Rate limits automatically increase as you graduate to higher tiers.

**Rate Limit Metrics:**
- **RPM** - Requests Per Minute
- **RPD** - Requests Per Day
- **TPM** - Tokens Per Minute
- **TPD** - Tokens Per Day

### TTS Model Rate Limits

**Tier 1 (Free tier: $0 spent):**
- `tts-1`: **3 RPM**
- Very limited for batch processing

**Tier 1 (After initial spending):**
- `tts-1`: **50 RPM**

**Tier 2 and above:**
- Rate limits increase with spending
- Check your account dashboard at `platform.openai.com/account/limits`

### `gpt-4o-mini-tts` Model

Your codebase uses the newer `gpt-4o-mini-tts` model with:
- **Model:** `gpt-4o-mini-tts` (newest, best quality)
- **Voice:** `cedar` (newest, most natural)
- **Max input tokens:** 2000 tokens
- **Current chunk size:** 4000 characters

**Rate Limit Considerations:**
- Rate limits apply per API account, not per process
- Multiple parallel processes share the same rate limit pool
- Hitting rate limits returns 429 errors
- Recommended: Implement exponential backoff for retries

### Concurrent Request Limits

Search results indicate concurrency limits exist but specific numbers for TTS models were not documented publicly. Common patterns:

- **Sequential RPM:** 50 requests/minute for Tier 1
- **Concurrent requests:** Not explicitly documented for TTS
- **Best practice:** Assume 5-10 concurrent connections max to avoid throttling

---

## 3. Current Podcast Workflow Analysis

### Sequential Processing Pipeline

```
User pastes URL
    ↓
1. Scrape article (10-30s)
    ↓
2. Check profanity (manual grep, 5s)
    ↓
3. Clean with Claude (optional, 30-60s)
    ↓
4. Generate TTS (2-5 min per article)
    ↓  - Chunks at 4k chars
    ↓  - Multiple OpenAI API calls
    ↓  - ffmpeg concatenation
    ↓
5. Upload to Azure (10-30s)
    ↓
6. Update episodes.yaml (manual, 30s)
    ↓
7. Regenerate feed + deploy (30s)
```

**Current Bottleneck:** TTS generation (2-5 minutes per article)

### Parallelization Opportunities

| Stage | Parallelizable? | Rate Limit? | Tool |
|-------|----------------|-------------|------|
| Scrape | ✅ Yes | ❌ No limit | Bash background |
| Profanity check | ✅ Yes | ❌ No limit | Bash background |
| Claude clean | ⚠️ Partial | ⚠️ Claude API limits | Sequential recommended |
| TTS generation | ⚠️ Limited | ⚠️ 50 RPM (Tier 1) | Sequential with queue |
| Azure upload | ✅ Yes | ❌ No limit | Bash background |
| Feed update | ❌ No | N/A | Single operation |

---

## 4. Proposed Parallel Workflow Design

### Approach A: Bash Background Commands (Recommended)

Use background Bash execution to parallelize independent stages:

```bash
# Stage 1: Parallel scraping (10 articles)
for url in "${urls[@]}"; do
  uv run main.py scrape "$url" &
done
wait  # Wait for all to complete

# Stage 2: Parallel profanity checks
for file in temp/*.txt; do
  grep -i -E "fuck|shit|damn" "$file" > "${file}.profanity" &
done
wait

# Stage 3: Sequential cleaning (if needed)
# Use Claude Agent SDK one at a time to respect API limits

# Stage 4: Rate-limited TTS queue
# Process sequentially or with controlled concurrency (3-5 max)
for file in temp/*.txt; do
  uv run main.py tts "$file" -o "temp/$(basename $file .txt).mp3"
  sleep 1.2  # Rate limit: 50 RPM = 1 per 1.2s
done

# Stage 5: Parallel uploads
for audio in temp/*.mp3; do
  uv run main.py upload "$audio" &
done
wait

# Stage 6: Batch update episodes.yaml
# Single operation with all episodes

# Stage 7: Deploy
uv run main.py feed && git add -A && git commit -m "Batch: 10 episodes" && git push
```

**Pros:**
- Uses existing CLI commands
- No code changes required
- Simple shell scripting
- Background Bash support built-in

**Cons:**
- Manual orchestration
- No progress visibility within Claude
- Error handling requires shell script logic

### Approach B: Python Orchestrator Script

Create a dedicated batch processing script:

```python
# batch_process.py
import asyncio
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

async def process_batch(urls: list[str], max_concurrent_tts: int = 3):
    """Process multiple articles in parallel with rate limiting."""

    # Stage 1: Parallel scraping
    print("Stage 1: Scraping articles...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        scrape_futures = [
            executor.submit(scrape_article, url)
            for url in urls
        ]
        articles = [f.result() for f in scrape_futures]

    # Stage 2: Parallel profanity checks
    print("Stage 2: Checking profanity...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        check_futures = [
            executor.submit(check_profanity, article)
            for article in articles
        ]
        profanity_results = [f.result() for f in check_futures]

    # Stage 3: Sequential cleaning (respects Claude API limits)
    print("Stage 3: Cleaning with Claude...")
    cleaned_articles = []
    for article, has_profanity in zip(articles, profanity_results):
        if has_profanity:
            cleaned = await clean_file(article)
            cleaned_articles.append(cleaned)
        else:
            cleaned_articles.append(article)

    # Stage 4: Rate-limited TTS queue
    print("Stage 4: Generating TTS (rate limited)...")
    semaphore = asyncio.Semaphore(max_concurrent_tts)

    async def tts_with_limit(article):
        async with semaphore:
            result = await generate_tts(article)
            await asyncio.sleep(1.2)  # Rate limit: 50 RPM
            return result

    audio_files = await asyncio.gather(*[
        tts_with_limit(article)
        for article in cleaned_articles
    ])

    # Stage 5: Parallel uploads
    print("Stage 5: Uploading to Azure...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        upload_futures = [
            executor.submit(upload_blob, audio_file)
            for audio_file in audio_files
        ]
        blob_urls = [f.result() for f in upload_futures]

    # Stage 6: Batch update episodes.yaml
    print("Stage 6: Updating feed...")
    for article, blob_url in zip(cleaned_articles, blob_urls):
        add_episode(article.metadata, blob_url)

    # Stage 7: Deploy
    print("Stage 7: Regenerating RSS and deploying...")
    write_feed()

    return blob_urls
```

**Usage:**
```bash
uv run batch_process.py \
  --urls urls.txt \
  --max-concurrent-tts 3
```

**Pros:**
- Clean Python async/await pattern
- Built-in rate limiting with semaphores
- Progress tracking and error handling
- Reusable for future batches

**Cons:**
- Requires new Python module
- More complex than shell script
- Needs testing and debugging

### Approach C: Hybrid (Best of Both)

Use background Bash for independent stages + Python for TTS queue:

```bash
# batch.sh - Orchestration script

# Stage 1: Parallel scraping
echo "Scraping 10 articles..."
cat urls.txt | xargs -P 10 -I {} bash -c 'uv run main.py scrape "{}"'

# Stage 2: Profanity checks
echo "Checking profanity..."
find temp -name "*.txt" | xargs -P 10 -I {} bash -c 'grep -i -E "fuck|shit|damn" "{}" > "{}.profanity" 2>/dev/null'

# Stage 3: Manual review
echo "Review profanity results and edit if needed..."
ls temp/*.profanity
read -p "Press enter when ready to continue..."

# Stage 4: Rate-limited TTS (Python helper)
echo "Generating TTS with rate limiting..."
uv run python3 -c "
import os
import time
import subprocess
from pathlib import Path

files = sorted(Path('temp').glob('*.txt'))
for i, file in enumerate(files):
    print(f'[{i+1}/{len(files)}] Processing {file.name}...')
    subprocess.run(['uv', 'run', 'main.py', 'tts', str(file), '-o', f'temp/{file.stem}.mp3'])
    if i < len(files) - 1:
        time.sleep(1.5)  # Rate limit buffer
"

# Stage 5: Parallel uploads
echo "Uploading to Azure..."
find temp -name "*.mp3" | xargs -P 10 -I {} uv run main.py upload {}

# Stage 6-7: Manual episode.yaml update + deploy
echo "Update episodes.yaml manually, then run:"
echo "uv run main.py feed && git add -A && git commit -m 'Batch episodes' && git push"
```

**Pros:**
- Simple shell script with parallel xargs
- Python one-liner for rate-limited TTS
- No new files to maintain
- Easy to understand and modify

**Cons:**
- Requires manual steps (review profanity, update episodes.yaml)
- Less sophisticated error handling

---

## 5. Recommended Implementation

### Phase 1: Shell Script with Background Bash (Immediate)

**Action:** Create `/home/david/dev/ai-generated-podcast/scripts/batch_process.sh`

```bash
#!/bin/bash
# Batch process multiple blog posts into podcast episodes

set -euo pipefail

URLS_FILE="${1:-urls.txt}"
MAX_CONCURRENT_TTS=3
TEMP_DIR="temp/batch-$(date +%Y%m%d-%H%M%S)"

mkdir -p "$TEMP_DIR"

echo "=== Stage 1: Scraping articles ==="
cat "$URLS_FILE" | xargs -P 10 -I {} bash -c "
  uv run main.py scrape '{}' -o '$TEMP_DIR/\$(basename '{}').txt' || echo 'Failed: {}'
"

echo "=== Stage 2: Profanity checks ==="
find "$TEMP_DIR" -name "*.txt" -type f | while read file; do
  echo "Checking: \$(basename \$file)"
  if grep -q -i -E "fuck|shit|damn|bitch|bastard" "\$file"; then
    echo "  ⚠️  Profanity found - manual edit needed"
    grep -n -i -E "fuck|shit|damn|bitch|bastard" "\$file" | head -5
  else
    echo "  ✓ Clean"
  fi
done

echo ""
read -p "Edit files if needed, then press Enter to continue..."

echo "=== Stage 3: TTS generation (rate limited) ==="
article_count=\$(find "$TEMP_DIR" -name "*.txt" -type f | wc -l)
current=0

find "$TEMP_DIR" -name "*.txt" -type f | while read file; do
  current=\$((current + 1))
  echo "[\$current/\$article_count] Generating TTS: \$(basename \$file)"

  uv run main.py tts "\$file" -o "\${file%.txt}.mp3" -p openai -v cedar

  # Rate limit: 50 RPM = 1.2s per request (with buffer)
  if [ \$current -lt \$article_count ]; then
    sleep 1.5
  fi
done

echo "=== Stage 4: Uploading to Azure ==="
find "$TEMP_DIR" -name "*.mp3" -type f | xargs -P 10 -I {} bash -c "
  filename=\$(basename '{}')
  uv run main.py upload '{}' --name \"\$filename\" || echo 'Failed: {}'
"

echo "=== Stage 5: Manual steps ==="
echo "1. Add episodes to episodes.yaml"
echo "2. Run: uv run main.py feed"
echo "3. Run: git add -A && git commit -m 'Batch import' && git push"
echo ""
echo "Files ready in: $TEMP_DIR"
```

**Usage:**
```bash
# Create urls.txt with one URL per line
cat > urls.txt << EOF
https://blog.example.com/post1
https://blog.example.com/post2
https://blog.example.com/post3
EOF

# Run batch processor
bash scripts/batch_process.sh urls.txt
```

### Phase 2: Python Async Orchestrator (Future)

**Action:** Create `/home/david/dev/ai-generated-podcast/batch_process.py` with proper async/await patterns, semaphores for rate limiting, and comprehensive error handling.

**Benefits:**
- Better progress tracking
- Structured error handling
- Reusable for automation
- Can integrate with CI/CD

### Phase 3: Claude Agent SDK Integration (When Available)

**Action:** If Task tool gets `run_in_background` support in the future, refactor to use Task agents for true parallel processing.

**Benefits:**
- Claude-native orchestration
- Better integration with Claude Code workflow
- Progress visibility in Claude UI

---

## 6. Rate Limiting Strategy

### Conservative Approach (Recommended for Tier 1)

**Tier 1 Limit:** 50 RPM

**Strategy:**
- Process TTS sequentially with 1.5s delays
- Chunk size: 4000 chars (current)
- Per-article chunks: ~3-10 (varies by length)
- Effective throughput: ~40 requests/minute (buffer for retries)

**Batch Estimates:**
- 5 articles: 5-10 minutes total
- 10 articles: 10-20 minutes total

### Aggressive Approach (For Tier 2+)

If you upgrade to Tier 2 (check `platform.openai.com/account/limits`):

**Strategy:**
- Process 3-5 articles concurrently
- Use asyncio semaphore to limit concurrent TTS calls
- Implement exponential backoff for 429 errors
- Monitor rate limit headers in API responses

**Example:**
```python
semaphore = asyncio.Semaphore(3)  # Max 3 concurrent TTS operations

async def tts_with_backoff(text, output, max_retries=3):
    async with semaphore:
        for attempt in range(max_retries):
            try:
                return await generate_tts_async(text, output)
            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(wait_time)
                else:
                    raise
```

---

## 7. Pseudo-Code for Parallel Workflow

### High-Level Orchestration

```python
async def batch_process_episodes(urls: list[str]):
    """
    Process multiple articles into podcast episodes with parallel stages.

    Stages:
    1. Scrape articles (parallel, no limits)
    2. Check profanity (parallel, no limits)
    3. Clean with Claude (sequential, API limits)
    4. Generate TTS (rate-limited queue)
    5. Upload to Azure (parallel, no limits)
    6. Update feed (single operation)
    """

    # Stage 1: Parallel scraping
    print(f"Scraping {len(urls)} articles...")
    articles = await asyncio.gather(*[
        scrape_article_async(url) for url in urls
    ])

    # Stage 2: Parallel profanity detection
    print("Checking for profanity...")
    profanity_flags = await asyncio.gather(*[
        check_profanity_async(article) for article in articles
    ])

    # Stage 3: Sequential cleaning (respects Claude API rate limits)
    print("Cleaning articles with profanity...")
    cleaned_articles = []
    for article, has_profanity in zip(articles, profanity_flags):
        if has_profanity:
            print(f"  Cleaning: {article.title}")
            cleaned = await clean_with_claude(article)
            cleaned_articles.append(cleaned)
        else:
            cleaned_articles.append(article)

    # Stage 4: Rate-limited TTS queue
    print("Generating TTS audio (rate limited to 50 RPM)...")
    tts_semaphore = asyncio.Semaphore(1)  # Sequential for Tier 1

    async def generate_tts_rate_limited(article, index):
        async with tts_semaphore:
            print(f"  [{index+1}/{len(cleaned_articles)}] Generating: {article.title}")
            audio_file = await generate_tts_async(article)
            await asyncio.sleep(1.5)  # Rate limit buffer
            return audio_file

    audio_files = await asyncio.gather(*[
        generate_tts_rate_limited(article, i)
        for i, article in enumerate(cleaned_articles)
    ])

    # Stage 5: Parallel uploads
    print("Uploading to Azure...")
    blob_urls = await asyncio.gather(*[
        upload_to_azure_async(audio_file)
        for audio_file in audio_files
    ])

    # Stage 6: Update feed
    print("Updating RSS feed...")
    for article, blob_url in zip(cleaned_articles, blob_urls):
        add_episode_to_yaml(article, blob_url)

    write_feed()

    print(f"✓ Batch complete: {len(urls)} episodes processed")
    return blob_urls


# Helper functions (async wrappers)

async def scrape_article_async(url: str):
    """Run scraper in thread pool to avoid blocking."""
    return await asyncio.to_thread(scrape_article, url)

async def check_profanity_async(article):
    """Check for profanity patterns."""
    patterns = ["fuck", "shit", "damn", "bitch", "bastard"]
    text = article.text.lower()
    return any(pattern in text for pattern in patterns)

async def clean_with_claude(article):
    """Clean article using Claude Agent SDK."""
    return await clean_file(article.path)

async def generate_tts_async(article):
    """Generate TTS audio from article text."""
    return await asyncio.to_thread(
        generate_audio,
        article.text,
        article.audio_path,
        provider="openai",
        voice="cedar"
    )

async def upload_to_azure_async(audio_file):
    """Upload audio file to Azure Blob Storage."""
    return await asyncio.to_thread(upload_blob, audio_file)
```

### Stage-by-Stage Detail

#### Stage 1: Scraping

```python
async def scrape_all_articles(urls: list[str]) -> list[Article]:
    """Scrape multiple articles in parallel."""

    async def scrape_with_error_handling(url: str) -> Article | None:
        try:
            return await scrape_article_async(url)
        except Exception as e:
            print(f"✗ Failed to scrape {url}: {e}")
            return None

    results = await asyncio.gather(*[
        scrape_with_error_handling(url) for url in urls
    ])

    # Filter out failed scrapes
    articles = [a for a in results if a is not None]
    print(f"✓ Scraped {len(articles)}/{len(urls)} articles")
    return articles
```

#### Stage 2: Profanity Detection

```python
async def detect_profanity_batch(articles: list[Article]) -> dict[Article, list[str]]:
    """Detect profanity in multiple articles in parallel."""

    profanity_patterns = [
        r"\bfuck",
        r"\bsh[i!]t",
        r"\bdamn",
        r"\bbitch",
        r"\bbastard"
    ]

    async def find_profanity(article: Article) -> tuple[Article, list[str]]:
        import re
        matches = []
        for pattern in profanity_patterns:
            found = re.findall(pattern, article.text, re.IGNORECASE)
            matches.extend(found)
        return (article, matches)

    results = await asyncio.gather(*[
        find_profanity(article) for article in articles
    ])

    return dict(results)
```

#### Stage 3: Cleaning

```python
async def clean_articles_sequentially(
    profanity_map: dict[Article, list[str]]
) -> list[Article]:
    """Clean articles with profanity using Claude Agent SDK (sequential)."""

    cleaned = []

    for article, profanity_list in profanity_map.items():
        if profanity_list:
            print(f"Cleaning {article.title} ({len(profanity_list)} matches)...")
            result = await clean_file(article.path, model="sonnet")
            article.was_edited = result.was_edited
            article.changes = result.changes_made

        cleaned.append(article)

    return cleaned
```

#### Stage 4: TTS Generation (Rate Limited)

```python
async def generate_tts_batch(
    articles: list[Article],
    max_concurrent: int = 1,  # Tier 1: sequential
    rate_limit_delay: float = 1.5
) -> list[Path]:
    """Generate TTS for multiple articles with rate limiting."""

    semaphore = asyncio.Semaphore(max_concurrent)

    async def generate_with_rate_limit(article: Article, index: int) -> Path:
        async with semaphore:
            print(f"[{index+1}/{len(articles)}] TTS: {article.title}")

            # Generate audio
            audio_path = Path(f"temp/{article.slug}.mp3")
            await asyncio.to_thread(
                generate_audio,
                article.text,
                audio_path,
                provider="openai",
                voice="cedar"
            )

            # Rate limit delay (except for last item)
            if index < len(articles) - 1:
                await asyncio.sleep(rate_limit_delay)

            return audio_path

    audio_paths = await asyncio.gather(*[
        generate_with_rate_limit(article, i)
        for i, article in enumerate(articles)
    ])

    return audio_paths
```

#### Stage 5: Azure Upload

```python
async def upload_batch(audio_files: list[Path]) -> list[str]:
    """Upload multiple audio files to Azure in parallel."""

    async def upload_with_error_handling(audio_file: Path) -> str | None:
        try:
            blob_url = await asyncio.to_thread(upload_blob, audio_file, audio_file.name)
            print(f"✓ Uploaded: {audio_file.name}")
            return blob_url
        except Exception as e:
            print(f"✗ Failed to upload {audio_file.name}: {e}")
            return None

    results = await asyncio.gather(*[
        upload_with_error_handling(audio_file) for audio_file in audio_files
    ])

    # Filter failures
    urls = [url for url in results if url is not None]
    print(f"✓ Uploaded {len(urls)}/{len(audio_files)} files")
    return urls
```

---

## 8. Testing Strategy

### Small Batch Test (3 articles)

```bash
# Test with 3 short articles
cat > test_urls.txt << EOF
https://blog.example.com/short-post-1
https://blog.example.com/short-post-2
https://blog.example.com/short-post-3
EOF

# Run batch processor
time bash scripts/batch_process.sh test_urls.txt

# Expected: ~5-8 minutes total
# - Scraping: 30s
# - Profanity checks: 5s
# - TTS: 3-4 min (sequential)
# - Uploads: 30s
```

### Medium Batch Test (5-10 articles)

```bash
# Test with 10 typical blog posts
# Expected: 15-25 minutes total
```

### Error Handling Test

```bash
# Include invalid URLs and Medium articles (blocked)
# Verify graceful failures and partial completion
```

---

## 9. Future Enhancements

### When Task Tool Gets `run_in_background`

If GitHub issue #5236 is resolved:

```python
# Future: True parallel agent execution
task_ids = []

for url in urls:
    task_id = Task({
        prompt: f"Scrape and process article from {url}",
        run_in_background: True  # Future feature
    })
    task_ids.append(task_id)

# Monitor progress
for task_id in task_ids:
    output = AgentOutput({ agent_id: task_id })
    print(output.progress)
```

### ElevenLabs Alternative

If OpenAI rate limits become problematic:

```python
# Fallback to ElevenLabs (10k char chunks, different rate limits)
generate_audio(
    text,
    output_path,
    provider="elevenlabs",
    voice=None  # Uses default voice
)
```

### Webhook Notifications

```python
# Notify when batch completes
import requests

def notify_completion(episode_count: int, duration: float):
    requests.post("https://hooks.slack.com/...", json={
        "text": f"Batch complete: {episode_count} episodes in {duration:.1f}m"
    })
```

---

## 10. Conclusion

### What We Learned

1. **Task Tool:** Currently synchronous only - no `run_in_background` support
2. **Bash Tool:** Full background support with monitoring and control
3. **OpenAI TTS:** 50 RPM rate limit for Tier 1 constrains parallel TTS
4. **Best Approach:** Hybrid bash script with parallel scraping/uploads, sequential TTS

### Immediate Action Items

1. ✅ Create `scripts/batch_process.sh` for shell-based batch processing
2. ✅ Test with 3-5 articles to validate workflow
3. ⏳ Monitor OpenAI usage tier and adjust rate limits
4. ⏳ Consider Python orchestrator script for better progress tracking

### Long-Term Roadmap

1. **Q1 2026:** Shell script batch processor (manual orchestration)
2. **Q2 2026:** Python async orchestrator with error recovery
3. **Future:** Task agent background execution (when available)

### Performance Expectations

**Current (Sequential):**
- 1 article: 3-5 minutes
- 10 articles: 30-50 minutes

**With Batch Processing (Optimized):**
- 10 articles: 15-20 minutes (40-60% faster)
- Parallelizes everything except TTS generation
- Rate limit is the bottleneck

---

## References

- [How to run Claude Code in parallel | Ona](https://ona.com/stories/parallelize-claude-code)
- [What is the Task Tool in Claude Code | ClaudeLog](https://claudelog.com/faqs/what-is-task-tool-in-claude-code/)
- [How Claude Code Background Tasks Are Revolutionizing Developer Workflows](https://apidog.com/blog/claude-code-background-tasks/)
- [Feature Request: Background Agent Execution (Issue #9905)](https://github.com/anthropics/claude-code/issues/9905)
- [Background Bash Commands in Claude Code](https://harishgarg.com/running-bash-commands-in-the-background-inside-claude-code)
- [OpenAI Rate Limits Documentation](https://platform.openai.com/docs/guides/rate-limits)
- [Tts-1 & tts-1-hd API RPM based on tier](https://community.openai.com/t/tts-1-tts-1-hd-api-rpm-and-rpd-based-on-chosen-tier/783207)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-13
**Maintainer:** Research for Issue #3
