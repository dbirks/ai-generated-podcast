# Deep Research Skills & Tools for AI-Generated Podcast (Tidbits Feature)

Research conducted: 2026-01-13

## Executive Summary

This document summarizes existing deep research skills, MCP servers, and tools in the Claude Code ecosystem that could be leveraged for implementing the tidbits/shorts feature (Issue #1). The goal is to automate the process of researching a topic and generating short-form podcast content.

---

## 1. Deep Research MCP Servers

### 1.1 Claude Deep Research (mcherukara)

**Repository:** https://github.com/mcherukara/Claude-Deep-Research

**Description:** A Python-based MCP server that enables comprehensive research capabilities for Claude through DuckDuckGo and Semantic Scholar integrations.

**Key Features:**
- Unified access to web and academic information
- Multi-stage research workflow (exploration → synthesis → follow-up → analysis)
- Automatic citation formatting (APA style)
- Structured prompts guide Claude through the research process

**Installation:**
```bash
git clone https://github.com/mcherukara/Claude-Deep-Research.git
cd Claude-Deep-Research
pip install mcp httpx beautifulsoup4

# For Claude Code specifically:
claude mcp add-json "search-scholar" '{"command":"python","args":["deep_research.py"]}'
```

**Usage Examples:**
- "Research the latest developments in quantum computing"
- "Research the history and cultural significance of origami using academic sources"

**Relevance to Tidbits:** HIGH - Could be used to gather comprehensive information on a user-provided topic, with proper citations for the podcast script.

**References:**
- [GitHub Repository](https://github.com/mcherukara/Claude-Deep-Research)
- [Installation Guide](https://skywork.ai/skypage/en/claude-deep-research-ai-engineer-guide/1980147193323573248)
- [PulseMCP Listing](https://www.pulsemcp.com/servers/claude-deep-research)

---

### 1.2 Enhanced Deep Web Research (qpd-v)

**Repository:** https://github.com/qpd-v/mcp-DEEPwebresearch

**Description:** Enhanced MCP server for deep web research with advanced capabilities.

**Key Features:**
- Multi-source web research
- Enhanced content extraction
- Research session tracking

**Installation:**
```bash
npm install mcp-deepwebresearch
```

**Relevance to Tidbits:** MEDIUM - Alternative to mcherukara's implementation with additional features.

**References:**
- [GitHub Repository](https://github.com/qpd-v/mcp-DEEPwebresearch)
- [NPM Package](https://www.npmjs.com/package/mcp-deepwebresearch)

---

### 1.3 Web Research MCP

**Repository:** https://github.com/mzxrai/mcp-webresearch

**Description:** Gives Claude real-time information from the web with integrated Google search and webpage content extraction.

**Key Features:**
- Google search integration
- Webpage content extraction
- Screenshot capture capabilities
- Research session tracking (visited pages, search queries)

**Relevance to Tidbits:** HIGH - Good for gathering diverse web sources for a topic.

**References:**
- [GitHub Repository](https://github.com/mzxrai/mcp-webresearch)
- [MCPMarket Listing](https://mcpmarket.com/server/web-research-1)

---

## 2. Web Search MCP Servers

### 2.1 Exa MCP Server

**Repository:** https://github.com/exa-labs/exa-mcp-server

**Description:** Official Exa AI MCP server for web search and crawling with advanced content gathering.

**Key Features:**
- **web_search_exa**: Real-time web searches with optimized results
- **deep_search_exa**: Deep web search with smart query expansion and high-quality summaries
- **company_research**: Comprehensive company research by crawling websites
- **crawling**: Extract content from specific URLs (articles, PDFs, web pages)
- **get_code_context_exa**: Search code snippets, examples, and documentation

**Installation:**
```bash
npm install exa-mcp-server
```

**Configuration:**
Default tools enabled: web_search_exa, get_code_context_exa
Other tools can be added via the tools parameter.

**Relevance to Tidbits:** HIGH - Excellent for gathering diverse, high-quality content from the web. Deep search with summaries could be particularly useful.

**References:**
- [GitHub Repository](https://github.com/exa-labs/exa-mcp-server)
- [Official Documentation](https://docs.exa.ai/reference/exa-mcp)
- [AI Engineer's Guide](https://skywork.ai/skypage/en/exa-web-search-mcp-server-guide/1977576254742786048)

---

### 2.2 Other Web Search Options

**Perplexity Ask MCP:**
- Delegates questions to Perplexity's backend
- Multi-step searches with synthesized answers
- Cited sources

**Brave Search MCP:**
- Privacy-focused search
- Free API key available
- Comprehensive search results

**Claude Search MCP:**
- Web search using Claude API
- Standardized interface for LLMs

**References:**
- [Search Tools Overview](https://claudefa.st/blog/tools/mcp-extensions/search-tools)
- [MCP Servers for Claude Code](https://intuitionlabs.ai/articles/mcp-servers-claude-code-internet-search)

---

## 3. Podcast Generation Tools

### 3.1 Podcastfy (NotebookLM Alternative)

**Repository:** https://github.com/souzatharsis/podcastfy

**Description:** Open-source Python package that transforms multi-modal content into engaging, multi-lingual audio conversations using GenAI.

**Key Features:**
- Input: websites, PDFs, images, YouTube videos, user-provided topics
- Multiple TTS providers: OpenAI, Google, ElevenLabs, Microsoft Edge
- Supports 100+ LLM models for transcript generation
- Multi-speaker conversations
- Multilingual support
- Transcript-only mode available
- Supports both shorts (2-5 min) and longform (30+ min) podcasts

**Installation:**
```bash
pip install podcastfy
```

**Usage Examples:**

Python API - Single URL:
```python
from podcastfy.client import generate_podcast

audio_file = generate_podcast(
    urls=["https://example.com/article"],
    tts_model="elevenlabs"
)
```

Python API - Multiple URLs:
```python
urls = [
    "https://github.com/souzatharsis/podcastfy/blob/main/README.md",
    "https://www.youtube.com/watch?v=jx2imp33glc"
]

audio_file_multi = generate_podcast(
    urls=urls,
    tts_model="elevenlabs"
)
```

Command Line:
```bash
python -m podcastfy.client --url <url1> --url <url2>
```

**TTS Model Options:**
- OpenAI TTS (default) - requires OPENAI_API_KEY
- ElevenLabs ('elevenlabs') - great customization
- Google Multispeaker TTS ('geminimulti') - best quality
- Microsoft Edge ('edge') - no API key required

**Custom Configuration:**
- Can pass custom config dictionary to generate_podcast()
- Parameters: word_count, conversation_style, podcast_name, creativity
- Can set output_language for target language

**Relevance to Tidbits:** VERY HIGH - This is almost exactly what we need! It can:
1. Take URLs or topics as input
2. Generate conversational transcripts using LLMs
3. Convert to audio using multiple TTS providers
4. Support short-form content (2-5 min)

**Comparison to Current Setup:**
- Current: Manual article scraping → profanity check → OpenAI TTS (cedar voice)
- Podcastfy: Automated content ingestion → transcript generation → multi-provider TTS

**Potential Integration:**
Could replace or augment the current workflow:
- Use Podcastfy for topic-based content (tidbits)
- Keep current workflow for URL-based articles
- Could use same TTS provider (OpenAI) for consistency

**References:**
- [GitHub Repository](https://github.com/souzatharsis/podcastfy)
- [Documentation](https://podcastfy.readthedocs.io/en/latest/podcastfy_demo.html)
- [PyPI Package](https://pypi.org/project/podcastfy/)
- [Usage Guide](https://github.com/souzatharsis/podcastfy/blob/main/usage/how-to.md)

---

### 3.2 Open-Notebook

**Repository:** https://github.com/lfnovo/open-notebook

**Description:** Open-source implementation of NotebookLM with more flexibility.

**Key Features:**
- MCP integration for Claude Desktop, VS Code, and other MCP clients
- Professional podcast generation
- Multi-speaker flexibility
- Full script control

**Relevance to Tidbits:** MEDIUM - More focused on notebook-style workflows, but has MCP integration.

**References:**
- [GitHub Repository](https://github.com/lfnovo/open-notebook)

---

### 3.3 NotebookLM MCP Server

**Repository:** https://github.com/roomi-fields/notebooklm-mcp

**Description:** MCP server for NotebookLM that lets AI agents research documentation directly.

**Key Features:**
- Grounded, citation-backed answers from Gemini
- Persistent auth
- Library management
- Cross-client sharing
- Zero hallucinations

**Relevance to Tidbits:** MEDIUM - More focused on documentation research, but could be useful for fact-checking.

**References:**
- [GitHub Repository](https://github.com/roomi-fields/notebooklm-mcp)

---

### 3.4 Claude Opus Podcast Generator

**Repository:** https://github.com/lawquarter/Claude-Podcast

**Description:** Flask-based web application that creates podcast scripts from user-provided content.

**Key Features:**
- Creates podcast scripts from content
- ElevenLabs API integration for TTS

**Relevance to Tidbits:** LOW - More focused on web UI, less suitable for CLI automation.

**References:**
- [GitHub Repository](https://github.com/lawquarter/Claude-Podcast)

---

## 4. Workflow Automation Frameworks

### 4.1 n8n Podcast Creation Workflow

**Description:** Workflow automation that uses GPT-5 and Claude Sonnet to turn a single topic into a complete podcast episode.

**Key Features:**
- Single topic input → complete podcast episode
- Integrates GPT-5 and Claude Sonnet
- ElevenLabs text-to-speech
- Ready-to-send audio file output

**Relevance to Tidbits:** MEDIUM - Shows how to chain LLMs with TTS, but requires n8n platform.

**References:**
- [n8n Workflow Template](https://n8n.io/workflows/10051-automate-podcast-creation-with-gpt-claude-and-eleven-labs-text-to-speech/)

---

### 4.2 Claude Code Agent Orchestration

**Multi-Agent Orchestration Platforms:**

**wshobson/agents:**
- 99 specialized AI agents
- 15 multi-agent workflow orchestrators
- 107 agent skills
- 71 development tools
- Repository: https://github.com/wshobson/agents

**Claude-Flow (ruvnet):**
- Leading agent orchestration platform
- Multi-agent swarms
- Autonomous workflows
- RAG integration
- Native Claude Code support via MCP
- Repository: https://github.com/ruvnet/claude-flow

**Claude Code Workflow (CCW):**
- JSON-driven multi-agent framework
- Intelligent CLI orchestration
- Repository: https://github.com/catlog22/Claude-Code-Workflow

**Best Practices:**
- Split work into phases: Research → Plan → Implement → Validate
- Clear context between phases
- Use sub-agents for parallel tasks

**Relevance to Tidbits:** MEDIUM - Useful for understanding how to orchestrate complex workflows, but may be overkill for the tidbits feature.

**References:**
- [Agent Orchestration Guide](https://sankalp.bearblog.dev/my-experience-with-claude-code-20-and-how-to-get-better-at-using-coding-agents/)
- [How to Use Claude Code Features](https://www.producttalk.org/how-to-use-claude-code-features/)

---

## 5. Deep Research Skills (Claude Code Native)

### 5.1 Deep Research Skill

**Description:** Built-in skill that uses OpenAI's Deep Research API (o4-mini-deep-research model).

**Key Features:**
- Interactive clarifying questions to enhance prompts
- Takes 10-20 minutes to complete
- Synchronous (blocking) operation
- Minimizes token usage during wait

**Installation:**
Available through MCPMarket and Claude Code skill system.

**Usage:**
Three approaches mentioned:
1. **MCP Server Approach** - Using Claude-Deep-Research
2. **Skills Approach** - Using OpenAI Deep Research API
3. **DIY Recursive Approach** - Cranot's deep-research (~20 lines of shell)

**Relevance to Tidbits:** HIGH - Could be used as a built-in skill for research phase.

**References:**
- [MCPMarket Listing](https://mcpmarket.com/tools/skills/deep-research)
- [Three Ways to Build Deep Research](https://paddo.dev/blog/three-ways-deep-research-claude/)
- [How to Use Guide](https://www.pulsemcp.com/use-cases/deep-research/claude-brave-google-playwright)

---

## 6. Recommended Implementation Strategy for Tidbits

Based on the research, here's a recommended approach for implementing the tidbits/shorts feature:

### Option A: Podcastfy Integration (Recommended)

**Pros:**
- Most comprehensive solution
- Already handles: research → transcript → TTS
- Supports multiple TTS providers (including OpenAI)
- Built for short-form content (2-5 min)
- Open-source Python package (easy integration)
- Active development

**Cons:**
- Different architecture than current workflow
- May need customization for profanity filtering
- Learning curve for new package

**Implementation Steps:**
1. Install Podcastfy: `pip install podcastfy`
2. Create new command: `uv run main.py tidbit "topic"`
3. Configure to use OpenAI TTS (cedar voice) for consistency
4. Add profanity filtering to generated transcripts
5. Upload to Azure and add to episodes.yaml

**Example Code:**
```python
from podcastfy.client import generate_podcast

def generate_tidbit(topic: str):
    # Generate podcast from topic
    audio_file = generate_podcast(
        urls=[],  # No URLs, just topic
        custom_config={
            'word_count': 500,  # Short form
            'conversation_style': 'informative',
            'podcast_name': 'AI Generated Podcast - Tidbits'
        },
        tts_model='openai'  # Use OpenAI TTS
    )

    # Apply profanity filtering
    # Upload to Azure
    # Add to episodes.yaml
```

---

### Option B: Custom Workflow with MCP Servers

**Pros:**
- More control over each step
- Can mix and match tools
- Follows existing architecture

**Cons:**
- More development work
- Need to handle orchestration
- Multiple tools to maintain

**Implementation Steps:**
1. Use Exa MCP or Claude Deep Research for topic research
2. Use Claude to generate conversational script
3. Use existing TTS pipeline (OpenAI cedar voice)
4. Apply profanity filtering
5. Upload to Azure and add to episodes.yaml

**Recommended MCP Servers:**
- **Research:** Exa MCP (deep_search_exa tool)
- **Content Generation:** Claude with custom prompts
- **TTS:** Current OpenAI setup

---

### Option C: Hybrid Approach

**Description:** Use Podcastfy for transcript generation, but keep current TTS pipeline.

**Pros:**
- Best of both worlds
- Consistent TTS voice (cedar)
- Podcastfy handles research and script generation
- Existing profanity filter and upload workflow

**Cons:**
- Need to extract transcript from Podcastfy
- Some redundancy

**Implementation Steps:**
1. Use Podcastfy with `--transcript-only` flag
2. Apply profanity filtering to transcript
3. Use existing TTS pipeline (OpenAI cedar)
4. Upload to Azure and add to episodes.yaml

---

## 7. Comparison Matrix

| Tool/Approach | Research | Script Gen | TTS | Integration Effort | Maintenance |
|---------------|----------|------------|-----|-------------------|-------------|
| **Podcastfy** | ✅ Built-in | ✅ Built-in | ✅ Multiple providers | Low | Low |
| **Claude Deep Research + Custom** | ✅ Excellent | 🔧 DIY | 🔧 DIY | Medium | Medium |
| **Exa MCP + Custom** | ✅ Excellent | 🔧 DIY | 🔧 DIY | Medium | Medium |
| **n8n Workflow** | ✅ Built-in | ✅ Built-in | ✅ Built-in | High (platform) | Low |
| **Current Workflow Extended** | ❌ Manual | ❌ Manual | ✅ Working | Low | Low |

Legend:
- ✅ = Fully supported
- 🔧 = Requires custom development
- ❌ = Not supported

---

## 8. Additional Considerations

### Profanity Filtering
- Podcastfy doesn't have built-in profanity filtering
- Need to apply current profanity rules to generated transcripts
- Could be done post-generation before TTS

### Episode Metadata
- Need to track that tidbits are AI-researched (not from a specific blog URL)
- Might add `source_type: "research"` to episodes.yaml
- Should include research sources/citations in description

### Voice Consistency
- Current episodes use OpenAI cedar voice
- Podcastfy supports OpenAI TTS, so can maintain consistency
- Or could use Podcastfy's multi-speaker for variety

### Quality Control
- Research-based content may need more fact-checking
- Could add a review step before publishing
- Consider adding citations/sources to episode descriptions

### Cost Considerations
- Exa MCP: Requires API key (paid)
- Podcastfy: Uses various APIs (most require keys)
- OpenAI Deep Research: Uses o4-mini-deep-research (costs tokens)
- Could start with free tools (DuckDuckGo, Edge TTS)

---

## 9. Next Steps

1. **Prototype with Podcastfy:**
   - Install package and test basic functionality
   - Generate a sample tidbit on a test topic
   - Compare quality to current episodes

2. **Evaluate Quality:**
   - Test research depth and accuracy
   - Check audio quality with different TTS providers
   - Assess whether it meets podcast standards

3. **Plan Integration:**
   - Decide on Option A, B, or C
   - Design CLI interface: `uv run main.py tidbit "topic"`
   - Plan episode metadata schema changes

4. **Implement MVP:**
   - Start with simplest working version
   - Add profanity filtering
   - Integrate with Azure upload
   - Update episodes.yaml format

5. **Iterate:**
   - Gather feedback on generated content
   - Refine prompts and configuration
   - Add quality controls as needed

---

## 10. Useful Resources

### Documentation
- [Claude Code Agent Skills](https://code.claude.com/docs/en/skills)
- [MCP Servers Guide](https://claude.com/blog/extending-claude-capabilities-with-skills-mcp-servers)
- [Podcastfy Documentation](https://podcastfy.readthedocs.io/)

### Tool Catalogs
- [Awesome MCP Servers](https://mcpservers.org/)
- [Awesome Claude Skills](https://github.com/ComposioHQ/awesome-claude-skills)
- [MCPMarket](https://mcpmarket.com/)
- [Claude Plugins Directory](https://claude-plugins.dev/)

### Tutorials
- [How to Use Claude Code](https://www.producttalk.org/how-to-use-claude-code-features/)
- [Three Ways to Build Deep Research](https://paddo.dev/blog/three-ways-deep-research-claude/)
- [MCP Servers for Claude Code](https://mcpcat.io/guides/best-mcp-servers-for-claude-code/)

---

## Sources

### Deep Research
- [Claude Deep Research GitHub](https://github.com/mcherukara/Claude-Deep-Research)
- [Claude Deep Research Guide](https://skywork.ai/skypage/en/claude-deep-research-ai-engineer-guide/1980147193323573248)
- [PulseMCP - Claude Deep Research](https://www.pulsemcp.com/servers/claude-deep-research)
- [MCPMarket - Deep Research](https://mcpmarket.com/tools/skills/deep-research)
- [Three Ways to Build Deep Research with Claude](https://paddo.dev/blog/three-ways-deep-research-claude/)

### Web Search MCP Servers
- [Integrating MCP Servers for Web Search](https://intuitionlabs.ai/articles/mcp-servers-claude-code-internet-search)
- [Web Research MCP GitHub](https://github.com/mzxrai/mcp-webresearch)
- [Exa MCP Server GitHub](https://github.com/exa-labs/exa-mcp-server)
- [Exa Official Documentation](https://docs.exa.ai/reference/exa-mcp)
- [Exa MCP Server Guide](https://skywork.ai/skypage/en/exa-web-search-mcp-server-guide/1977576254742786048)
- [Search Tools - Claude Fast](https://claudefa.st/blog/tools/mcp-extensions/search-tools)

### Podcast Generation
- [Podcastfy GitHub](https://github.com/souzatharsis/podcastfy)
- [Podcastfy Documentation](https://podcastfy.readthedocs.io/en/latest/podcastfy_demo.html)
- [Podcastfy PyPI](https://pypi.org/project/podcastfy/)
- [Podcastfy Usage Guide](https://github.com/souzatharsis/podcastfy/blob/main/usage/how-to.md)
- [Open-Notebook GitHub](https://github.com/lfnovo/open-notebook)
- [NotebookLM MCP Server](https://github.com/roomi-fields/notebooklm-mcp)
- [Claude Podcast Generator GitHub](https://github.com/lawquarter/Claude-Podcast)

### Workflow Automation
- [n8n Podcast Creation Workflow](https://n8n.io/workflows/10051-automate-podcast-creation-with-gpt-claude-and-eleven-labs-text-to-speech/)
- [wshobson/agents GitHub](https://github.com/wshobson/agents)
- [Claude-Flow GitHub](https://github.com/ruvnet/claude-flow)
- [Claude Code Workflow GitHub](https://github.com/catlog22/Claude-Code-Workflow)
- [Guide to Claude Code 2.0](https://sankalp.bearblog.dev/my-experience-with-claude-code-20-and-how-to-get-better-at-using-coding-agents/)
- [How to Use Claude Code Features](https://www.producttalk.org/how-to-use-claude-code-features/)

### Additional Resources
- [Claude Code Agent Skills](https://code.claude.com/docs/en/skills)
- [Extending Claude with Skills and MCP](https://claude.com/blog/extending-claude-capabilities-with-skills-mcp-servers)
- [Best MCP Servers for Claude Code](https://mcpcat.io/guides/best-mcp-servers-for-claude-code/)
- [Awesome Claude Skills](https://github.com/ComposioHQ/awesome-claude-skills)
- [MCPMarket](https://mcpmarket.com/)
- [MCP Servers Directory](https://mcpservers.org/)

---

**Research Date:** 2026-01-13
**Researcher:** Claude Code (Sonnet 4.5)
**Purpose:** Evaluating tools for tidbits/shorts feature (Issue #1)
