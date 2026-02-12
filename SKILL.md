---
name: botsee
description: AI-powered competitive intelligence via BotSee API
version: 2.0.0
---

# BotSee Skill

Get AI-powered competitive intelligence on any website.

Commands:
- /botsee                              - Quick status and help
- /botsee setup <api_key> <domain>     - Setup with defaults (2/2/5)
- /botsee configure <domain> [t p q]   - Save custom config
- /botsee config-show                  - Display saved config
- /botsee analyze                      - Run competitive analysis
- /botsee content                      - Generate blog post from analysis

<!-- Implementation will be added in next tasks -->

## Implementation

```bash
#!/bin/bash

# Parse command
command="${1:-}"

case "$command" in
  "")
    # /botsee - Quick status & help
    if [ ! -f ~/.botsee/config.json ]; then
      echo "🤖 BotSee - AI Competitive Intelligence"
      echo ""
      echo "Get started: /botsee setup <api_key> <domain>"
      echo "Learn more: https://botsee.io/docs"
      exit 0
    fi

    # Config exists - show status
    api_key=$(jq -r '.api_key' ~/.botsee/config.json 2>/dev/null)
    key_prefix="${api_key:0:15}"

    # Direct API call with inline error handling
    response=$(curl -s -m 30 -w "\n%{http_code}" \
      -H "Authorization: Bearer $api_key" \
      "https://botsee.io/v1/usage")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" != "200" ]; then
      echo "❌ API error ($http_code). Run: /botsee setup"
      exit 1
    fi

    balance=$(echo "$body" | jq -r '.balance')
    sites=$(echo "$body" | jq -r '.sites_count // 0')

    echo "🤖 BotSee"
    echo "━━━━━━━━━━━━━━━"
    echo "💰 Credits: $balance"
    echo "🌐 Sites: $sites"
    echo "🔑 Key: ${key_prefix}..."
    echo ""
    echo "Commands:"
    echo "  /botsee setup <key> <domain>  - Quick setup with defaults"
    echo "  /botsee configure <domain>    - Custom configuration"
    echo "  /botsee analyze               - Analyze website"
    echo "  /botsee content               - Generate blog post"
    ;;

  "configure")
    # /botsee configure <domain> [types] [personas] [questions]
    # Save configuration for later use with /botsee setup
    echo "🤖 BotSee Configuration"
    echo ""

    domain="${2:-}"
    types="${3:-2}"
    personas="${4:-2}"
    questions="${5:-5}"

    # Validate domain
    if [ -z "$domain" ]; then
      echo "❌ Domain required"
      echo ""
      echo "Usage: /botsee configure <domain> [types] [personas] [questions]"
      echo "Example: /botsee configure https://example.com 2 2 5"
      exit 1
    fi

    # Add https:// if missing
    [[ "$domain" =~ ^https?:// ]] || domain="https://$domain"

    # Validate ranges
    if [ "$types" -lt 1 ] || [ "$types" -gt 3 ]; then
      echo "❌ Customer types must be 1-3"
      exit 1
    fi

    if [ "$personas" -lt 1 ] || [ "$personas" -gt 3 ]; then
      echo "❌ Personas per type must be 1-3"
      exit 1
    fi

    if [ "$questions" -lt 3 ] || [ "$questions" -gt 10 ]; then
      echo "❌ Questions per persona must be 3-10"
      exit 1
    fi

    # Create .context directory if needed
    mkdir -p .context

    # Save configuration
    cat > .context/botsee-config.json <<EOF
{
  "domain": "$domain",
  "types": $types,
  "personas_per_type": $personas,
  "questions_per_persona": $questions
}
EOF

    echo "✅ Configuration saved to .context/botsee-config.json"
    echo ""
    echo "Domain: $domain"
    echo "Customer Types: $types"
    echo "Personas per Type: $personas"
    echo "Questions per Persona: $questions"
    echo ""
    echo "Next: /botsee setup <api_key>"
    ;;

  "config-show")
    # /botsee config-show - Display saved configuration
    echo "📋 BotSee Configuration"
    echo "━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    if [ ! -f .context/botsee-config.json ]; then
      echo "No configuration found."
      echo ""
      echo "Create config: /botsee configure <domain> [types] [personas] [questions]"
      echo "Example: /botsee configure https://example.com 2 2 5"
      exit 0
    fi

    domain=$(jq -r '.domain' .context/botsee-config.json)
    types=$(jq -r '.types' .context/botsee-config.json)
    personas=$(jq -r '.personas_per_type' .context/botsee-config.json)
    questions=$(jq -r '.questions_per_persona' .context/botsee-config.json)

    echo "Domain: $domain"
    echo "Customer Types: $types"
    echo "Personas per Type: $personas"
    echo "Questions per Persona: $questions"
    echo ""
    echo "Ready to run: /botsee setup <api_key>"
    ;;

  "setup")
    # /botsee setup <api_key> [domain] - Non-interactive site configuration
    echo "🤖 BotSee Setup"
    echo ""

    # Parse arguments
    api_key="${2:-}"
    domain_arg="${3:-}"

    # Validate API key
    if [ -z "$api_key" ]; then
      echo "❌ API key required"
      echo ""
      echo "Usage: /botsee setup <api_key> <domain>"
      echo "   or: /botsee setup <api_key>  (uses saved config)"
      echo ""
      echo "Get API key: https://botsee.io/signup"
      exit 1
    fi

    # Validate API key and get balance
    response=$(curl -s -m 30 -w "\n%{http_code}" \
      -H "Authorization: Bearer $api_key" "https://botsee.io/v1/usage")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" != "200" ]; then
      echo "❌ Invalid API key"
      exit 1
    fi

    balance=$(echo "$body" | jq -r '.balance')
    echo "✅ API key valid | Balance: $balance credits"
    echo ""

    # Load configuration
    if [ -n "$domain_arg" ]; then
      # Use provided domain with defaults
      domain="$domain_arg"
      [[ "$domain" =~ ^https?:// ]] || domain="https://$domain"
      types=2
      personas=2
      questions=5
      echo "Using defaults: $types types, $personas personas/type, $questions questions/persona"
    elif [ -f .context/botsee-config.json ]; then
      # Load from saved config
      domain=$(jq -r '.domain' .context/botsee-config.json)
      types=$(jq -r '.types' .context/botsee-config.json)
      personas=$(jq -r '.personas_per_type' .context/botsee-config.json)
      questions=$(jq -r '.questions_per_persona' .context/botsee-config.json)
      echo "Loaded config: $types types, $personas personas/type, $questions questions/persona"
    else
      echo "❌ No domain provided and no saved config found"
      echo ""
      echo "Usage: /botsee setup <api_key> <domain>"
      echo "   or: /botsee configure <domain> && /botsee setup <api_key>"
      exit 1
    fi

    echo ""

    # Inline API helper
    api_call() {
      local method="$1" endpoint="$2" data="$3"
      curl -s -m 30 -X "$method" \
        -H "Authorization: Bearer $api_key" \
        -H "Content-Type: application/json" \
        ${data:+-d "$data"} "https://botsee.io/v1$endpoint"
    }

    # Create site
    echo "⏳ Creating site: $domain"
    site=$(api_call POST /sites "{\"url\":\"$domain\"}")
    site_uuid=$(echo "$site" | jq -r '.site.uuid')
    echo "✅ Site created: $site_uuid"
    echo ""

    # Generate customer types
    echo "⏳ Generating $types customer type(s)..."
    ct=$(api_call POST "/sites/$site_uuid/customer-types/generate" "{\"count\":$types}")
    ct_uuids=($(echo "$ct" | jq -r '.customer_types[].uuid'))

    echo "📋 Customer Types:"
    echo "$ct" | jq -r '.customer_types[] | "  • \(.name)"'
    echo ""

    # Generate personas for each customer type
    echo "⏳ Generating personas ($personas per type)..."
    all_persona_uuids=()
    persona_count=0

    for ct_uuid in "${ct_uuids[@]}"; do
      ct_name=$(echo "$ct" | jq -r ".customer_types[] | select(.uuid==\"$ct_uuid\") | .name")

      personas_resp=$(api_call POST "/customer-types/$ct_uuid/personas/generate" "{\"count\":$personas}")
      p_uuids=($(echo "$personas_resp" | jq -r '.personas[].uuid'))
      all_persona_uuids+=("${p_uuids[@]}")
      persona_count=$((persona_count + ${#p_uuids[@]}))

      echo "  ✓ $ct_name: ${#p_uuids[@]} persona(s)"
    done

    echo "✅ Generated $persona_count persona(s)"
    echo ""

    # Generate questions for each persona
    echo "⏳ Generating questions ($questions per persona)..."
    question_count=0

    for p_uuid in "${all_persona_uuids[@]}"; do
      questions_resp=$(api_call POST "/personas/$p_uuid/questions/generate" "{\"count\":$questions}")
      q_count=$(echo "$questions_resp" | jq -r '.questions | length')
      question_count=$((question_count + q_count))
    done

    echo "✅ Generated $question_count question(s)"
    echo ""

    # Save configuration
    mkdir -p ~/.botsee && chmod 700 ~/.botsee
    (umask 077; echo "{\"api_key\":\"$api_key\",\"site_uuid\":\"$site_uuid\"}" > ~/.botsee/config.json)

    # Final summary
    echo "✅ Setup complete!"
    echo ""
    echo "Generated:"
    echo "  • $types customer type(s)"
    echo "  • $persona_count persona(s)"
    echo "  • $question_count question(s)"
    echo ""
    echo "💰 Remaining: $balance credits"
    echo ""
    echo "Next: /botsee analyze"
    ;;

  "analyze")
    # /botsee analyze - Run analysis on pre-configured site
    echo "🤖 BotSee Analysis"
    echo ""

    # Read config
    if [ ! -f ~/.botsee/config.json ]; then
      echo "❌ Not configured. Run: /botsee setup"
      exit 1
    fi

    api_key=$(jq -r '.api_key' ~/.botsee/config.json)
    site_uuid=$(jq -r '.site_uuid' ~/.botsee/config.json)

    if [ -z "$site_uuid" ] || [ "$site_uuid" = "null" ]; then
      echo "❌ No site configured. Run: /botsee setup"
      exit 1
    fi

    # Inline API helper
    api_call() {
      local method="$1" endpoint="$2" data="$3"
      local resp=$(curl -s -m 30 -w "\n%{http_code}" \
        -X "$method" \
        -H "Authorization: Bearer $api_key" \
        -H "Content-Type: application/json" \
        ${data:+-d "$data"} \
        "https://botsee.io/v1$endpoint")

      local code=$(echo "$resp" | tail -n1)
      local body=$(echo "$resp" | head -n-1)

      if [ "$code" = "402" ]; then
        echo "❌ Insufficient credits"
        echo "$body" | jq -r '.balance // "unknown"' 2>/dev/null
        echo "Add credits: https://botsee.io/billing"
        exit 1
      elif [[ ! "$code" =~ ^(200|201|202)$ ]]; then
        echo "❌ API error ($code)"
        exit 1
      fi

      echo "$body"
    }

    # Start analysis
    echo "⏳ Starting analysis..."
    analysis=$(api_call POST /analysis "{
      \"site_uuid\":\"$site_uuid\",
      \"scope\":\"site\",
      \"models\":[\"openai\",\"claude\",\"perplexity\"]
    }")

    analysis_uuid=$(echo "$analysis" | jq -r '.analysis.uuid')
    echo "📊 Analysis UUID: $analysis_uuid"
    echo ""

    # Poll with cancellation support
    trap 'echo ""; echo "⚠️ Cancelled. UUID: $analysis_uuid"; exit 130' INT

    attempt=0
    while [ $attempt -lt 60 ]; do
      status_resp=$(api_call GET "/analysis/$analysis_uuid")
      status=$(echo "$status_resp" | jq -r '.analysis.status')

      case $status in
        completed|partial)
          echo "✅ Analysis complete!"
          break
          ;;
        failed)
          echo "❌ Analysis failed"
          exit 1
          ;;
        *)
          printf "\r⏳ Analyzing... %dm %ds" $((attempt/6)) $((attempt%6*10))
          sleep 10
          ((attempt++))
          ;;
      esac
    done

    trap - INT

    if [ $attempt -eq 60 ]; then
      echo ""
      echo "⏰ Timeout. UUID: $analysis_uuid"
      exit 1
    fi

    # Fetch and display results
    echo ""
    echo "⏳ Fetching results..."
    competitors=$(api_call GET "/analysis/$analysis_uuid/competitors")
    keywords=$(api_call GET "/analysis/$analysis_uuid/keywords")

    echo ""
    echo "📊 Top Competitors:"
    echo "$competitors" | jq -r '.competitors[:10][] | "  \(.rank // "?"). \(.company_name) - \(.mentions) mentions"'

    echo ""
    echo "🔑 Top Keywords:"
    echo "$keywords" | jq -r '.keywords[:10][] | "  • \(.keyword) (\(.frequency)x)"'

    # Show balance
    echo ""
    usage=$(api_call GET /usage)
    balance=$(echo "$usage" | jq -r '.balance')
    echo "💰 Remaining: $balance credits"
    echo ""
    echo "💡 Next: /botsee content"
    ;;

  "content")
    # /botsee content - Generate blog post from analysis
    echo "🤖 BotSee Content Generator"
    echo "💡 Cost: 15 credits"
    echo ""

    # Read config
    if [ ! -f ~/.botsee/config.json ]; then
      echo "❌ Not configured. Run: /botsee setup"
      exit 1
    fi

    api_key=$(jq -r '.api_key' ~/.botsee/config.json)

    # Inline API call helper
    api_call() {
      local method="$1" endpoint="$2" data="$3"
      local resp=$(curl -s -m 30 -w "\n%{http_code}" \
        -X "$method" \
        -H "Authorization: Bearer $api_key" \
        -H "Content-Type: application/json" \
        ${data:+-d "$data"} \
        "https://botsee.io/v1$endpoint")

      local code=$(echo "$resp" | tail -n1)
      local body=$(echo "$resp" | head -n-1)

      case $code in
        200|201) echo "$body" ;;
        402)
          echo "❌ Insufficient credits (need 15)"
          echo "$body" | jq -r '.balance // empty' 2>/dev/null
          exit 1
          ;;
        *)
          echo "❌ API error ($code)"
          exit 1
          ;;
      esac
    }

    # Get latest site and analysis
    sites=$(api_call GET /sites)
    site_uuid=$(echo "$sites" | jq -r '.sites[0].uuid // empty')

    if [ -z "$site_uuid" ]; then
      echo "❌ No sites found. Run: /botsee setup"
      exit 1
    fi

    analyses=$(api_call GET "/sites/$site_uuid/analysis?limit=1")
    analysis_uuid=$(echo "$analyses" | jq -r '.analyses[0].uuid // empty')

    if [ -z "$analysis_uuid" ]; then
      echo "❌ No analyses found. Run: /botsee analyze"
      exit 1
    fi

    # Generate content
    echo "⏳ Generating blog post..."
    content_resp=$(api_call POST "/analysis/$analysis_uuid/content" '{}')
    content=$(echo "$content_resp" | jq -r '.content')
    credits=$(echo "$content_resp" | jq -r '.credits_used')

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$content"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "💰 Used: $credits credits"
    echo ""

    # Auto-save with timestamp
    filename="botsee-$(date +%Y%m%d-%H%M%S).md"
    echo "$content" > "$filename"
    echo "✅ Saved: $filename"
    ;;

  *)
    echo "❌ Unknown command: $command"
    echo ""
    echo "Available commands:"
    echo "  /botsee                        - Status and help"
    echo "  /botsee setup <key> <domain>   - Quick setup (uses 2/2/5)"
    echo "  /botsee configure <domain>     - Save custom config"
    echo "  /botsee config-show            - View saved config"
    echo "  /botsee analyze                - Run analysis"
    echo "  /botsee content                - Generate content"
    exit 1
    ;;
esac
```
