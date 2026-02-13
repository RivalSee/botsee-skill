#!/usr/bin/env python3
"""BotSee CLI — AI-powered competitive intelligence via BotSee API."""

import argparse
import json
import os
import ssl
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# API Configuration
BASE_URL = "https://botsee.io"

# File Paths
USER_CONFIG = Path.home() / ".botsee" / "config.json"
WORKSPACE_CONFIG = Path(".context") / "botsee-config.json"

# Polling Configuration
POLL_INTERVAL = 3  # seconds
SIGNUP_POLL_TIMEOUT = 300  # 5 minutes
ANALYSIS_POLL_TIMEOUT = 600  # 10 minutes

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_NO_CONTENT = 204

# Validation Ranges
TYPES_MIN, TYPES_MAX = 1, 3
PERSONAS_MIN, PERSONAS_MAX = 1, 3
QUESTIONS_MIN, QUESTIONS_MAX = 3, 10

# Display Truncation
DESC_TRUNCATE_LEN = 50
TEXT_TRUNCATE_LEN = 80


def api_call(method, endpoint, data=None, api_key=None, timeout=30):
    """Make an API call to BotSee. Returns (response_dict, http_status)."""
    url = f"{BASE_URL}/v1{endpoint}"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    # Create SSL context with certificate validation
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}, resp.status
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            error_data = json.loads(raw)
            # Sanitize error messages - don't leak API keys
            if "api_key" in str(error_data).lower():
                error_data = {"error": "Authentication failed"}
            return error_data, e.code
        except (json.JSONDecodeError, ValueError):
            return {"error": "Request failed"}, e.code
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def load_user_config():
    """Load user config from ~/.botsee/config.json."""
    if not USER_CONFIG.exists():
        return None
    with open(USER_CONFIG) as f:
        return json.load(f)


def save_user_config(api_key, site_uuid):
    """Save user config to ~/.botsee/config.json with secure permissions."""
    USER_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    with open(USER_CONFIG, "w") as f:
        json.dump({"api_key": api_key, "site_uuid": site_uuid}, f, indent=2)
    os.chmod(USER_CONFIG, 0o600)
    os.chmod(USER_CONFIG.parent, 0o700)


def load_workspace_config():
    """Load workspace config from .context/botsee-config.json."""
    if not WORKSPACE_CONFIG.exists():
        return None
    with open(WORKSPACE_CONFIG) as f:
        return json.load(f)


def save_workspace_config(domain, types, personas, questions):
    """Save workspace config to .context/botsee-config.json."""
    WORKSPACE_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    with open(WORKSPACE_CONFIG, "w") as f:
        json.dump({
            "domain": domain,
            "types": types,
            "personas_per_type": personas,
            "questions_per_persona": questions,
        }, f, indent=2)


def normalize_domain(domain):
    """Ensure domain has https:// prefix."""
    if not domain.startswith(("http://", "https://")):
        domain = f"https://{domain}"
    return domain


def require_user_config():
    """Load user config or exit with error."""
    config = load_user_config()
    if not config:
        print("No BotSee config found. Run: /botsee setup <domain>", file=sys.stderr)
        sys.exit(1)
    return config


# --- Helper Functions ---


def is_success(status):
    """Check if HTTP status code indicates success (2xx)."""
    return 200 <= status < 300


def check_response(resp, status, expected_statuses=None):
    """Check API response and exit on error."""
    if expected_statuses is None:
        expected_statuses = [HTTP_OK, HTTP_CREATED, HTTP_ACCEPTED]

    if status not in expected_statuses:
        error_msg = resp.get("error", f"Request failed with HTTP {status}")
        print(f"Error: {error_msg}", file=sys.stderr)
        sys.exit(1)
    return resp


def poll_until(endpoint, status_key, complete_value, fail_value=None, api_key=None, timeout=300, interval=3):
    """
    Poll an endpoint until a condition is met.

    Args:
        endpoint: API endpoint to poll
        status_key: Key in response to check (e.g., "status")
        complete_value: Value indicating completion (e.g., "completed")
        fail_value: Value indicating failure (optional)
        api_key: API key for authentication
        timeout: Maximum time to poll in seconds
        interval: Time between polls in seconds

    Returns:
        Response dict when complete

    Raises:
        SystemExit on timeout or failure
    """
    elapsed = 0
    while elapsed < timeout:
        time.sleep(interval)
        elapsed += interval

        resp, status = api_call("GET", endpoint, api_key=api_key)
        if status != HTTP_OK:
            continue

        value = resp.get(status_key)
        if value == complete_value:
            return resp
        if fail_value and value == fail_value:
            print(f"Operation failed: {value}", file=sys.stderr)
            sys.exit(1)

    print(f"Operation timed out after {timeout} seconds", file=sys.stderr)
    sys.exit(1)


# --- High-level workflow commands ---


def cmd_status(_args):
    """Show account status and balance."""
    config = load_user_config()
    if not config:
        print("🤖 BotSee - AI Competitive Intelligence")
        print("")
        print("Get started: /botsee signup")
        print("Learn more: https://botsee.io/docs")
        return

    resp, status = api_call("GET", "/usage", api_key=config["api_key"])
    if status != HTTP_OK:
        print(f"API error ({status}). Run: /botsee signup", file=sys.stderr)
        sys.exit(1)

    # Get active site details if available
    active_site = None
    site_uuid = config.get("site_uuid")
    if site_uuid:
        site_resp, site_status = api_call("GET", f"/sites/{site_uuid}", api_key=config["api_key"])
        if site_status == HTTP_OK:
            active_site = site_resp.get("site", {})

    # Show only last 4 characters of API key for security
    key_suffix = config["api_key"][-4:] if len(config["api_key"]) >= 4 else "****"
    print("🤖 BotSee")
    print("━━━━━━━━━━━━━━━")
    print(f"💰 Credits: {resp.get('balance', '?')}")
    print(f"🌐 Sites: {resp.get('sites_count', 0)}")
    if active_site:
        site_url = active_site.get("url", "?")
        site_name = active_site.get("product_name", "?")
        print(f"📍 Active: {site_name} ({site_url})")
    print(f"🔑 Key: ...{key_suffix}")
    print("")
    print("Commands:")
    print("  /botsee signup                - Get API key")
    print("  /botsee create-site <domain>  - Create site")
    print("  /botsee analyze               - Analyze website")
    print("  /botsee content               - Generate blog post")


def cmd_signup(args):
    """Signup for BotSee: create account (new users) or validate key (existing users)."""
    if args.api_key:
        # Existing user flow - validate and save API key
        api_key = args.api_key
        resp, status = api_call("POST", "/auth/validate", api_key=api_key)
        if status != HTTP_OK:
            print(f"Invalid API key (HTTP {status})", file=sys.stderr)
            sys.exit(1)
        balance = resp.get("balance", "?")

        # Save API key to config
        save_user_config(api_key, None)

        print(f"✅ API key valid | Balance: {balance} credits")
        print("")
        print(f"Next: /botsee create-site <domain>")
        return

    # Check if there's a pending signup to complete
    pending_signup_path = os.path.join(os.path.expanduser("~/.botsee"), "pending_signup.json")
    if os.path.exists(pending_signup_path):
        # Resume pending signup
        print("🤖 BotSee Signup")
        print("")
        print("⏳ Checking signup status...")

        with open(pending_signup_path, "r") as f:
            pending = json.load(f)

        status_url = pending.get("status_url")
        setup_token = pending.get("setup_token")

        # Check status once
        poll_url = status_url if status_url else f"/signup/{setup_token}/status"
        poll_resp, poll_status = api_call("GET", poll_url)

        if poll_status == HTTP_OK:
            signup_status = poll_resp.get("status")
            if signup_status == "completed":
                api_key = poll_resp.get("api_key")
                if api_key:
                    # Save API key and clean up pending signup
                    save_user_config(api_key, None)
                    os.remove(pending_signup_path)

                    print(f"✅ Signup complete!")
                    print("")
                    print(f"Next: /botsee create-site <domain>")
                    return
            elif signup_status == "expired":
                os.remove(pending_signup_path)
                print("Signup token expired. Run /botsee signup again.", file=sys.stderr)
                sys.exit(1)

        # Still pending
        setup_url = pending.get("setup_url")
        print(f"📋 Signup not yet complete. Please visit:")
        print(f"")
        print(f"   {setup_url}")
        print(f"")
        print("Once you've completed signup, run /botsee signup again to save your API key.")
        sys.exit(0)

    # New signup - create token
    # Build signup data with optional contact fields
    signup_data = {}
    if args.email:
        signup_data["contact_email"] = args.email
    if args.name:
        signup_data["contact_name"] = args.name
    if args.company:
        signup_data["company_name"] = args.company

    # Call signup API (contact fields are optional)
    resp, status = api_call("POST", "/signup", data=signup_data)
    if not is_success(status):
        print(f"Signup failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    # Parse response - API returns setup_token, not token
    setup_token = resp.get("setup_token")
    setup_url = resp.get("setup_url")
    status_url = resp.get("status_url")  # API provides this

    if not setup_token or not setup_url:
        print(f"Unexpected signup response: {resp}", file=sys.stderr)
        sys.exit(1)

    # Show URL prominently
    print(f"")
    print(f"Complete signup: {setup_url}")
    print(f"")

    # Wait for user to complete signup
    try:
        input("Press Enter when done...")
    except (EOFError, KeyboardInterrupt):
        # Non-interactive mode or user cancelled - save pending signup and exit
        os.makedirs(os.path.dirname(pending_signup_path), exist_ok=True)
        with open(pending_signup_path, "w") as f:
            json.dump({
                "setup_token": setup_token,
                "setup_url": setup_url,
                "status_url": status_url
            }, f, indent=2)
        print("")
        print("Run /botsee signup again after completing signup to save your API key.")
        return

    print("")
    print("⏳ Checking signup status...")

    # Check status
    poll_url = status_url if status_url else f"/signup/{setup_token}/status"
    poll_resp, poll_status = api_call("GET", poll_url)

    if poll_status == HTTP_OK:
        signup_status = poll_resp.get("status")
        if signup_status == "completed":
            api_key = poll_resp.get("api_key")
            if api_key:
                # Save API key
                save_user_config(api_key, None)
                print(f"✅ Signup complete!")
                print("")
                print(f"Next: /botsee create-site <domain>")
                return
        elif signup_status == "expired":
            print("Signup token expired. Run /botsee signup again.", file=sys.stderr)
            sys.exit(1)

    # Still pending - save for later
    os.makedirs(os.path.dirname(pending_signup_path), exist_ok=True)
    with open(pending_signup_path, "w") as f:
        json.dump({
            "setup_token": setup_token,
            "setup_url": setup_url,
            "status_url": status_url
        }, f, indent=2)
    print(f"Signup not yet complete. Please complete it at:")
    print(f"   {setup_url}")
    print("")
    print("Then run /botsee signup again to save your API key.")


def cmd_create_site(args):
    """Create site and generate content."""
    # Require user config (API key must exist from signup)
    config = require_user_config()
    api_key = config.get("api_key")

    domain = normalize_domain(args.domain)
    types = args.types
    personas = args.personas
    questions = args.questions

    # Validate ranges
    if not (TYPES_MIN <= types <= TYPES_MAX):
        print(f"Error: types must be between {TYPES_MIN} and {TYPES_MAX}", file=sys.stderr)
        sys.exit(1)
    if not (PERSONAS_MIN <= personas <= PERSONAS_MAX):
        print(f"Error: personas must be between {PERSONAS_MIN} and {PERSONAS_MAX}", file=sys.stderr)
        sys.exit(1)
    if not (QUESTIONS_MIN <= questions <= QUESTIONS_MAX):
        print(f"Error: questions must be between {QUESTIONS_MIN} and {QUESTIONS_MAX}", file=sys.stderr)
        sys.exit(1)

    print(f"🤖 BotSee Configuration")
    print("")
    print(f"Using: {types} types, {personas} personas/type, {questions} questions/persona")
    print("")

    # Create site
    print(f"⏳ Creating site: {domain}")
    resp, status = api_call("POST", "/sites", data={"url": domain}, api_key=api_key)
    if status not in (200, 201):
        print(f"Site creation failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)
    site_uuid = resp.get("site", {}).get("uuid")
    print(f"✅ Site created: {site_uuid}")
    print("")

    # Generate customer types
    print(f"⏳ Generating {types} customer type(s)...")
    resp, status = api_call(
        "POST", f"/sites/{site_uuid}/customer-types/generate",
        data={"count": types}, api_key=api_key
    )
    if status not in (200, 201):
        print(f"Customer type generation failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    ct_list = resp.get("customer_types", [])
    print("📋 Customer Types:")
    for ct in ct_list:
        print(f"  • {ct.get('name', '?')}")
    print("")

    # Generate personas per type
    all_persona_uuids = []
    print(f"⏳ Generating personas ({personas} per type)...")
    for ct in ct_list:
        ct_uuid = ct.get("uuid")
        ct_name = ct.get("name", "?")
        resp, status = api_call(
            "POST", f"/customer-types/{ct_uuid}/personas/generate",
            data={"count": personas}, api_key=api_key
        )
        if status not in (200, 201):
            print(f"  ✗ {ct_name}: failed (HTTP {status})", file=sys.stderr)
            continue
        p_list = resp.get("personas", [])
        all_persona_uuids.extend(p.get("uuid") for p in p_list)
        print(f"  ✓ {ct_name}: {len(p_list)} persona(s)")

    total_personas = len(all_persona_uuids)
    print(f"✅ Generated {total_personas} persona(s)")
    print("")

    # Generate questions per persona
    total_questions = 0
    print(f"⏳ Generating questions ({questions} per persona)...")
    for p_uuid in all_persona_uuids:
        resp, status = api_call(
            "POST", f"/personas/{p_uuid}/questions/generate",
            data={"count": questions}, api_key=api_key
        )
        if status not in (200, 201):
            continue
        total_questions += len(resp.get("questions", []))
    print(f"✅ Generated {total_questions} question(s)")
    print("")

    # Save configs
    save_user_config(api_key, site_uuid)
    save_workspace_config(domain, types, personas, questions)

    # Re-fetch balance
    usage_resp, _ = api_call("GET", "/usage", api_key=api_key)
    balance = usage_resp.get("balance", "?")

    print("✅ Configuration complete!")
    print("")
    print("Generated:")
    print(f"  • {len(ct_list)} customer type(s)")
    print(f"  • {total_personas} persona(s)")
    print(f"  • {total_questions} question(s)")
    print("")
    print(f"💰 Remaining: {balance} credits")
    print("")
    print("Next steps:")
    print("  /botsee analyze           - Run competitive analysis")
    print("")
    print("View your content:")
    print("  /botsee list-types        - View customer types")
    print("  /botsee list-personas     - View all personas")
    print("  /botsee get-site          - View site details")


def cmd_config_show(_args):
    """Display saved workspace configuration."""
    config = load_workspace_config()
    if not config:
        print("No workspace config found. Run: /botsee create-site <domain>")
        return

    print("📋 BotSee Configuration")
    print("━━━━━━━━━━━━━━━━━━━━━")
    print(f"Domain: {config.get('domain', '?')}")
    print(f"Customer Types: {config.get('types', '?')}")
    print(f"Personas per Type: {config.get('personas_per_type', '?')}")
    print(f"Questions per Persona: {config.get('questions_per_persona', '?')}")
    print("")
    print("This configuration was used when creating the site.")


def cmd_analyze(args):
    """Run competitive analysis on configured site."""
    config = require_user_config()
    api_key = config["api_key"]

    # Use provided site_uuid or fall back to config
    site_uuid = args.site_uuid if hasattr(args, 'site_uuid') and args.site_uuid else config.get("site_uuid")

    print("🤖 BotSee Analysis")
    print("━━━━━━━━━━━━━━━━━━")
    print("")

    # Start analysis
    print("⏳ Starting analysis...")
    resp, status = api_call("POST", "/analysis", data={"site_uuid": site_uuid}, api_key=api_key)
    if status not in (200, 201, 202):
        print(f"Analysis failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    analysis_uuid = resp.get("analysis", {}).get("uuid")
    if not analysis_uuid:
        print(f"Unexpected response: {resp}", file=sys.stderr)
        sys.exit(1)

    print(f"📊 Analysis started: {analysis_uuid}")
    print("⏳ Processing (this may take a few minutes)...")

    # Poll for completion
    elapsed = 0
    while elapsed < 600:  # 10 minute timeout for analysis
        time.sleep(5)
        elapsed += 5

        resp, status = api_call("GET", f"/analysis/{analysis_uuid}", api_key=api_key)
        if status != 200:
            continue

        analysis_status = resp.get("analysis", {}).get("status")
        if analysis_status == "completed":
            print("✅ Analysis complete!")
            print("")
            break
        elif analysis_status == "failed":
            print("Analysis failed.", file=sys.stderr)
            sys.exit(1)
    else:
        print("Analysis timed out.", file=sys.stderr)
        sys.exit(1)

    # Fetch results
    comp_resp, _ = api_call("GET", f"/analysis/{analysis_uuid}/competitors", api_key=api_key)
    kw_resp, _ = api_call("GET", f"/analysis/{analysis_uuid}/keywords", api_key=api_key)
    src_resp, _ = api_call("GET", f"/analysis/{analysis_uuid}/sources", api_key=api_key)

    # Display competitors by customer type
    by_customer_type = comp_resp.get("by_customer_type", [])
    overall_summary = comp_resp.get("overall_summary", {})

    if by_customer_type:
        print("📊 Competitors by Customer Type:")
        print("")
        for group in by_customer_type:
            customer_type_name = group.get("customer_type_name", "Unknown")
            competitors = group.get("competitors", [])[:5]  # Top 5 per type

            if competitors:
                print(f"  {customer_type_name}:")
                for c in competitors:
                    name = c.get("name", "?")
                    appearance = c.get("appearance_percentage", 0)
                    avg_rank = c.get("avg_rank", "?")
                    mentions = c.get("mentions", 0)
                    print(f"    • {name} - {appearance:.0f}% appearance, avg rank {avg_rank}, {mentions} mentions")
                print("")

        # Show overall summary
        total_competitors = overall_summary.get("total_unique_competitors", 0)
        total_responses = overall_summary.get("total_responses_analyzed", 0)
        print(f"  Total: {total_competitors} unique competitors across {total_responses} responses")
        print("")

    # Display keywords
    keywords = kw_resp.get("keywords", [])[:10]
    if keywords:
        print("🔑 Top Keywords:")
        for k in keywords:
            keyword = k.get("keyword", "?")
            freq = k.get("frequency", 0)
            print(f"  • \"{keyword}\" ({freq}x)")
        print("")

    # Display sources
    sources = src_resp.get("sources", [])[:10]
    if sources:
        print("📄 Top Sources:")
        for s in sources:
            url = s.get("url", "?")
            mentions = s.get("mentions", 0)
            own = " ⭐" if s.get("own_company_mentioned") else ""
            print(f"  • {url} ({mentions}x){own}")
        print("")

    # Show balance
    usage_resp, _ = api_call("GET", "/usage", api_key=api_key)
    balance = usage_resp.get("balance", "?")
    print(f"💰 Remaining: {balance} credits")


def cmd_content(_args):
    """Generate blog post from latest analysis."""
    config = require_user_config()
    api_key = config["api_key"]
    site_uuid = config["site_uuid"]

    # Get latest analysis
    resp, status = api_call("GET", f"/sites/{site_uuid}/analysis?limit=1", api_key=api_key)
    if status != 200:
        print(f"Failed to fetch analyses (HTTP {status})", file=sys.stderr)
        sys.exit(1)

    analyses = resp.get("analyses", [])
    if not analyses:
        print("No analysis found. Run /botsee analyze first.", file=sys.stderr)
        sys.exit(1)

    analysis_uuid = analyses[0].get("uuid")

    print("⏳ Generating blog post...")
    resp, status = api_call(
        "POST", f"/analysis/{analysis_uuid}/content",
        data={}, api_key=api_key
    )
    if status not in (200, 201):
        print(f"Content generation failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    content = resp.get("content", "")
    credits_used = resp.get("credits_used", "?")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(content)
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("")
    print(f"💰 Used: {credits_used} credits")

    # Auto-save
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"botsee-{timestamp}.md"
    with open(filename, "w") as f:
        f.write(content)
    print(f"✅ Saved: {filename}")


# --- Sites CRUD ---


def cmd_list_sites(_args):
    """List all sites."""
    config = require_user_config()
    resp, status = api_call("GET", "/sites", api_key=config["api_key"])
    if status != 200:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    sites = resp.get("sites", [])
    if not sites:
        print("No sites found.")
        return

    active_uuid = config.get("site_uuid")

    print(f"Sites ({len(sites)}):")
    for s in sites:
        uuid = s.get("uuid", "?")
        url = s.get("url", "?")
        name = s.get("product_name", "?")
        active_marker = " ⭐" if uuid == active_uuid else ""
        print(f"  {uuid[:8]}... - {url} ({name}){active_marker}")


def cmd_get_site(args):
    """Get a site by UUID."""
    config = require_user_config()
    resp, status = api_call("GET", f"/sites/{args.uuid}", api_key=config["api_key"])
    if status != 200:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    site = resp.get("site", {})
    print(json.dumps(site, indent=2))


def cmd_archive_site(args):
    """Archive (soft-delete) a site."""
    config = require_user_config()
    resp, status = api_call("DELETE", f"/sites/{args.uuid}", api_key=config["api_key"])
    if status == 204:
        print(f"✅ Site {args.uuid} archived")
    else:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)


def cmd_use_site(args):
    """Switch active site."""
    config = require_user_config()
    api_key = config["api_key"]
    site_uuid = args.uuid

    # Verify site exists
    resp, status = api_call("GET", f"/sites/{site_uuid}", api_key=api_key)
    if status != 200:
        print(f"Failed to fetch site (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    site = resp.get("site", {})
    site_url = site.get("url", "?")
    site_name = site.get("product_name", "?")

    # Update config with new active site
    save_user_config(api_key, site_uuid)

    print(f"✅ Active site changed to: {site_name}")
    print(f"   URL: {site_url}")
    print(f"   UUID: {site_uuid}")


# --- Customer Types CRUD ---


def cmd_list_types(args):
    """List customer types for a site."""
    config = require_user_config()
    site_uuid = args.site_uuid or config["site_uuid"]
    resp, status = api_call("GET", f"/sites/{site_uuid}/customer-types", api_key=config["api_key"])
    if status != 200:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    types = resp.get("customer_types", [])
    if not types:
        print("No customer types found.")
        return

    print(f"Customer Types ({len(types)}):")
    for t in types:
        uuid = t.get("uuid", "?")
        name = t.get("name", "?")
        desc = t.get("description", "")[:50]
        print(f"  {uuid[:8]}... - {name}")
        if desc:
            print(f"    {desc}...")


def cmd_get_type(args):
    """Get a customer type by UUID."""
    config = require_user_config()
    resp, status = api_call("GET", f"/customer-types/{args.uuid}", api_key=config["api_key"])
    if status != 200:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    ct = resp.get("customer_type", {})
    print(json.dumps(ct, indent=2))


def cmd_create_type(args):
    """Create a customer type manually (FREE)."""
    config = require_user_config()
    data = {"name": args.name}
    if args.description:
        data["description"] = args.description

    resp, status = api_call(
        "POST", f"/sites/{args.site_uuid}/customer-types",
        data=data, api_key=config["api_key"]
    )
    if status not in (200, 201):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    ct = resp.get("customer_type", {})
    uuid = ct.get("uuid", "?")
    print(f"✅ Customer type created: {uuid}")
    print(json.dumps(ct, indent=2))


def cmd_generate_types(args):
    """AI-generate customer types (5 credits each)."""
    config = require_user_config()
    site_uuid = args.site_uuid or config["site_uuid"]
    resp, status = api_call(
        "POST", f"/sites/{site_uuid}/customer-types/generate",
        data={"count": args.count}, api_key=config["api_key"]
    )
    if status not in (200, 201):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    types = resp.get("customer_types", [])
    print(f"✅ Generated {len(types)} customer type(s)")
    for t in types:
        print(f"  • {t.get('name', '?')}")


def cmd_update_type(args):
    """Update a customer type."""
    config = require_user_config()
    data = {}
    if args.name:
        data["name"] = args.name
    if args.description:
        data["description"] = args.description

    resp, status = api_call(
        "PUT", f"/customer-types/{args.uuid}",
        data=data, api_key=config["api_key"]
    )
    if status not in (200, 204):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Customer type {args.uuid} updated")


def cmd_archive_type(args):
    """Archive a customer type."""
    config = require_user_config()
    resp, status = api_call("DELETE", f"/customer-types/{args.uuid}", api_key=config["api_key"])
    if status == 204:
        print(f"✅ Customer type {args.uuid} archived")
    else:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)


# --- Personas CRUD ---


def cmd_list_personas(args):
    """List personas for a customer type."""
    config = require_user_config()
    resp, status = api_call(
        "GET", f"/customer-types/{args.type_uuid}/personas",
        api_key=config["api_key"]
    )
    if status != 200:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    personas = resp.get("personas", [])
    if not personas:
        print("No personas found.")
        return

    print(f"Personas ({len(personas)}):")
    for p in personas:
        uuid = p.get("uuid", "?")
        name = p.get("name", "?")
        desc = p.get("description", "")[:50]
        print(f"  {uuid[:8]}... - {name}")
        if desc:
            print(f"    {desc}...")


def cmd_get_persona(args):
    """Get a persona by UUID."""
    config = require_user_config()
    resp, status = api_call("GET", f"/personas/{args.uuid}", api_key=config["api_key"])
    if status != 200:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    persona = resp.get("persona", {})
    print(json.dumps(persona, indent=2))


def cmd_create_persona(args):
    """Create a persona manually (FREE)."""
    config = require_user_config()
    data = {"name": args.name}
    if args.description:
        data["description"] = args.description

    resp, status = api_call(
        "POST", f"/customer-types/{args.type_uuid}/personas",
        data=data, api_key=config["api_key"]
    )
    if status not in (200, 201):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    persona = resp.get("persona", {})
    uuid = persona.get("uuid", "?")
    print(f"✅ Persona created: {uuid}")
    print(json.dumps(persona, indent=2))


def cmd_generate_personas(args):
    """AI-generate personas (5 credits each)."""
    config = require_user_config()
    resp, status = api_call(
        "POST", f"/customer-types/{args.type_uuid}/personas/generate",
        data={"count": args.count}, api_key=config["api_key"]
    )
    if status not in (200, 201):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    personas = resp.get("personas", [])
    print(f"✅ Generated {len(personas)} persona(s)")
    for p in personas:
        print(f"  • {p.get('name', '?')}")


def cmd_update_persona(args):
    """Update a persona."""
    config = require_user_config()
    data = {}
    if args.name:
        data["name"] = args.name
    if args.description:
        data["description"] = args.description

    resp, status = api_call(
        "PUT", f"/personas/{args.uuid}",
        data=data, api_key=config["api_key"]
    )
    if status not in (200, 204):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Persona {args.uuid} updated")


def cmd_archive_persona(args):
    """Archive a persona."""
    config = require_user_config()
    resp, status = api_call("DELETE", f"/personas/{args.uuid}", api_key=config["api_key"])
    if status == 204:
        print(f"✅ Persona {args.uuid} archived")
    else:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)


# --- Questions CRUD ---


def cmd_list_questions(args):
    """List questions for a persona."""
    config = require_user_config()
    resp, status = api_call(
        "GET", f"/personas/{args.persona_uuid}/questions",
        api_key=config["api_key"]
    )
    if status != 200:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    questions = resp.get("questions", [])
    if not questions:
        print("No questions found.")
        return

    print(f"Questions ({len(questions)}):")
    for q in questions:
        uuid = q.get("uuid", "?")
        text = q.get("text", "?")[:80]
        print(f"  {uuid[:8]}... - {text}")


def cmd_get_question(args):
    """Get a question by UUID."""
    config = require_user_config()
    resp, status = api_call("GET", f"/questions/{args.uuid}/results", api_key=config["api_key"])
    if status != 200:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    question = resp.get("question", {})
    print(json.dumps(question, indent=2))


def cmd_create_question(args):
    """Create a question manually (FREE)."""
    config = require_user_config()
    data = {"text": args.text}

    resp, status = api_call(
        "POST", f"/personas/{args.persona_uuid}/questions",
        data=data, api_key=config["api_key"]
    )
    if status not in (200, 201):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    question = resp.get("question", {})
    uuid = question.get("uuid", "?")
    print(f"✅ Question created: {uuid}")
    print(json.dumps(question, indent=2))


def cmd_generate_questions(args):
    """AI-generate questions (10 credits flat)."""
    config = require_user_config()
    resp, status = api_call(
        "POST", f"/personas/{args.persona_uuid}/questions/generate",
        data={"count": args.count}, api_key=config["api_key"]
    )
    if status not in (200, 201):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    questions = resp.get("questions", [])
    print(f"✅ Generated {len(questions)} question(s)")
    for q in questions:
        text = q.get("text", "?")[:80]
        print(f"  • {text}")


def cmd_update_question(args):
    """Update a question."""
    config = require_user_config()
    data = {"text": args.text}

    resp, status = api_call(
        "PUT", f"/questions/{args.uuid}",
        data=data, api_key=config["api_key"]
    )
    if status not in (200, 204):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Question {args.uuid} updated")


def cmd_delete_question(args):
    """Delete a question (permanent)."""
    config = require_user_config()
    resp, status = api_call("DELETE", f"/questions/{args.uuid}", api_key=config["api_key"])
    if status == 204:
        print(f"✅ Question {args.uuid} deleted")
    else:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)


# --- Results commands ---


def cmd_results_competitors(args):
    """Get competitors from analysis."""
    config = require_user_config()
    resp, status = api_call(
        "GET", f"/analysis/{args.analysis_uuid}/competitors",
        api_key=config["api_key"]
    )
    if status != 200:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    # Return full response with by_customer_type and overall_summary
    print(json.dumps(resp, indent=2))


def cmd_results_keywords(args):
    """Get keywords from analysis."""
    config = require_user_config()
    resp, status = api_call(
        "GET", f"/analysis/{args.analysis_uuid}/keywords",
        api_key=config["api_key"]
    )
    if status != 200:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    keywords = resp.get("keywords", [])
    print(json.dumps(keywords, indent=2))


def cmd_results_sources(args):
    """Get sources from analysis."""
    config = require_user_config()
    resp, status = api_call(
        "GET", f"/analysis/{args.analysis_uuid}/sources",
        api_key=config["api_key"]
    )
    if status != 200:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    sources = resp.get("sources", [])
    print(json.dumps(sources, indent=2))


def cmd_results_responses(args):
    """Get raw LLM responses from analysis."""
    config = require_user_config()
    resp, status = api_call(
        "GET", f"/analysis/{args.analysis_uuid}/responses",
        api_key=config["api_key"]
    )
    if status != 200:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    responses = resp.get("responses", [])
    print(json.dumps(responses, indent=2))


# --- Main ---


def main():
    parser = argparse.ArgumentParser(
        description="BotSee CLI — AI-powered competitive intelligence"
    )
    subparsers = parser.add_subparsers(dest="command")

    # High-level workflow commands
    subparsers.add_parser("status", help="Show account status and balance")

    signup_parser = subparsers.add_parser("signup", help="Signup for BotSee and get API key")
    signup_parser.add_argument("--api-key", help="Existing API key (skip signup)")
    signup_parser.add_argument("--email", help="Contact email (optional)")
    signup_parser.add_argument("--name", help="Contact name (optional)")
    signup_parser.add_argument("--company", help="Company name (optional)")

    create_site_parser = subparsers.add_parser("create-site", help="Create site and generate content")
    create_site_parser.add_argument("domain", help="Website URL to analyze")
    create_site_parser.add_argument("--types", type=int, default=2, help="Number of customer types (default: 2)")
    create_site_parser.add_argument("--personas", type=int, default=2, help="Personas per customer type (default: 2)")
    create_site_parser.add_argument("--questions", type=int, default=5, help="Questions per persona (default: 5)")

    subparsers.add_parser("config-show", help="Display saved configuration")

    analyze_parser = subparsers.add_parser("analyze", help="Run competitive analysis")
    analyze_parser.add_argument("site_uuid", nargs="?", help="Site UUID (optional, defaults to active site)")

    subparsers.add_parser("content", help="Generate blog post from analysis")

    # Sites CRUD
    subparsers.add_parser("list-sites", help="List all sites")
    get_site_parser = subparsers.add_parser("get-site", help="Get site by UUID")
    get_site_parser.add_argument("uuid", help="Site UUID")

    archive_site_parser = subparsers.add_parser("archive-site", help="Archive a site")
    archive_site_parser.add_argument("uuid", help="Site UUID")

    use_site_parser = subparsers.add_parser("use-site", help="Switch active site")
    use_site_parser.add_argument("uuid", help="Site UUID")

    # Customer Types CRUD
    list_types_parser = subparsers.add_parser("list-types", help="List customer types")
    list_types_parser.add_argument("--site-uuid", help="Site UUID (defaults to config)")

    get_type_parser = subparsers.add_parser("get-type", help="Get customer type by UUID")
    get_type_parser.add_argument("uuid", help="Customer type UUID")

    create_type_parser = subparsers.add_parser("create-type", help="Create customer type (FREE)")
    create_type_parser.add_argument("site_uuid", help="Site UUID")
    create_type_parser.add_argument("--name", required=True, help="Type name")
    create_type_parser.add_argument("--description", help="Type description")

    gen_types_parser = subparsers.add_parser("generate-types", help="AI-generate types (5 credits each)")
    gen_types_parser.add_argument("--site-uuid", help="Site UUID (defaults to config)")
    gen_types_parser.add_argument("--count", type=int, default=2, help="Number to generate")

    update_type_parser = subparsers.add_parser("update-type", help="Update customer type")
    update_type_parser.add_argument("uuid", help="Customer type UUID")
    update_type_parser.add_argument("--name", help="New name")
    update_type_parser.add_argument("--description", help="New description")

    archive_type_parser = subparsers.add_parser("archive-type", help="Archive customer type")
    archive_type_parser.add_argument("uuid", help="Customer type UUID")

    # Personas CRUD
    list_personas_parser = subparsers.add_parser("list-personas", help="List personas for type")
    list_personas_parser.add_argument("type_uuid", help="Customer type UUID")

    get_persona_parser = subparsers.add_parser("get-persona", help="Get persona by UUID")
    get_persona_parser.add_argument("uuid", help="Persona UUID")

    create_persona_parser = subparsers.add_parser("create-persona", help="Create persona (FREE)")
    create_persona_parser.add_argument("type_uuid", help="Customer type UUID")
    create_persona_parser.add_argument("--name", required=True, help="Persona name")
    create_persona_parser.add_argument("--description", help="Persona description")

    gen_personas_parser = subparsers.add_parser("generate-personas", help="AI-generate personas (5 credits each)")
    gen_personas_parser.add_argument("type_uuid", help="Customer type UUID")
    gen_personas_parser.add_argument("--count", type=int, default=2, help="Number to generate")

    update_persona_parser = subparsers.add_parser("update-persona", help="Update persona")
    update_persona_parser.add_argument("uuid", help="Persona UUID")
    update_persona_parser.add_argument("--name", help="New name")
    update_persona_parser.add_argument("--description", help="New description")

    archive_persona_parser = subparsers.add_parser("archive-persona", help="Archive persona")
    archive_persona_parser.add_argument("uuid", help="Persona UUID")

    # Questions CRUD
    list_questions_parser = subparsers.add_parser("list-questions", help="List questions for persona")
    list_questions_parser.add_argument("persona_uuid", help="Persona UUID")

    get_question_parser = subparsers.add_parser("get-question", help="Get question by UUID")
    get_question_parser.add_argument("uuid", help="Question UUID")

    create_question_parser = subparsers.add_parser("create-question", help="Create question (FREE)")
    create_question_parser.add_argument("persona_uuid", help="Persona UUID")
    create_question_parser.add_argument("--text", required=True, help="Question text")

    gen_questions_parser = subparsers.add_parser("generate-questions", help="AI-generate questions (10 credits)")
    gen_questions_parser.add_argument("persona_uuid", help="Persona UUID")
    gen_questions_parser.add_argument("--count", type=int, default=5, help="Number to generate")

    update_question_parser = subparsers.add_parser("update-question", help="Update question")
    update_question_parser.add_argument("uuid", help="Question UUID")
    update_question_parser.add_argument("--text", required=True, help="New question text")

    delete_question_parser = subparsers.add_parser("delete-question", help="Delete question (permanent)")
    delete_question_parser.add_argument("uuid", help="Question UUID")

    # Results commands
    results_comp_parser = subparsers.add_parser("results-competitors", help="Get competitors")
    results_comp_parser.add_argument("analysis_uuid", help="Analysis UUID")

    results_kw_parser = subparsers.add_parser("results-keywords", help="Get keywords")
    results_kw_parser.add_argument("analysis_uuid", help="Analysis UUID")

    results_src_parser = subparsers.add_parser("results-sources", help="Get sources")
    results_src_parser.add_argument("analysis_uuid", help="Analysis UUID")

    results_resp_parser = subparsers.add_parser("results-responses", help="Get raw responses")
    results_resp_parser.add_argument("analysis_uuid", help="Analysis UUID")

    args = parser.parse_args()

    commands = {
        "status": cmd_status,
        "signup": cmd_signup,
        "create-site": cmd_create_site,
        "config-show": cmd_config_show,
        "analyze": cmd_analyze,
        "content": cmd_content,
        "list-sites": cmd_list_sites,
        "get-site": cmd_get_site,
        "archive-site": cmd_archive_site,
        "use-site": cmd_use_site,
        "list-types": cmd_list_types,
        "get-type": cmd_get_type,
        "create-type": cmd_create_type,
        "generate-types": cmd_generate_types,
        "update-type": cmd_update_type,
        "archive-type": cmd_archive_type,
        "list-personas": cmd_list_personas,
        "get-persona": cmd_get_persona,
        "create-persona": cmd_create_persona,
        "generate-personas": cmd_generate_personas,
        "update-persona": cmd_update_persona,
        "archive-persona": cmd_archive_persona,
        "list-questions": cmd_list_questions,
        "get-question": cmd_get_question,
        "create-question": cmd_create_question,
        "generate-questions": cmd_generate_questions,
        "update-question": cmd_update_question,
        "delete-question": cmd_delete_question,
        "results-competitors": cmd_results_competitors,
        "results-keywords": cmd_results_keywords,
        "results-sources": cmd_results_sources,
        "results-responses": cmd_results_responses,
    }

    if args.command is None:
        cmd_status(args)
    elif args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
