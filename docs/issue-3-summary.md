# Issue #3: Parallel Processing - Summary

**Research completed:** 2026-01-13
**Full report:** [parallel-processing-research.md](./parallel-processing-research.md)

## TL;DR

**Can we parallelize episode creation?** Sort of.

- ✅ **Scraping**: Fully parallel (no limits)
- ✅ **Profanity checks**: Fully parallel (no limits)
- ⚠️ **Claude cleaning**: Sequential (API limits)
- ❌ **TTS generation**: Sequential or limited (50 RPM on Tier 1)
- ✅ **Azure uploads**: Fully parallel (no limits)

**Bottleneck:** OpenAI TTS API rate limits (50 requests/minute for Tier 1)

**Best approach:** Shell script using background Bash commands

---

## Key Findings

### 1. Claude Code Task Agents

- **Task tool does NOT support background execution**
- Feature request exists (GitHub #9905, #5236) but not available yet
- Workaround: Use Bash tool with `run_in_background=True`

### 2. OpenAI TTS Rate Limits

**Tier 1 (after initial spending):**
- 50 requests per minute (RPM)
- Each article = 3-10 TTS requests (depends on length/chunking)
- **Realistic throughput:** ~5 articles per 10-15 minutes

**Rate limit is the constraint**, not compute power or Claude Code capabilities.

### 3. Recommended Workflow

Use a shell script that parallelizes independent stages:

```bash
# Parallel: Scrape 10 articles (~30s)
cat urls.txt | xargs -P 10 -I {} uv run main.py scrape {}

# Parallel: Check profanity (~5s)
find temp -name "*.txt" | xargs -P 10 grep -E "profanity_patterns"

# Sequential: Generate TTS with rate limiting (~15-20min for 10 articles)
for file in temp/*.txt; do
  uv run main.py tts "$file" -o "${file%.txt}.mp3"
  sleep 1.5  # Rate limit buffer
done

# Parallel: Upload to Azure (~30s)
find temp -name "*.mp3" | xargs -P 10 uv run main.py upload {}
```

**Total time for 10 articles:** ~20-25 minutes (vs 40-50 minutes sequential)

---

## Performance Comparison

| Workflow | 5 Articles | 10 Articles | Notes |
|----------|-----------|-------------|-------|
| Current (sequential) | 15-25 min | 30-50 min | Everything runs one-at-a-time |
| Optimized (parallel) | 8-12 min | 15-25 min | 40-60% faster |
| Theoretical (no limits) | 3-5 min | 4-6 min | If TTS had no rate limits |

**Savings:** ~40-60% time reduction with batch processing

---

## Implementation Phases

### Phase 1: Shell Script (Immediate)

**File:** `/home/david/dev/ai-generated-podcast/scripts/batch_process.sh`

- Uses existing CLI commands
- Parallelizes scraping and uploads with `xargs -P 10`
- Rate-limits TTS with `sleep 1.5` between requests
- Manual profanity review step
- **Effort:** 1 hour to create and test

### Phase 2: Python Orchestrator (Future)

**File:** `/home/david/dev/ai-generated-podcast/batch_process.py`

- Full async/await with asyncio
- Better progress tracking
- Structured error handling
- Retry logic with exponential backoff
- **Effort:** 4-6 hours to develop and test

### Phase 3: Task Agent Integration (When Available)

Wait for Claude Code to add `run_in_background` support to Task tool.

---

## Testing Plan

1. **Small batch (3 articles):** Verify workflow works end-to-end (~5-8 min)
2. **Medium batch (5 articles):** Stress test rate limiting (~10-12 min)
3. **Large batch (10 articles):** Full production test (~20-25 min)
4. **Error handling:** Include invalid URLs to test failure modes

---

## Rate Limiting Strategy

### Conservative (Tier 1 - Recommended)

```python
# Sequential TTS with 1.5s delay between requests
for article in articles:
    generate_tts(article)
    sleep(1.5)  # Buffer for safety
```

- **Throughput:** ~40 requests/minute (80% of limit)
- **Safe for production**
- **Predictable timing**

### Aggressive (Tier 2+ only)

```python
# 3-5 concurrent TTS operations with semaphore
semaphore = asyncio.Semaphore(3)
tasks = [generate_tts_with_semaphore(article) for article in articles]
await asyncio.gather(*tasks)
```

- **Throughput:** 100+ requests/minute
- **Requires Tier 2+ account**
- **Needs exponential backoff for 429 errors**

---

## Recommended Next Steps

1. **Create `scripts/batch_process.sh`** - Shell script for batch processing
2. **Test with 3 articles** - Validate workflow and timing
3. **Check OpenAI tier** - Confirm rate limits at `platform.openai.com/account/limits`
4. **Monitor usage** - Track API usage during batch runs
5. **Document workflow** - Update AGENTS.md with batch instructions

---

## References

Full research document: [parallel-processing-research.md](./parallel-processing-research.md) (900+ lines)

External sources:
- [Claude Code Background Tasks](https://apidog.com/blog/claude-code-background-tasks/)
- [GitHub Issue #9905: Background Agent Execution](https://github.com/anthropics/claude-code/issues/9905)
- [OpenAI Rate Limits](https://platform.openai.com/docs/guides/rate-limits)
- [OpenAI TTS Rate Limits by Tier](https://community.openai.com/t/tts-1-tts-1-hd-api-rpm-and-rpd-based-on-chosen-tier/783207)
