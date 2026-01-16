# Issue #4: Running Claude Code in GitHub Actions - Recommendation

**TL;DR:** ✅ **YES, Claude Code can run in GitHub Actions.** Two viable approaches:

1. **Official GitHub Action** (recommended for intelligence)
2. **Direct Python Scripts** (recommended for cost/simplicity)

---

## Quick Decision Matrix

Choose based on your priorities:

| Priority | Recommended Approach |
|----------|---------------------|
| **Low cost, simple workflow** | Python Scripts (no Claude) |
| **Intelligent, adaptive, error-handling** | Official Claude Code Action |
| **Interactive PR reviews** | Official Claude Code Action |
| **Scheduled automation** | Either approach works |

---

## Approach 1: Official Claude Code Action ⭐ RECOMMENDED FOR INTELLIGENCE

### Setup (5 minutes)

1. **Install GitHub App:**
   ```bash
   claude /install-github-app
   ```

2. **Add Secret:**
   - Go to: Settings → Secrets and variables → Actions
   - Add: `ANTHROPIC_API_KEY` (your Anthropic API key)

3. **Create `.github/workflows/claude-podcast.yml`:**
   ```yaml
   name: Claude Podcast Generator

   on:
     workflow_dispatch:
       inputs:
         blog_url:
           description: 'Blog post URL'
           required: true
         episode_title:
           description: 'Episode title'
           required: true

   jobs:
     generate:
       runs-on: ubuntu-latest
       permissions:
         contents: write
         pull-requests: write
         issues: write
       steps:
         - uses: actions/checkout@v5
           with:
             fetch-depth: 1

         - uses: anthropics/claude-code-action@v1
           with:
             anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
             prompt: |
               Generate a podcast episode from ${{ github.event.inputs.blog_url }}:

               1. Scrape the article using scraper.py
               2. Check for profanity (fuck/shit/damn) and clean if needed
               3. Generate TTS audio: uv run main.py tts temp/article.txt -o "temp/${{ github.event.inputs.episode_title }}.mp3"
               4. Upload to Azure: uv run main.py upload "temp/${{ github.event.inputs.episode_title }}.mp3" --name "${{ github.event.inputs.episode_title }}.m4a"
               5. Update episodes.yaml with metadata
               6. Regenerate RSS feed: uv run main.py feed
               7. Commit and push changes
   ```

4. **Test:**
   - Go to Actions → Claude Podcast Generator → Run workflow
   - Enter blog URL and title

### Pros
- ✅ Intelligent error handling
- ✅ Automatic profanity filtering
- ✅ Adaptive scraping (handles tricky sites)
- ✅ Can respond to PR comments (`@claude generate episode from <url>`)

### Cons
- ❌ Higher cost (~$0.50-$2.00 per episode)
- ❌ Requires Anthropic API key

---

## Approach 2: Direct Python Scripts ⭐ RECOMMENDED FOR SIMPLICITY

### Setup (10 minutes)

1. **Create helper script `scripts/add_episode.py`:**
   ```python
   import yaml
   import sys
   from datetime import datetime, timezone

   def add_episode(title, blog_url, author):
       with open('episodes.yaml', 'r') as f:
           episodes = yaml.safe_load(f) or []

       episodes.append({
           'title': title,
           'published_date': datetime.now(timezone.utc).isoformat(),
           'blog_url': blog_url,
           'was_edited': False,
           'author': author,
           'article_date': datetime.now().date().isoformat(),
           'tech': 'OpenAI TTS (cedar)',
           'description': f'Generated from {blog_url}'
       })

       with open('episodes.yaml', 'w') as f:
           yaml.dump(episodes, f, default_flow_style=False)

   if __name__ == '__main__':
       add_episode(sys.argv[1], sys.argv[2], sys.argv[3])
   ```

2. **Create `.github/workflows/generate-episode.yml`:**
   ```yaml
   name: Generate Podcast Episode

   on:
     workflow_dispatch:
       inputs:
         blog_url:
           description: 'Blog post URL'
           required: true
         episode_title:
           description: 'Episode title'
           required: true
         author:
           description: 'Author name'
           required: true

   jobs:
     generate:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v5

         - uses: actions/setup-python@v5
           with:
             python-version: '3.12'

         - name: Install uv
           run: curl -LsSf https://astral.sh/uv/install.sh | sh

         - name: Install dependencies
           run: uv sync

         - name: Scrape article
           run: uv run main.py scrape "${{ github.event.inputs.blog_url }}"

         - name: Check for profanity
           id: profanity
           run: |
             if grep -i -E "fuck|shit|damn|bitch|bastard" temp/article.txt; then
               echo "found=true" >> $GITHUB_OUTPUT
               echo "⚠️ Profanity detected - manual review required"
               exit 1
             fi

         - name: Generate TTS
           env:
             OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
           run: |
             uv run main.py tts temp/article.txt \
               -o "temp/${{ github.event.inputs.episode_title }}.mp3"

         - name: Upload to Azure
           env:
             AZURE_STORAGE_CONNECTION_STRING: ${{ secrets.AZURE_STORAGE_CONNECTION_STRING }}
           run: |
             uv run main.py upload \
               "temp/${{ github.event.inputs.episode_title }}.mp3" \
               --name "${{ github.event.inputs.episode_title }}.m4a"

         - name: Update episodes.yaml
           run: |
             uv run python scripts/add_episode.py \
               "${{ github.event.inputs.episode_title }}" \
               "${{ github.event.inputs.blog_url }}" \
               "${{ github.event.inputs.author }}"

         - name: Regenerate RSS feed
           run: uv run main.py feed

         - name: Commit and push
           run: |
             git config user.name "github-actions[bot]"
             git config user.email "github-actions[bot]@users.noreply.github.com"
             git add episodes.yaml rss.xml
             git commit -m "Add episode: ${{ github.event.inputs.episode_title }}"
             git push
   ```

3. **Add secrets:**
   - Settings → Secrets and variables → Actions
   - Add: `OPENAI_API_KEY`
   - Add: `AZURE_STORAGE_CONNECTION_STRING`

4. **Test:**
   - Actions → Generate Podcast Episode → Run workflow

### Pros
- ✅ Low cost (~$0.10-$0.30 per episode)
- ✅ Fast execution
- ✅ Deterministic workflow
- ✅ No additional API dependencies

### Cons
- ❌ No intelligent error handling
- ❌ Profanity check fails workflow (requires manual fix)
- ❌ No adaptive scraping

---

## Cost Comparison

| Approach | Cost per Episode | API Keys Required |
|----------|------------------|-------------------|
| **Official Action** | $0.50 - $2.00 | ANTHROPIC_API_KEY, OPENAI_API_KEY, AZURE_STORAGE_CONNECTION_STRING |
| **Python Scripts** | $0.10 - $0.30 | OPENAI_API_KEY, AZURE_STORAGE_CONNECTION_STRING |

---

## Why Not Direct Claude CLI?

The `claude` CLI tool has **authentication challenges** in CI/CD:

- ❌ OAuth requires browser (not CI-friendly)
- ❌ NPM package is deprecated
- ❌ No official support for non-interactive API key auth
- ❌ [GitHub Issue #7100](https://github.com/anthropics/claude-code/issues/7100) closed as "not planned"

**Conclusion:** Don't use the direct CLI approach for CI/CD.

---

## My Recommendation

For **this project specifically**, I recommend:

### Start with: Python Scripts (Approach 2)
**Why:**
- ✅ Workflow is straightforward and deterministic
- ✅ Low cost (no Anthropic API)
- ✅ Existing Python codebase handles everything
- ✅ Easy to maintain

**Trade-off:** Manual profanity cleanup (workflow fails, you edit, re-run)

### Upgrade to: Official Action (Approach 1) if:
- You want intelligent profanity filtering
- You want adaptive error handling
- You want PR-based workflow (`@claude generate episode from <url>`)
- Cost is not a concern

---

## Implementation Timeline

### Immediate (Python Scripts):
- ✅ **Day 1:** Create `scripts/add_episode.py` helper
- ✅ **Day 1:** Create `.github/workflows/generate-episode.yml`
- ✅ **Day 1:** Add secrets to GitHub
- ✅ **Day 1:** Test with one episode

### Future (Official Action):
- ⏱️ **When needed:** Run `claude /install-github-app`
- ⏱️ **When needed:** Add `ANTHROPIC_API_KEY` secret
- ⏱️ **When needed:** Create `.github/workflows/claude-podcast.yml`

---

## Next Steps

1. **Choose your approach** (I suggest starting with Python Scripts)
2. **Follow setup steps** from the relevant section above
3. **Test with a single episode**
4. **Document any issues** or improvements needed

**Full research details:** See `/home/david/dev/ai-generated-podcast/docs/claude-code-ci-research.md`

---

## Questions?

- **"Can I use both approaches?"** Yes! Use Python for simple episodes, Claude for complex ones.
- **"How do I handle Medium articles?"** Both approaches would need manual text paste (Medium blocks scraping).
- **"What about profanity filtering?"** Official Action can handle it intelligently; Python approach fails workflow for manual review.
- **"Can I trigger from PR comments?"** Only with Official Action (`@claude` mentions).

---

**Status:** ✅ Research complete. Ready for implementation.
