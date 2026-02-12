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
# Simple setup with defaults (2/2/5) - ~75 credits
/botsee setup bts_live_YOUR_API_KEY https://example.com

# Or configure first, then setup
/botsee configure https://example.com 3 3 10  # Custom values
/botsee config-show                           # Review config
/botsee setup bts_live_YOUR_API_KEY           # Setup with saved config

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

### `/botsee setup <api_key> <domain>`
Non-interactive setup. Configure once, analyze many times.

**Usage:**
```bash
# Quick setup with defaults (2/2/5)
/botsee setup bts_live_YOUR_KEY https://example.com

# Or use saved config
/botsee configure https://example.com 3 3 10
/botsee setup bts_live_YOUR_KEY
```

**Process:**
1. Validates API key
2. Creates site for domain
3. Generates customer types (default: 2)
4. Generates personas per type (default: 2)
5. Generates questions per persona (default: 5)
6. Saves configuration to `~/.botsee/config.json`

**Cost:** ~75 credits with defaults (2/2/5)
- Site creation: 5 credits
- Customer types: 5 credits × count
- Personas: 5 credits × count
- Questions: 10 credits × persona_count

### `/botsee configure <domain> [types] [personas] [questions]`
Save configuration for later use with `/botsee setup`.

**Usage:**
```bash
# With defaults (2/2/5)
/botsee configure https://example.com

# With custom values
/botsee configure https://example.com 3 3 10
```

**Saves to:** `.context/botsee-config.json`

**Parameters:**
- `domain` - Website URL (required)
- `types` - Customer types, 1-3 (default: 2)
- `personas` - Personas per type, 1-3 (default: 2)
- `questions` - Questions per persona, 3-10 (default: 5)

### `/botsee config-show`
Display currently saved configuration from `.context/botsee-config.json`.

**Output:**
```
📋 BotSee Configuration
━━━━━━━━━━━━━━━━━━━━━
Domain: https://example.com
Customer Types: 2
Personas per Type: 2
Questions per Persona: 5

Ready to run: /botsee setup <api_key>
```

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

**Workspace Config** (`.context/botsee-config.json`):
Saved by `/botsee configure`, used by `/botsee setup`:
```json
{
  "domain": "https://example.com",
  "types": 2,
  "personas_per_type": 2,
  "questions_per_persona": 5
}
```

**User Config** (`~/.botsee/config.json`):
Saved by `/botsee setup` with secure permissions (600):
```json
{
  "api_key": "bts_live_...",
  "site_uuid": "..."
}
```

To reconfigure: `/botsee setup <api_key> <domain>` or `/botsee configure <domain>`

## Example Workflow

**Simple Setup (One Command):**
```bash
# Get API key from https://botsee.io/signup
/botsee setup bts_live_abc123... https://www.example.com

# Output:
✅ API key valid | Balance: 1000 credits

Using defaults: 2 types, 2 personas/type, 5 questions/persona

⏳ Creating site: https://www.example.com
✅ Site created: abc-def-123

⏳ Generating 2 customer type(s)...
📋 Customer Types:
  • Small Business Owners
  • Marketing Managers

⏳ Generating personas (2 per type)...
  ✓ Small Business Owners: 2 persona(s)
  ✓ Marketing Managers: 2 persona(s)
✅ Generated 4 persona(s)

⏳ Generating questions (5 per persona)...
✅ Generated 20 question(s)

✅ Setup complete!

Generated:
  • 2 customer type(s)
  • 4 persona(s)
  • 20 question(s)

💰 Remaining: 925 credits

Next: /botsee analyze
```

**Advanced Setup (Two Commands):**
```bash
# Configure with custom values
/botsee configure https://www.example.com 3 3 10

# Review configuration
/botsee config-show

# Run setup
/botsee setup bts_live_abc123...
```

**Run Analysis:**
```bash
/botsee analyze

# Output:
📊 Top Competitors:
  1. competitor.com - 45 mentions
  2. rival.com - 32 mentions

🔑 Top Keywords:
  • "email marketing" (12x)
  • "crm software" (8x)

💰 Remaining: 265 credits
```

**Generate Content:**
```bash
/botsee content

# Output:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Generated blog post content...]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Used: 15 credits

✅ Saved: botsee-20260211-143052.md
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
