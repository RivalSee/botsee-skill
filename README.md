# BotSee Skill for Claude Code

> Get AI-powered competitive intelligence in Claude Code

BotSee analyzes any website to identify competitors, keywords, and content opportunities using multiple AI models (OpenAI, Claude, Perplexity).

## Installation

1. Copy `SKILL.md` to your Claude Code skills directory:
```bash
# macOS/Linux
cp SKILL.md ~/.claude/skills/botsee.md
```

2. Restart Claude Code or reload skills

## Requirements

- Claude Code
- BotSee account: https://botsee.io/signup
- Tools: `curl`, `jq` (pre-installed on macOS/Linux)

## Quick Start

```bash
# One-time interactive setup (~75 credits)
/botsee setup
# - Enter API key from https://botsee.io/signup
# - Enter website URL
# - Generate & refine customer types, personas, questions

# Run analysis on pre-configured site (~660 credits)
/botsee analyze

# Generate blog post from analysis (15 credits)
/botsee content

# Check status and balance
/botsee
```

## Commands

### `/botsee`
Shows current status, balance, and available commands.

```
🤖 BotSee
━━━━━━━━━━━━━━━
💰 Credits: 1,250
🌐 Sites: 1
🔑 Key: bts_live_abc123...
```

### `/botsee setup`
Interactive setup with feedback loops. Configure once, analyze many times.

**Flow:**
1. Enter API key
2. Enter website URL
3. Generate customer types (1-3 recommended: 2)
   - Review generated types
   - Press Enter to continue or 'r' to regenerate
4. Generate personas (1-3 per type, recommend 2)
   - Review each persona
   - Provide feedback or regenerate
5. Generate questions (3-10 per persona, recommend 5)
   - Review questions
   - Refine as needed

**Cost:** ~75 credits (one-time)
- Site creation: 5 credits
- Customer types: 5 credits × count
- Personas: 5 credits × count
- Questions: 10 credits × persona_count

### `/botsee analyze`
Runs full competitive analysis on your pre-configured site. No prompts needed.

**Output:**
```
📊 Top Competitors:
  1. competitor.com - 45 mentions
  2. rival.com - 32 mentions
  3. alternative.com - 28 mentions

🔑 Top Keywords:
  • "best email marketing" (12x)
  • "affordable crm software" (8x)
  • "customer engagement tools" (7x)

💰 Remaining: 590 credits
```

**Cost:** ~660 credits per run (varies by question count and models)

### `/botsee content`
Generates blog post based on latest analysis.

**Cost:** 15 credits

## Configuration

Configuration stored in `~/.botsee/config.json` with secure permissions (600):
```json
{
  "api_key": "bts_live_...",
  "site_uuid": "..."
}
```

To reconfigure: `/botsee setup`

## Example Workflow

```bash
# Setup once
/botsee setup
Enter API key: bts_live_abc123...
Website URL to analyze: https://www.example.com
How many customer types? (1-3, recommend 2): 2
⏳ Generating 2 customer type(s)...

📋 Generated Customer Types:
  - Small Business Owners
  - Marketing Managers

Comments or changes? (Enter to continue, 'r' to regenerate):
# ... continue through personas and questions ...

✅ Setup complete!

# Run analysis multiple times
/botsee analyze
# ... results ...

# Generate content
/botsee content
# ... blog post ...
```

## Troubleshooting

**"Invalid API key"**
- Get a new key at https://botsee.io/signup
- Run `/botsee setup` to reconfigure

**"Insufficient credits"**
- Add credits at https://botsee.io/billing
- Current balance shown in error message

**"Network timeout"**
- Check internet connection
- API calls timeout after 30 seconds

**Ctrl+C during analysis**
- Analysis continues in background
- UUID shown for reference
- Re-run `/botsee analyze` to start new analysis

## Credits & Costs

- **Setup (one-time):** ~75 credits
  - Site creation: 5
  - 2 customer types: 10
  - 4 personas: 20
  - 20 questions: 40

- **Analysis (per run):** ~660 credits
  - Varies by question count and models
  - 20 questions × 3 models × ~11 credits average

- **Content (per post):** 15 credits

**Total for first complete workflow:** ~750 credits

## License

MIT License - see LICENSE file

## Support

- Documentation: https://botsee.io/docs
- Issues: https://github.com/rivalsee/botsee-skill/issues
