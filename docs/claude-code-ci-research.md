# Claude Code in GitHub Actions - Research Summary

**Issue Reference:** #4
**Research Date:** January 13, 2026
**Status:** FEASIBLE - Multiple integration paths available

---

## Executive Summary

Claude Code **CAN** run in GitHub Actions through multiple approaches:

1. **Official GitHub Action** (Recommended) - Use `anthropics/claude-code-action@v1`
2. **Claude Agent SDK** - Programmatic integration with TypeScript/JavaScript
3. **Direct CLI** (Limited) - Headless mode with authentication challenges

**Recommendation for this project:** Use Option #1 (Official GitHub Action) or Option #3 (Direct Python orchestration without Claude Code CLI).

---

## Option 1: Official Claude Code GitHub Action (RECOMMENDED)

### Overview
Anthropic provides an official GitHub Action that wraps Claude Code functionality for CI/CD.

### Installation

**Quick Setup (Easiest):**
```bash
claude /install-github-app
```

This guided CLI setup will:
1. Configure the GitHub App
2. Add required secrets to your repository
3. Create a PR with the workflow file

**Manual Setup:**
1. Install the [Claude GitHub App](https://github.com/apps/claude)
2. Add `ANTHROPIC_API_KEY` to repository secrets (Settings → Secrets and variables → Actions)
3. Add workflow file to `.github/workflows/claude.yml`

### Example Workflow

```yaml
name: Claude Code

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]
  pull_request_review:
    types: [submitted]

jobs:
  claude:
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review' && contains(github.event.review.body, '@claude')) ||
      (github.event_name == 'issues' && (contains(github.event.issue.body, '@claude') || contains(github.event.issue.title, '@claude')))
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write
      id-token: write
      actions: read
    steps:
      - name: Checkout repository
        uses: actions/checkout@v5
        with:
          fetch-depth: 1

      - name: Run Claude Code
        id: claude
        uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

          # Optional customizations
          # trigger_phrase: "/claude"
          # claude_args: |
          #   --model claude-opus-4-1-20250805
          #   --max-turns 10
          #   --allowedTools "Bash(npm install),Bash(npm run build),Bash(npm run test:*)"
```

### Automation Workflows (Non-Interactive)

**Path-Specific Automation:**
```yaml
on:
  pull_request:
    paths:
      - "src/api/**/*.ts"

steps:
  - uses: anthropics/claude-code-action@v1
    with:
      prompt: |
        Update the API documentation in README.md to reflect
        the changes made to the API endpoints in this PR.
      anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

**Scheduled Automation:**
```yaml
on:
  schedule:
    - cron: '0 2 * * 1'  # Monday 2am

steps:
  - uses: anthropics/claude-code-action@v1
    with:
      prompt: |
        Review dependency updates and create a PR
        if security patches are available.
      anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Authentication Methods

The action supports multiple authentication methods:
1. **Anthropic Direct API** - `ANTHROPIC_API_KEY` (easiest)
2. **Amazon Bedrock** - AWS credentials
3. **Google Vertex AI** - GCP credentials
4. **Microsoft Foundry** - Azure credentials

### Permissions Required

```yaml
permissions:
  contents: write        # Read/write repo files
  pull-requests: write   # Comment on PRs
  issues: write          # Comment on issues
  id-token: write        # OIDC token for cloud providers
  actions: read          # Read CI results
```

### Pros
- ✅ Official support from Anthropic
- ✅ No authentication complexity
- ✅ Works with `@claude` mentions in PRs/issues
- ✅ Supports automated workflows with `prompt` parameter
- ✅ Full Claude Code capabilities

### Cons
- ❌ Requires ANTHROPIC_API_KEY secret (costs money)
- ❌ Each workflow run consumes API tokens
- ❌ May be overkill for simple scripted tasks

### Resources
- [Official Docs](https://code.claude.com/docs/en/github-actions)
- [GitHub Action Repo](https://github.com/anthropics/claude-code-action)
- [Example Workflows](https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml)
- [Setup Guide](https://github.com/anthropics/claude-code-action/blob/main/docs/setup.md)

---

## Option 2: Claude Agent SDK (Programmatic)

### Overview
The `@anthropic-ai/claude-agent-sdk` npm package allows you to build custom automation with Claude Code's capabilities programmatically.

### Installation

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20'

- name: Install Claude Agent SDK
  run: npm install @anthropic-ai/claude-agent-sdk
```

### Example Usage

```javascript
import { ClaudeAgent } from '@anthropic-ai/claude-agent-sdk';

const agent = new ClaudeAgent({
  apiKey: process.env.ANTHROPIC_API_KEY,
  model: 'claude-opus-4-5-20251101'
});

// Read files, execute commands, etc.
const result = await agent.run({
  prompt: "Analyze the changes in this PR",
  tools: ['read_file', 'bash', 'grep']
});
```

### Pros
- ✅ Full programmatic control
- ✅ Can integrate with custom Node.js/TypeScript workflows
- ✅ Build custom tools and workflows

### Cons
- ❌ More complex setup
- ❌ Requires writing custom integration code
- ❌ Less documentation than official action

### Resources
- [npm Package](https://www.npmjs.com/package/@anthropic-ai/claude-agent-sdk)
- [CI/CD Example](https://jpcaparas.medium.com/claude-agent-sdk-in-ci-cd-a-safe-read-only-pr-intelligence-workflow-cb996cf1745d)

---

## Option 3: Direct Claude CLI (LIMITED - NOT RECOMMENDED)

### Installation Methods

**Native Binary (Recommended for 2026):**
```bash
# Linux/macOS
curl -fsSL https://claude.ai/install.sh | bash

# Windows PowerShell
irm https://claude.ai/install.ps1 | iex
```

**NPM (DEPRECATED):**
```bash
npm install -g @anthropic-ai/claude-code  # DO NOT USE - Deprecated
```

> **Note:** NPM installation is deprecated as of 2026. The native binary method is now the standard.

### Headless Mode

Claude CLI supports a `-p` (or `--print`) flag for non-interactive execution:

```bash
# Basic usage
claude -p "Summarize the changes in this commit"

# With allowed tools
claude -p "Review staged changes and create commit" \
  --allowedTools "Bash(git diff:*),Bash(git log:*),Bash(git commit:*)"

# JSON output for parsing
claude -p "Extract function names from auth.py" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array"}}}' \
  | jq '.structured_output'

# With permission mode
claude -p "Fix linting errors" --permission-mode acceptAll
```

### GitHub Actions Integration Example

```yaml
- name: Install Claude Code
  run: |
    curl -fsSL https://claude.ai/install.sh | bash
    echo "$HOME/.local/bin" >> $GITHUB_PATH

- name: Run Claude Headless
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    claude -p "Analyze code quality in src/" \
      --output-format json \
      --allowedTools "Bash(grep),Bash(find)" \
      > analysis.json
```

### Authentication Challenges ⚠️

**CRITICAL LIMITATION:** Claude CLI authentication is problematic in CI/CD:

1. **OAuth Flow Requires Browser** - The standard `claude /login` command opens a browser-based OAuth flow, which doesn't work in headless CI environments.

2. **Environment Variable Support** - The CLI can use `ANTHROPIC_API_KEY`, but this is not officially documented or fully supported.

3. **Credential File Transfer** - You can transfer `~/.config/claude-code/auth.json` from a local authenticated session, but this is a security risk and not recommended.

4. **Issue Status** - [GitHub Issue #7100](https://github.com/anthropics/claude-code/issues/7100) requesting proper CI/CD authentication was **closed as not planned** on January 7, 2026.

### Workarounds (Not Recommended)

**Method 1: Credential File Transfer (Security Risk)**
```yaml
# DO NOT DO THIS - Security risk
- name: Setup Claude Auth
  run: |
    mkdir -p ~/.config/claude-code
    echo "${{ secrets.CLAUDE_AUTH_JSON }}" > ~/.config/claude-code/auth.json
```

**Method 2: Environment Variable (Unofficial)**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
claude -p "Run task"
```

### Pros
- ✅ Direct CLI control
- ✅ Headless mode with `-p` flag
- ✅ JSON output support

### Cons
- ❌ Authentication is problematic in CI
- ❌ NPM package is deprecated
- ❌ Non-interactive API key auth not officially supported
- ❌ OAuth flow requires browser
- ❌ No official CI/CD support

### Resources
- [Headless Mode Docs](https://code.claude.com/docs/en/headless)
- [Installation Guide](https://code.claude.com/docs/en/setup)
- [CI/CD Auth Issue](https://github.com/anthropics/claude-code/issues/7100) (closed)
- [Non-Interactive Auth Issue](https://github.com/anthropics/claude-code/issues/551)

---

## Option 4: Direct Python Orchestration (RECOMMENDED FOR THIS PROJECT)

### Overview
Since this project already has Python scripts (`main.py`, `scraper.py`, `tts.py`, etc.), we can orchestrate the podcast workflow directly without Claude Code.

### Workflow Example

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

jobs:
  generate-episode:
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
        run: |
          uv run main.py scrape "${{ github.event.inputs.blog_url }}"

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
          # Add episode metadata to episodes.yaml
          # This step would need a Python script to append to YAML
          echo "Manual step: Add episode to episodes.yaml"

      - name: Regenerate feed
        run: uv run main.py feed

      - name: Commit and push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add episodes.yaml rss.xml
          git commit -m "Add episode: ${{ github.event.inputs.episode_title }}"
          git push
```

### Pros
- ✅ No Claude API costs
- ✅ Uses existing Python codebase
- ✅ Full control over workflow
- ✅ No authentication complexity
- ✅ Faster execution (no LLM overhead)

### Cons
- ❌ No intelligent error handling
- ❌ No automatic profanity filtering (would need to be scripted)
- ❌ Manual YAML editing required

---

## Comparison Table

| Feature | Official Action | Agent SDK | Direct CLI | Python Scripts |
|---------|----------------|-----------|------------|----------------|
| **Ease of Setup** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Authentication** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| **CI/CD Ready** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Cost** | 💰💰💰 | 💰💰💰 | 💰💰💰 | 💰 (OpenAI only) |
| **Flexibility** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Intelligence** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **Maintenance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |

---

## Required Environment Variables

### For Official Action / Agent SDK / CLI

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key (starts with `sk-ant-`) |
| `OPENAI_API_KEY` | No | For TTS generation |
| `AZURE_STORAGE_CONNECTION_STRING` | No | For audio upload |

### For Python Scripts Only

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for TTS |
| `AZURE_STORAGE_CONNECTION_STRING` | Yes | Azure Blob Storage connection |

---

## Recommendation for This Project

### Short-term: Python Scripts (Option 4)
For the immediate needs of this project, **direct Python orchestration** is recommended because:

1. ✅ Existing Python codebase already handles all steps
2. ✅ No additional API costs beyond OpenAI TTS
3. ✅ Workflow is straightforward and deterministic
4. ✅ No authentication complexity

### Long-term: Official Action (Option 1)
If you want **intelligent automation** (profanity filtering, error handling, adaptive scraping), consider the **Official Claude Code Action**:

1. ✅ Best for interactive workflows (`@claude` mentions)
2. ✅ Best for code reviews and PR automation
3. ✅ Intelligent error handling
4. ❌ Higher cost (Anthropic API)

### Not Recommended: Direct CLI (Option 3)
The direct CLI approach has too many limitations for CI/CD:
- ❌ Authentication not CI-friendly
- ❌ NPM package deprecated
- ❌ No official support for non-interactive use

---

## Implementation Steps (Option 1: Official Action)

If you choose the Official Action route:

1. **Setup GitHub App:**
   ```bash
   claude /install-github-app
   ```

2. **Add API Key Secret:**
   - Go to repository Settings → Secrets and variables → Actions
   - Add `ANTHROPIC_API_KEY` with your Anthropic API key

3. **Create Workflow File:**
   - Copy the example workflow from this document to `.github/workflows/claude-podcast.yml`

4. **Test with PR Comment:**
   - Open a PR and comment: `@claude Generate a podcast episode from https://example.com/post`

5. **Automate with Prompt:**
   ```yaml
   on:
     workflow_dispatch:
       inputs:
         blog_url:
           required: true

   steps:
     - uses: anthropics/claude-code-action@v1
       with:
         prompt: |
           Generate a podcast episode from ${{ inputs.blog_url }}:
           1. Scrape the article
           2. Check for profanity and clean if needed
           3. Generate TTS audio
           4. Upload to Azure
           5. Update episodes.yaml
           6. Regenerate RSS feed
         anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
   ```

---

## Implementation Steps (Option 4: Python Scripts)

If you choose direct Python orchestration:

1. **Create Workflow File:**
   - Add `.github/workflows/generate-episode.yml` (see Option 4 example)

2. **Add Required Secrets:**
   - `OPENAI_API_KEY`
   - `AZURE_STORAGE_CONNECTION_STRING`
   - `GITHUB_TOKEN` (automatically provided)

3. **Create Helper Script:**
   ```python
   # scripts/add_episode.py
   import yaml
   import sys
   from datetime import datetime

   def add_episode(title, blog_url, author, description):
       with open('episodes.yaml', 'r') as f:
           episodes = yaml.safe_load(f)

       episodes.append({
           'title': title,
           'published_date': datetime.now().isoformat(),
           'blog_url': blog_url,
           'was_edited': False,
           'author': author,
           'article_date': datetime.now().date().isoformat(),
           'tech': 'OpenAI TTS (cedar)',
           'description': description
       })

       with open('episodes.yaml', 'w') as f:
           yaml.dump(episodes, f)
   ```

4. **Test Manually:**
   - Go to Actions → Generate Podcast Episode → Run workflow
   - Enter blog URL and episode title
   - Verify output

---

## Cost Analysis

### Official Action (Option 1)
- **Anthropic API:** ~$15-45/1M tokens (depends on model)
- **OpenAI TTS:** $15/1M chars
- **Estimated per episode:** $0.50 - $2.00 (depending on article length and complexity)

### Python Scripts (Option 4)
- **OpenAI TTS:** $15/1M chars
- **Estimated per episode:** $0.10 - $0.30 (TTS only)

---

## Security Considerations

### API Keys
- ✅ Always use GitHub Secrets (`${{ secrets.* }}`)
- ❌ Never hardcode API keys in workflows
- ✅ Regularly rotate keys
- ✅ Use fine-grained permissions where possible

### Permissions
```yaml
permissions:
  contents: write       # Required to commit changes
  pull-requests: write  # Required for PR comments
  issues: write         # Required for issue comments
```

### Best Practices
1. Use `fetch-depth: 1` for shallow clones (faster)
2. Set up branch protection rules
3. Require PR reviews for workflow changes
4. Use environment secrets for production

---

## Conclusion

**Claude Code CAN run in GitHub Actions**, primarily through the official `anthropics/claude-code-action@v1`. However, for this specific project:

- **Best for simple automation:** Use **Option 4 (Python Scripts)**
- **Best for intelligent automation:** Use **Option 1 (Official Action)**
- **Avoid:** Option 3 (Direct CLI) - authentication issues

The decision depends on your priorities:
- **Cost-conscious + deterministic workflow:** Python Scripts
- **Intelligent + adaptive + error-handling:** Official Action

---

## Sources

- [Claude Code GitHub Actions - Official Docs](https://code.claude.com/docs/en/github-actions)
- [anthropics/claude-code-action - GitHub](https://github.com/anthropics/claude-code-action)
- [Example Workflow YAML](https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml)
- [Setup Guide](https://github.com/anthropics/claude-code-action/blob/main/docs/setup.md)
- [Headless Mode Documentation](https://code.claude.com/docs/en/headless)
- [CI/CD Auth Issue #7100](https://github.com/anthropics/claude-code/issues/7100)
- [Non-Interactive Auth Issue #551](https://github.com/anthropics/claude-code/issues/551)
- [Claude Agent SDK - npm](https://www.npmjs.com/package/@anthropic-ai/claude-agent-sdk)
- [Claude Code Installation Guide](https://code.claude.com/docs/en/setup)
- [Integrating Claude Code with GitHub Actions](https://stevekinney.com/courses/ai-development/integrating-with-github-actions)
- [How to Use Claude Code with GitHub Actions](https://apidog.com/blog/claude-code-github-actions/)
- [Claude Agent SDK in CI/CD](https://jpcaparas.medium.com/claude-agent-sdk-in-ci-cd-a-safe-read-only-pr-intelligence-workflow-cb996cf1745d)
- [Faster Claude Code agents in GitHub Actions](https://depot.dev/blog/claude-code-in-github-actions)
