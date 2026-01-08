# Claude API Profanity Filter - Complete Resource Index

## 📚 Available Resources

This directory contains a complete implementation and documentation for using Claude API to detect and filter profanity from blog posts before TTS (Text-to-Speech) conversion.

---

## 🚀 Quick Start (Choose Your Path)

### Path 1: I want to start using it NOW (5 minutes)
1. Read: [`QUICK_REFERENCE.md`](#quick_referencemd) - Quick start section
2. Run: `python blog_to_tts_cleaner.py` to see demo
3. Integrate: Copy the example code into your project

### Path 2: I want to understand the options (15 minutes)
1. Read: [`RESEARCH_SUMMARY.md`](#research_summarymd) - Executive summary
2. Explore: [`claude_profanity_filter_examples.py`](#claude_profanity_filter_examplespy) - 7 different approaches
3. Choose: Pick the approach that fits your needs

### Path 3: I want comprehensive documentation (30 minutes)
1. Read: [`CLAUDE_PROFANITY_FILTER_GUIDE.md`](#claude_profanity_filter_guidemd) - Complete guide
2. Study: All code examples and best practices
3. Implement: Custom solution for your specific needs

---

## 📄 File Descriptions

### RESEARCH_SUMMARY.md
**What it is:** Executive summary of the entire research
**When to read:** Start here for a complete overview
**Key sections:**
- Executive summary (answers to all your questions)
- SDK differences explained
- Pricing analysis with cost estimates
- Decision matrix (should you use Claude?)
- Recommendations for your podcast project

**Read this if:** You want a comprehensive overview in one place

---

### blog_to_tts_cleaner.py
**What it is:** Production-ready Python implementation
**When to use:** When you're ready to integrate into your project
**Features:**
- ✅ Automatic caching (avoid duplicate API calls)
- ✅ Retry logic with exponential backoff
- ✅ Batch and async processing
- ✅ Cost tracking and statistics
- ✅ Complete error handling
- ✅ 650+ lines of production code

**Use this if:** You want a ready-to-use solution

**Quick usage:**
```python
from blog_to_tts_cleaner import BlogTTSCleaner

cleaner = BlogTTSCleaner()
result = cleaner.clean_post("Your blog post text here...")
print(result.cleaned_text)
```

**Demo:**
```bash
python blog_to_tts_cleaner.py
```

---

### claude_profanity_filter_examples.py
**What it is:** 7 complete examples of different approaches
**When to use:** When you want to explore different filtering strategies
**Includes:**
1. Basic profanity detection
2. Censoring with asterisks (f***)
3. Intelligent text cleaning (preserves meaning)
4. Batch processing for efficiency
5. Advanced content moderation
6. Async processing for large volumes
7. Smart blog post cleaning for TTS

**Use this if:** You want to see all options before choosing

**Run examples:**
```bash
python claude_profanity_filter_examples.py
```

---

### CLAUDE_PROFANITY_FILTER_GUIDE.md
**What it is:** Comprehensive 700+ line implementation guide
**When to read:** When you need detailed documentation
**Sections:**
- SDK overview and differences
- Installation and setup
- Implementation approaches explained
- Complete code examples
- Best practices
- Pricing analysis with optimization strategies
- Performance benchmarks
- Troubleshooting guide
- Integration example

**Use this if:** You want to understand everything in depth

---

### QUICK_REFERENCE.md
**What it is:** Quick lookup reference for common tasks
**When to use:** When you need to quickly find specific information
**Includes:**
- 30-second quick start
- Common tasks with ready-to-use code
- Pricing cheat sheet
- Model selection guide
- Performance benchmarks
- Decision tree
- Pro tips and best practices
- Troubleshooting quick fixes

**Use this if:** You know what you want to do and need code fast

---

### PROFANITY_FILTER_INDEX.md
**What it is:** This file - navigation guide for all resources

---

## 🎯 Use Case Matrix

| Your Goal | Start With | Then Read | Finally Use |
|-----------|------------|-----------|-------------|
| **Quick integration** | QUICK_REFERENCE.md | blog_to_tts_cleaner.py | Production code |
| **Explore options** | claude_profanity_filter_examples.py | RESEARCH_SUMMARY.md | Choose approach |
| **Deep understanding** | CLAUDE_PROFANITY_FILTER_GUIDE.md | All examples | Custom implementation |
| **Cost analysis** | RESEARCH_SUMMARY.md (pricing) | QUICK_REFERENCE.md (cheat sheet) | Optimize approach |
| **Best practices** | CLAUDE_PROFANITY_FILTER_GUIDE.md | QUICK_REFERENCE.md (pro tips) | Apply to project |

---

## 💰 Quick Cost Reference

| Posts/Month | Model | Monthly Cost |
|-------------|-------|--------------|
| 10 posts | Sonnet 3.5 | $0.12 |
| 100 posts | Sonnet 3.5 | $1.20 |
| 1,000 posts | Sonnet 3.5 | $12.00 |
| 1,000 posts | Haiku | $2.00 |

**Average:** ~$0.012 per 1,000-word blog post with Sonnet 3.5

---

## 🔧 Quick Setup

### 1. Install Dependencies
```bash
pip install anthropic python-dotenv
```

### 2. Get API Key
1. Visit https://console.anthropic.com/
2. Create account and generate API key

### 3. Create .env File
```bash
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### 4. Test Installation
```bash
python blog_to_tts_cleaner.py
```

---

## 📊 File Statistics

| File | Lines | Purpose | Complexity |
|------|-------|---------|------------|
| blog_to_tts_cleaner.py | 650+ | Production code | Medium |
| claude_profanity_filter_examples.py | 423 | Example code | Low |
| CLAUDE_PROFANITY_FILTER_GUIDE.md | 700+ | Documentation | N/A |
| RESEARCH_SUMMARY.md | 400+ | Summary | N/A |
| QUICK_REFERENCE.md | 300+ | Quick reference | N/A |

**Total:** ~2,500+ lines of code and documentation

---

## 🎓 Learning Path

### Beginner Path (30 minutes)
1. Read: RESEARCH_SUMMARY.md → Executive Summary
2. Run: `python blog_to_tts_cleaner.py`
3. Modify: Change the test posts in the demo
4. Integrate: Copy the code into your project

### Intermediate Path (1 hour)
1. Read: QUICK_REFERENCE.md → All sections
2. Run: `python claude_profanity_filter_examples.py`
3. Study: Different approaches in the examples
4. Implement: Choose and customize for your needs

### Advanced Path (2-3 hours)
1. Read: CLAUDE_PROFANITY_FILTER_GUIDE.md → Complete guide
2. Study: All code examples and best practices
3. Experiment: Modify examples with your data
4. Optimize: Implement caching, batching, custom logic
5. Deploy: Production implementation with monitoring

---

## 🔍 Finding What You Need

### "How do I...?"

| Question | Find Answer In |
|----------|----------------|
| ...get started quickly? | QUICK_REFERENCE.md → Quick Start |
| ...understand the costs? | RESEARCH_SUMMARY.md → Pricing Analysis |
| ...see code examples? | claude_profanity_filter_examples.py |
| ...use in production? | blog_to_tts_cleaner.py |
| ...choose a model? | QUICK_REFERENCE.md → Model Selection |
| ...optimize performance? | CLAUDE_PROFANITY_FILTER_GUIDE.md → Performance |
| ...handle errors? | blog_to_tts_cleaner.py → Error handling code |
| ...batch process? | claude_profanity_filter_examples.py → Example 4 |
| ...use async? | claude_profanity_filter_examples.py → Example 6 |
| ...understand SDKs? | RESEARCH_SUMMARY.md → SDK Clarification |

### "I want to learn about...?"

| Topic | Primary Resource | Supporting Resources |
|-------|------------------|---------------------|
| SDK differences | RESEARCH_SUMMARY.md | CLAUDE_PROFANITY_FILTER_GUIDE.md |
| Pricing | RESEARCH_SUMMARY.md | QUICK_REFERENCE.md |
| Implementation | blog_to_tts_cleaner.py | claude_profanity_filter_examples.py |
| Best practices | CLAUDE_PROFANITY_FILTER_GUIDE.md | QUICK_REFERENCE.md |
| Code examples | claude_profanity_filter_examples.py | All files |
| Integration | RESEARCH_SUMMARY.md → Integration section | blog_to_tts_cleaner.py |
| Optimization | CLAUDE_PROFANITY_FILTER_GUIDE.md → Performance | QUICK_REFERENCE.md |

---

## 🚦 Traffic Light System

### 🟢 Start Here (Everyone should read)
- **RESEARCH_SUMMARY.md** - Executive summary
- **QUICK_REFERENCE.md** - Quick start section

### 🟡 Read Next (Based on your needs)
- **blog_to_tts_cleaner.py** - If you want production code
- **claude_profanity_filter_examples.py** - If you want to explore options
- **CLAUDE_PROFANITY_FILTER_GUIDE.md** - If you want deep understanding

### 🔵 Optional (For specific needs)
- **RESEARCH_SUMMARY.md** - Full document for comprehensive reference
- **QUICK_REFERENCE.md** - Full document for troubleshooting and tips

---

## 📝 Key Takeaways (TL;DR)

1. **Use Anthropic Python SDK** (`pip install anthropic`), not Claude Code/Agent SDK
2. **Cost:** ~$0.012 per 1,000-word blog post with Claude 3.5 Sonnet
3. **Best for TTS:** Use intelligent rewriting approach, not just censoring
4. **Production code:** Use `blog_to_tts_cleaner.py` - it's ready to go
5. **Optimize:** Enable caching, use batch processing, pre-filter with local library
6. **Model choice:** Haiku for detection, Sonnet 3.5 for quality rewrites

---

## ✅ Next Steps

1. **Immediate action:**
   ```bash
   python blog_to_tts_cleaner.py  # Run the demo
   ```

2. **Integration:**
   ```python
   from blog_to_tts_cleaner import BlogTTSCleaner
   cleaner = BlogTTSCleaner()
   result = cleaner.clean_post(your_blog_post)
   ```

3. **Customize:**
   - Modify model choice based on your budget
   - Enable/disable caching as needed
   - Adjust max_retries for your use case

4. **Monitor:**
   ```python
   cleaner.print_stats()  # See costs and usage
   ```

---

## 🆘 Getting Help

### Common Issues

| Issue | Solution |
|-------|----------|
| API key not found | Check .env file, use `load_dotenv()` |
| Rate limit exceeded | Implement retry with backoff (already in production code) |
| Too expensive | Use Haiku model or batch processing |
| Too slow | Use async processing or caching |
| Inconsistent results | Set temperature=0 |

### Troubleshooting Resources
1. **CLAUDE_PROFANITY_FILTER_GUIDE.md** → Troubleshooting section
2. **QUICK_REFERENCE.md** → Troubleshooting quick fixes
3. **blog_to_tts_cleaner.py** → Error handling implementation

---

## 📚 External Resources

- **Anthropic API Console:** https://console.anthropic.com/
- **Official Documentation:** https://docs.anthropic.com/
- **Pricing Page:** https://platform.claude.com/docs/en/about-claude/pricing
- **Python SDK GitHub:** https://github.com/anthropics/anthropic-sdk-python
- **Content Moderation Guide:** https://platform.claude.com/docs/en/about-claude/use-case-guides/content-moderation

---

## 📊 Decision Flow

```
Do you need profanity filtering?
    ↓ YES
Choose your approach:
    ↓
Need instant results (< 100ms)?
    → Use local library (better-profanity)
    ↓ NO
Need context-aware filtering?
    ↓ YES
What's your primary need?
    ↓
    ├─ Detection only? → Use Claude Haiku ($0.001/post)
    ├─ Censoring (f***)? → Use Claude Haiku ($0.002/post)
    └─ Natural rewrites for TTS? → Use Claude Sonnet 3.5 ($0.012/post) ⭐
        ↓
Processing volume?
    ├─ Single posts? → Use blog_to_tts_cleaner.py
    ├─ Batch (>10 posts)? → Use batch_clean_texts()
    └─ Large volume? → Use async processing
        ↓
Optimize costs?
    ├─ Enable caching ✅
    ├─ Use batch API (50% off) ✅
    └─ Pre-filter with local library ✅
        ↓
DONE! 🎉
```

---

## 🎯 Recommended Starting Point

**For most users (blog post → TTS pipeline):**

1. Start with: **RESEARCH_SUMMARY.md** (10 minutes)
2. Run demo: `python blog_to_tts_cleaner.py` (2 minutes)
3. Integrate: Use **blog_to_tts_cleaner.py** in your project (15 minutes)
4. Reference: Keep **QUICK_REFERENCE.md** handy for lookup

**Total time to get started: ~30 minutes**

---

**Created:** January 8, 2026
**Last Updated:** January 8, 2026
**Total Resources:** 5 files, 2,500+ lines of code and documentation
