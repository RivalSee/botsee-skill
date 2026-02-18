---
name: botsee
description: AI-powered competitive intelligence via BotSee API
version: 2.0.0
---

# BotSee Skill

Get AI-powered competitive intelligence on any website.

Commands:

**Workflow:**
- /botsee                                  - Quick status and help
- /botsee signup [--email EMAIL] [--name NAME] [--company COMPANY] [--api-key KEY] [--payment-method stripe|usdc] [--crypto] - Signup with credit card by default, or prepare USDC signup
- /botsee signup-pay-usdc --amount-cents N --from-address 0x... [--token TOKEN] [--tx-hash 0x...] - Start USDC payment for signup on Base mainnet
- /botsee signup-status [--token TOKEN]    - Check signup completion and save API key
- /botsee topup-usdc --amount-cents N --from-address 0x... [--tx-hash 0x...] - Add credits with USDC on Base mainnet
- /botsee create-site <domain> [--types N]   - Save custom config
- /botsee config-show                      - Display saved config
- /botsee analyze                          - Run competitive analysis
- /botsee content                          - Generate blog post from analysis

**Sites:**
- /botsee list-sites             - List all sites
- /botsee get-site [uuid]        - View site details
- /botsee create-site <domain>   - Create a new site
- /botsee archive-site [uuid]    - Archive a site

**Customer Types:**
- /botsee list-types             - List customer types
- /botsee get-type <uuid>        - View type details
- /botsee create-type <name> [desc] - Create customer type
- /botsee generate-types [count] - Generate customer types
- /botsee update-type <uuid> [name] [desc] - Update customer type
- /botsee archive-type <uuid>    - Archive customer type

**Personas:**
- /botsee list-personas [type]   - List personas (all or by type)
- /botsee get-persona <uuid>     - View persona details
- /botsee create-persona <type> <name> [desc] - Create persona
- /botsee generate-personas <type> [count] - Generate personas for type
- /botsee update-persona <uuid> [name] [desc] - Update persona
- /botsee archive-persona <uuid> - Archive persona

**Questions:**
- /botsee list-questions [persona] - List questions (all or by persona)
- /botsee get-question <uuid>    - View question details
- /botsee create-question <persona> <text> - Create question
- /botsee generate-questions <persona> [count] - Generate questions for persona
- /botsee update-question <uuid> <text> - Update question text
- /botsee delete-question <uuid> - Delete question

**Results:**
- /botsee results-competitors <uuid>    - View competitor results
- /botsee results-keywords <uuid>       - View keyword results
- /botsee results-sources <uuid>        - View source results
- /botsee results-responses <uuid>      - View all AI responses

## Implementation

When user invokes a BotSee command, run the corresponding Python script. All commands use a single bundled script that handles API calls internally.

### /botsee (status)

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py status
```

### /botsee signup [--email EMAIL] [--name NAME] [--company COMPANY] [--api-key KEY] [--payment-method stripe|usdc] [--crypto]

**New user signup flow:**

**Step 1: Get signup URL**
```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py signup
```

This displays a signup URL. Tell the user: "Visit this URL to complete signup and get your API key. Then paste your API key here."
This is the **credit card signup flow**.

**Step 2: User pastes API key in conversation**

When the user provides their API key (e.g., "Here's my API key: bts_live_abc123"), extract it and save it:

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py signup --api-key <extracted-key>
```

**Step 3: User runs create-site**

After saving the API key, the user can run:
```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py create-site <domain>
```

**IMPORTANT: Agent behavior when user pastes API key**

When you detect a BotSee API key in the conversation (format: `bts_live_*` or `bts_test_*`):
1. Automatically run `signup --api-key <key>` to save it
2. Confirm to the user: "✅ API key saved! You can now run /botsee create-site <domain>"
3. Do NOT ask the user to manually run the signup command with the key

**Example conversation:**
```
User: /botsee signup
Assistant: [runs signup, gets URL] "Visit https://botsee.io/setup/TOKEN to complete signup. Paste your API key here when you get it."

User: "Here's my API key: bts_live_abc123def456"
Assistant: [automatically runs: signup --api-key bts_live_abc123def456]
         "✅ API key saved! Run /botsee create-site <your-domain> to set up your site."

User: /botsee create-site https://example.com
Assistant: [runs create-site, which uses saved API key]
```

Existing user (has API key):

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py signup --api-key <key>
```

**What happens:**
1. Validates API key
2. Saves API key to `~/.botsee/config.json`

**Crypto flow (USDC on Base):**
```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py signup --crypto
python3 ~/.claude/skills/botsee/scripts/botsee.py signup-pay-usdc --amount-cents 250 --from-address 0x...
python3 ~/.claude/skills/botsee/scripts/botsee.py signup-status
```

USDC network:
- `base-mainnet` (Chain ID 8453)

### /botsee signup-pay-usdc --amount-cents N --from-address 0x... [--token TOKEN] [--tx-hash 0x...]

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py signup-pay-usdc --amount-cents 5000 --from-address 0x1234...
```

Use `--payment <proof>` to send x402 `payment` header when retrying after HTTP 402.
Use `--tx-hash <0x...>` to auto-build transaction-based x402 payload (`txHash`, `network`, `asset`, `amount`, `payer`).

### /botsee signup-status [--token TOKEN]

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py signup-status
```

Saves API key to `~/.botsee/config.json` automatically once signup is completed.

### /botsee topup-usdc --amount-cents N --from-address 0x... [--tx-hash 0x...]

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py topup-usdc --amount-cents 5000 --from-address 0x1234...
```

Use `--payment <proof>` to send x402 `payment` header when retrying after HTTP 402.
Use `--tx-hash <0x...>` to auto-build transaction-based x402 payload (`txHash`, `network`, `asset`, `amount`, `payer`).

### /botsee create-site <domain> [--types T] [--personas P] [--questions Q]

**Requires:** API key from `/botsee signup`

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py create-site <domain>
```

**Optional parameters:**
- `--types` (default: 2, range: 1-3)
- `--personas` (default: 2, range: 1-3)
- `--questions` (default: 5, range: 3-10)

**What happens:**
1. Creates a site for the domain
2. Generates customer types, personas, and questions
3. Saves configuration to workspace and user config

**Customize generation counts:**
```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py create-site <domain> --types 3 --personas 2 --questions 10
```

### /botsee config-show

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py config-show
```

### /botsee analyze

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py analyze
```

Starts analysis, polls until complete, then displays competitors, keywords, and sources.

### /botsee content

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py content
```

Generates blog post from latest analysis. Auto-saves to `botsee-YYYYMMDD-HHMMSS.md`.

---

## Sites Commands

### /botsee list-sites

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py list-sites
```

### /botsee get-site [uuid]

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py get-site [uuid]
```

If uuid is omitted, uses the site from `~/.botsee/config.json`.

### /botsee create-site <domain>

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py create-site <domain>
```

### /botsee archive-site [uuid]

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py archive-site [uuid]
```

---

## Customer Types Commands

### /botsee list-types

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py list-types
```

### /botsee get-type <uuid>

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py get-type <uuid>
```

### /botsee create-type <name> [description]

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py create-type "Enterprise Buyers" "Large companies seeking solutions"
```

### /botsee generate-types [count]

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py generate-types 3
```

Defaults to 2 if count is omitted.

### /botsee update-type <uuid> [name] [description]

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py update-type <uuid> --name "New Name" --description "New description"
```

### /botsee archive-type <uuid>

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py archive-type <uuid>
```

---

## Personas Commands

### /botsee list-personas [type_uuid]

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py list-personas
python3 ~/.claude/skills/botsee/scripts/botsee.py list-personas <type_uuid>
```

### /botsee get-persona <uuid>

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py get-persona <uuid>
```

### /botsee create-persona <type_uuid> <name> [description]

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py create-persona <type_uuid> "Sarah Chen" "VP of Marketing at mid-sized SaaS company"
```

### /botsee generate-personas <type_uuid> [count]

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py generate-personas <type_uuid> 3
```

Defaults to 2 if count is omitted.

### /botsee update-persona <uuid> [name] [description]

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py update-persona <uuid> --name "New Name" --description "New description"
```

### /botsee archive-persona <uuid>

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py archive-persona <uuid>
```

---

## Questions Commands

### /botsee list-questions [persona_uuid]

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py list-questions
python3 ~/.claude/skills/botsee/scripts/botsee.py list-questions <persona_uuid>
```

### /botsee get-question <uuid>

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py get-question <uuid>
```

### /botsee create-question <persona_uuid> <question_text>

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py create-question <persona_uuid> "What are the best email marketing tools?"
```

### /botsee generate-questions <persona_uuid> [count]

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py generate-questions <persona_uuid> 5
```

Defaults to 5 if count is omitted.

### /botsee update-question <uuid> <question_text>

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py update-question <uuid> "What are the best affordable email marketing tools?"
```

### /botsee delete-question <uuid>

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py delete-question <uuid>
```

---

## Results Commands

### /botsee results-competitors <analysis_uuid>

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py results-competitors <analysis_uuid>
```

### /botsee results-keywords <analysis_uuid>

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py results-keywords <analysis_uuid>
```

### /botsee results-sources <analysis_uuid>

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py results-sources <analysis_uuid>
```

### /botsee results-responses <analysis_uuid>

```bash
python3 ~/.claude/skills/botsee/scripts/botsee.py results-responses <analysis_uuid>
```

**Getting the Analysis UUID:**
The analysis UUID is displayed when you run `/botsee analyze`:
```
📊 Analysis started: abc-def-123
```
Copy the UUID and use it with the results commands to view detailed analysis data.

---

## Agent Usage Notes

This skill is designed for **non-interactive agent usage**. All commands accept arguments via command-line flags - no prompts or user input required.

### Key Considerations for Agents

**1. Signup Flow Requires Human Intervention**

For **new users** without an API key, the signup command creates a signup token and displays a URL:
```bash
/botsee signup
# Outputs signup URL for browser completion
```

**Agents should:**
- Use the `--api-key` flag if API key is available
- Inform user if signup is needed (cannot be completed by agent)
- Consider API key as a prerequisite for autonomous operation

**2. Async Operations with Polling**

Two commands can involve waiting/polling:
- `/botsee signup-status` (checks signup completion)
- `/botsee analyze`: up to 10 minute timeout

Commands will block until complete or timeout. No intermediate progress updates.

**3. Analysis Discovery**

To view detailed results after analysis:
1. Run `/botsee analyze` and capture the analysis UUID from output
2. Use UUID with `/botsee results-*` commands

**Recommended pattern:**
```bash
# Run analysis
output=$(/botsee analyze)
# Extract UUID (line containing "Analysis started:")
uuid=$(echo "$output" | grep "Analysis started:" | awk '{print $NF}')
# View results
/botsee results-competitors "$uuid"
```

**4. Configuration Files**

Two config files exist:
- **User config:** `~/.botsee/config.json` (API key + site UUID)
- **Workspace config:** `.context/botsee-config.json` (generation defaults, optional)

Agents can discover state via:
- `/botsee` - Shows account status
- `/botsee config-show` - Shows workspace config

**5. Credit Costs**

All operations that consume credits display remaining balance. Agents should:
- Check balance before expensive operations (`/botsee` command)
- Handle "Insufficient credits" errors gracefully
- Monitor credit usage (shown after each operation)

**Costs:**
- Setup (~75 credits with defaults 2/2/5)
- Analysis (~660 credits per run)
- Content generation (15 credits)

**6. Error Handling**

All errors exit with code 1 and print to stderr. Error messages include:
- HTTP status codes (when relevant)
- Actionable next steps
- No API key leakage (sanitized)

**7. Idempotency**

- **Safe to retry:** Status, list, get commands (read-only)
- **Not idempotent:** Create commands (will create duplicates)
- **Updates:** Require specific UUID, safe to retry

**8. Output Format**

- **CRUD operations:** JSON output for parsing
- **Workflow commands:** Human-readable formatted text
- **Status/balance:** Always displayed at command completion

### Example Agent Workflow

```bash
# 1. Check status (discover state)
/botsee

# 2. Save API key if provided by user
/botsee signup --api-key bts_live_abc123

# 3. Create a site
/botsee create-site https://example.com

# 4. Run analysis (captures UUID)
analysis_output=$(/botsee analyze)
uuid=$(echo "$analysis_output" | grep -oP '(?<=Analysis started: )\S+')

# 5. View results
/botsee results-competitors "$uuid"

# 6. Generate content
/botsee content

# 7. Check final balance
/botsee
```
