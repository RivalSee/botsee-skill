---
name: botsee
description: AI-powered competitive intelligence via BotSee API
version: 1.0.0
---

# BotSee Skill

Get AI-powered competitive intelligence on any website.

Commands:
- /botsee              - Quick status and help
- /botsee setup        - Configure API key and site interactively
- /botsee analyze      - Full competitive analysis
- /botsee content      - Generate blog post from analysis

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
      echo "Get started: /botsee setup"
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
    echo "  /botsee analyze  - Analyze website"
    echo "  /botsee content  - Generate blog post"
    echo "  /botsee setup    - Reconfigure"
    ;;

```

  "setup")
    # /botsee setup - Interactive site configuration
    echo "🤖 BotSee Setup - Interactive Configuration"
    echo ""

    # 1. Get API key
    echo "Get your API key: https://botsee.io/signup"
    read -sp "Enter API key: " api_key
    echo ""

    if [ -z "$api_key" ]; then
      echo "❌ API key required"
      exit 1
    fi

    # Validate and get balance
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

    # Inline API helper
    api_call() {
      local method="$1" endpoint="$2" data="$3"
      curl -s -m 30 -X "$method" \
        -H "Authorization: Bearer $api_key" \
        -H "Content-Type: application/json" \
        ${data:+-d "$data"} "https://botsee.io/v1$endpoint"
    }

    # 2. Get website URL
    read -p "Website URL to analyze: " url
    [[ "$url" =~ ^https?:// ]] || url="https://$url"

    echo "⏳ Creating site..."
    site=$(api_call POST /sites "{\"url\":\"$url\"}")
    site_uuid=$(echo "$site" | jq -r '.site.uuid')
    echo "✅ Site created: $site_uuid"
    echo ""

    # 3. Customer Types - Interactive loop
    while true; do
      read -p "How many customer types? (1-3, recommend 2): " ct_count
      ct_count=${ct_count:-2}

      echo "⏳ Generating $ct_count customer type(s)..."
      ct=$(api_call POST "/sites/$site_uuid/customer-types/generate" "{\"count\":$ct_count}")

      echo ""
      echo "📋 Generated Customer Types:"
      echo "$ct" | jq -r '.customer_types[] | "  - \(.name)"'
      echo ""

      read -p "Comments or changes? (Enter to continue, 'r' to regenerate): " feedback
      [ "$feedback" != "r" ] && break

      # Delete and regenerate
      echo "⏳ Regenerating..."
      for uuid in $(echo "$ct" | jq -r '.customer_types[].uuid'); do
        api_call DELETE "/customer-types/$uuid" >/dev/null
      done
    done

    ct_uuids=($(echo "$ct" | jq -r '.customer_types[].uuid'))
    echo "✅ Locked in ${#ct_uuids[@]} customer type(s)"
    echo ""

    # 4. Personas - Interactive loop per customer type
    all_persona_uuids=()
    for ct_uuid in "${ct_uuids[@]}"; do
      ct_name=$(echo "$ct" | jq -r ".customer_types[] | select(.uuid==\"$ct_uuid\") | .name")

      while true; do
        read -p "Personas for '$ct_name'? (1-3, recommend 2): " p_count
        p_count=${p_count:-2}

        echo "⏳ Generating $p_count persona(s)..."
        personas=$(api_call POST "/customer-types/$ct_uuid/personas/generate" "{\"count\":$p_count}")

        echo ""
        echo "📋 Generated Personas for '$ct_name':"
        echo "$personas" | jq -r '.personas[] | "  - \(.name): \(.description[:80])..."'
        echo ""

        read -p "Comments? (Enter to continue, 'r' to regenerate): " feedback
        [ "$feedback" != "r" ] && break

        # Delete and regenerate
        for uuid in $(echo "$personas" | jq -r '.personas[].uuid'); do
          api_call DELETE "/personas/$uuid" >/dev/null
        done
      done

      p_uuids=($(echo "$personas" | jq -r '.personas[].uuid'))
      all_persona_uuids+=("${p_uuids[@]}")
    done

    echo "✅ Locked in ${#all_persona_uuids[@]} persona(s)"
    echo ""

    # 5. Questions - Interactive loop per persona
    for p_uuid in "${all_persona_uuids[@]}"; do
      # Get persona name from previous responses
      p_name=$(echo "$personas" | jq -r ".personas[] | select(.uuid==\"$p_uuid\") | .name" 2>/dev/null || echo "Persona")

      while true; do
        read -p "Questions for '$p_name'? (3-10, recommend 5): " q_count
        q_count=${q_count:-5}

        echo "⏳ Generating $q_count question(s)..."
        questions=$(api_call POST "/personas/$p_uuid/questions/generate" "{\"count\":$q_count}")

        echo ""
        echo "📋 Generated Questions:"
        echo "$questions" | jq -r '.questions[] | "  - \(.question)"'
        echo ""

        read -p "Comments? (Enter to continue, 'r' to regenerate): " feedback
        [ "$feedback" != "r" ] && break

        # Delete and regenerate
        for uuid in $(echo "$questions" | jq -r '.questions[].uuid'); do
          api_call DELETE "/questions/$uuid" >/dev/null
        done
      done
    done

    # 6. Save configuration
    mkdir -p ~/.botsee && chmod 700 ~/.botsee
    (umask 077; echo "{\"api_key\":\"$api_key\",\"site_uuid\":\"$site_uuid\"}" > ~/.botsee/config.json)

    echo ""
    echo "✅ Setup complete!"
    echo "💰 Balance: $balance credits"
    echo ""
    echo "Run: /botsee analyze"
    ;;

```

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

```

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
    read -p "Save to file? (y/n) " save

    if [ "$save" = "y" ]; then
      filename="botsee-$(date +%Y%m%d-%H%M%S).md"
      echo "$content" > "$filename"
      echo "✅ Saved: $filename"
    fi
    ;;

  *)
    echo "❌ Unknown command: $command"
    echo ""
    echo "Available commands:"
    echo "  /botsee          - Status and help"
    echo "  /botsee setup    - Configure API key"
    echo "  /botsee analyze  - Run analysis"
    echo "  /botsee content  - Generate content"
    exit 1
    ;;
esac
```
