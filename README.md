# BotSee Skill for Claude Code

> Get AI-powered competitive intelligence in Claude Code

BotSee analyzes any website to identify competitors, keywords, and content opportunities using multiple AI models (OpenAI, Claude, Perplexity, Gemini, Grok).

## Installation

Copy the entire skill directory to Claude Code:
```bash
# macOS/Linux
cp -r . ~/.claude/skills/botsee
```

Restart Claude Code or reload skills.

## Requirements

- Claude Code
- Python 3 (pre-installed on macOS)

## Quick Start

```bash
# New user — creates account, shows signup URL
/botsee setup https://example.com

# Existing user — use your API key
/botsee setup https://example.com --api-key bts_live_YOUR_KEY

# Run analysis (~660 credits)
/botsee analyze

# Generate blog post (15 credits)
/botsee content

# Check status and balance
/botsee
```

## Commands

### Workflow Commands

#### `/botsee`
Shows current status, balance, and available commands.

```
🤖 BotSee
━━━━━━━━━━━━━━━
💰 Credits: 1,250
🌐 Sites: 1
🔑 Key: bts_live_abc123...
```

#### `/botsee setup <domain>`
Setup BotSee for a domain. Handles account creation for new users.

**New user (no API key):**
```bash
/botsee setup https://example.com
```

The setup command will:
1. Create a signup token via the BotSee API
2. Display a signup URL for you to complete registration
3. Wait for signup completion
4. Create site, generate customer types, personas, and questions
5. Save credentials to `~/.botsee/config.json`

**Existing user (has API key):**
```bash
/botsee setup https://example.com --api-key bts_live_YOUR_KEY
```

Skips signup, validates key, then creates site and generates types/personas/questions.

**Cost:** ~75 credits with defaults (2/2/5)
- Site creation: 5 credits
- Customer types: 5 credits per type
- Personas: 5 credits per persona
- Questions: 10 credits flat per persona

#### `/botsee configure <domain>`
Save custom configuration for later use with setup.

```bash
# With defaults (2/2/5)
/botsee configure https://example.com

# With custom values
/botsee configure https://example.com --types 3 --personas 3 --questions 10
```

Saves to `.context/botsee-config.json`. Setup reads this config automatically.

#### `/botsee config-show`
Display saved workspace configuration.

```
📋 BotSee Configuration
━━━━━━━━━━━━━━━━━━━━━
Domain: https://example.com
Customer Types: 2
Personas per Type: 2
Questions per Persona: 5

Ready to run: /botsee setup <domain>
```

#### `/botsee analyze`
Runs competitive analysis. Starts the analysis, polls until complete, then displays competitors, keywords, and cited sources.

```
📊 Top Competitors:
  1. competitor.com - 45 mentions
  2. rival.com - 32 mentions

🔑 Top Keywords:
  • "best email marketing" (12x)
  • "affordable crm software" (8x)

📄 Top Sources:
  • techcrunch.com (5x) ⭐
  • g2.com (3x)

💰 Remaining: 265 credits
```

**Cost:** ~660 credits per run (varies by question count and models)

#### `/botsee content`
Generates blog post from latest analysis. Auto-saves to `botsee-YYYYMMDD-HHMMSS.md`.

**Cost:** 15 credits

---

### Sites Management

#### `/botsee list-sites`
List all sites in your account.

```bash
/botsee list-sites
```

#### `/botsee get-site [uuid]`
View details of a specific site. If uuid is omitted, shows the current site from config.

```bash
/botsee get-site
/botsee get-site abc-def-123
```

#### `/botsee create-site <domain>`
Create a new site. Saves the new site UUID to config.

```bash
/botsee create-site https://example.com
```

**Cost:** 5 credits (auto-generates product_name and value_proposition)

#### `/botsee archive-site [uuid]`
Archive a site. If uuid is omitted, archives the current site.

```bash
/botsee archive-site
/botsee archive-site abc-def-123
```

---

### Customer Types Management

#### `/botsee list-types`
List all customer types for the current site.

```bash
/botsee list-types
```

#### `/botsee get-type <uuid>`
View details of a specific customer type.

```bash
/botsee get-type type-uuid-123
```

#### `/botsee create-type <name> [description]`
Create a new customer type manually.

```bash
/botsee create-type "Enterprise Buyers" "Large companies seeking solutions"
```

**Cost:** 5 credits

#### `/botsee generate-types [count]`
Generate customer types using AI. Defaults to 2.

```bash
/botsee generate-types
/botsee generate-types 3
```

**Cost:** 5 credits per type

#### `/botsee update-type <uuid> [--name NAME] [--description DESC]`
Update a customer type.

```bash
/botsee update-type type-uuid-123 --name "Enterprise Decision Makers"
/botsee update-type type-uuid-123 --description "C-level executives"
```

#### `/botsee archive-type <uuid>`
Archive a customer type.

```bash
/botsee archive-type type-uuid-123
```

---

### Personas Management

#### `/botsee list-personas [type_uuid]`
List personas. Show all or filter by customer type.

```bash
/botsee list-personas
/botsee list-personas type-uuid-123
```

#### `/botsee get-persona <uuid>`
View details of a specific persona.

```bash
/botsee get-persona persona-uuid-456
```

#### `/botsee create-persona <type_uuid> <name> [description]`
Create a new persona manually.

```bash
/botsee create-persona type-uuid-123 "Sarah Chen" "VP of Marketing at mid-sized SaaS"
```

**Cost:** 5 credits

#### `/botsee generate-personas <type_uuid> [count]`
Generate personas for a customer type using AI. Defaults to 2.

```bash
/botsee generate-personas type-uuid-123
/botsee generate-personas type-uuid-123 3
```

**Cost:** 5 credits per persona

#### `/botsee update-persona <uuid> [--name NAME] [--description DESC]`
Update a persona.

```bash
/botsee update-persona persona-uuid-456 --name "Sarah Chen (CMO)"
/botsee update-persona persona-uuid-456 --description "Chief Marketing Officer"
```

#### `/botsee archive-persona <uuid>`
Archive a persona.

```bash
/botsee archive-persona persona-uuid-456
```

---

### Questions Management

#### `/botsee list-questions [persona_uuid]`
List questions. Show all or filter by persona.

```bash
/botsee list-questions
/botsee list-questions persona-uuid-456
```

#### `/botsee get-question <uuid>`
View details of a specific question.

```bash
/botsee get-question question-uuid-789
```

#### `/botsee create-question <persona_uuid> <question_text>`
Create a new question manually.

```bash
/botsee create-question persona-uuid-456 "What are the best email marketing tools?"
```

#### `/botsee generate-questions <persona_uuid> [count]`
Generate questions for a persona using AI. Defaults to 5.

```bash
/botsee generate-questions persona-uuid-456
/botsee generate-questions persona-uuid-456 10
```

**Cost:** 10 credits per generation call (not per question)

#### `/botsee update-question <uuid> <question_text>`
Update a question's text.

```bash
/botsee update-question question-uuid-789 "What are the best affordable email marketing tools?"
```

#### `/botsee delete-question <uuid>`
Delete a question permanently.

```bash
/botsee delete-question question-uuid-789
```

---

### Results Commands

#### `/botsee results-competitors`
View competitor analysis results from the latest analysis.

```bash
/botsee results-competitors
```

#### `/botsee results-keywords`
View keyword analysis results from the latest analysis.

```bash
/botsee results-keywords
```

#### `/botsee results-sources`
View source analysis results (which websites cited your site/competitors).

```bash
/botsee results-sources
```

#### `/botsee results-responses`
View all raw AI responses from the latest analysis.

```bash
/botsee results-responses
```

## Full CRUD Operations

BotSee skill provides complete CRUD (Create, Read, Update, Delete) operations for all resources:

**Sites:** List, view, create, and archive sites
**Customer Types:** List, view, create, generate (AI), update, and archive types
**Personas:** List, view, create, generate (AI), update, and archive personas
**Questions:** List, view, create, generate (AI), update, and delete questions

You can:
- Use the high-level `/botsee setup` command for automatic setup
- Or manually build your structure using individual CRUD commands
- View and edit any resource at any time
- Generate additional resources as needed
- Customize your analysis by adding/removing questions

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

## Example Workflows

### New User Setup
```bash
/botsee setup https://www.example.com

# Output:
🤖 BotSee Setup

📋 Complete signup to get your API key:

   https://botsee.io/setup/abc123...

⏳ Waiting for signup completion...
✅ Signup complete!

Using: 2 types, 2 personas/type, 5 questions/persona

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

### Custom Setup
```bash
/botsee configure https://www.example.com --types 3 --personas 3 --questions 10
/botsee config-show
/botsee setup https://www.example.com --api-key bts_live_abc123...
```

### Run Analysis and Generate Content
```bash
/botsee analyze
/botsee content
```

### View and Edit Personas
```bash
# List all personas
/botsee list-personas

# View specific persona
/botsee get-persona persona-uuid-456

# Update persona description
/botsee update-persona persona-uuid-456 --description "Chief Marketing Officer at enterprise SaaS"

# List questions for this persona
/botsee list-questions persona-uuid-456

# Add a new question
/botsee create-question persona-uuid-456 "What are the best alternatives to HubSpot?"
```

### Manage Customer Types
```bash
# List all customer types
/botsee list-types

# Add a new customer type manually
/botsee create-type "Startup Founders" "Early-stage founders bootstrapping their companies"

# Generate personas for the new type
/botsee generate-personas type-uuid-new 3

# Generate questions for each persona
/botsee list-personas type-uuid-new
/botsee generate-questions persona-uuid-1 10
/botsee generate-questions persona-uuid-2 10
/botsee generate-questions persona-uuid-3 10
```

### View Results
```bash
# After running analysis, view different result types
/botsee results-competitors
/botsee results-keywords
/botsee results-sources
/botsee results-responses
```

## Troubleshooting

**"Invalid API key"**
- Run `/botsee setup <domain>` to create a new account
- Or use `--api-key` with a valid key

**"Insufficient credits"**
- Add credits at https://botsee.io/billing

**"Connection error"**
- Check internet connection
- API calls timeout after 30 seconds

## Credits & Costs

### Setup (one-time with defaults)
- Site creation: **5 credits**
- Generate 2 customer types: **10 credits** (5 each)
- Generate 4 personas: **20 credits** (5 each)
- Generate questions (4 calls): **40 credits** (10 per call, not per question)
- **Total:** ~75 credits

### Individual Operations
- **Create site:** 5 credits (auto-generates product_name/value_proposition)
- **Create customer type:** 5 credits
- **Generate customer types:** 5 credits per type
- **Create persona:** 5 credits
- **Generate personas:** 5 credits per persona
- **Generate questions:** 10 credits per call (generates multiple questions)
- **Analysis (per run):** ~660 credits (varies by question count and models)
- **Content generation:** 15 credits

### Example Workflows
- **First complete workflow** (setup + analysis + content): ~750 credits
- **Add new customer type with 3 personas (10 questions each):**
  - Create type: 5 credits
  - Generate 3 personas: 15 credits
  - Generate questions (3 calls): 30 credits
  - **Total:** 50 credits

## License

MIT License - see LICENSE file

## Support

- Documentation: https://botsee.io/docs
- Issues: https://github.com/rivalsee/botsee-skill/issues
