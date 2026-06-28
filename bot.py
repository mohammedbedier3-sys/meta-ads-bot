"""Meta Ads AI Bot — conversational interface powered by Claude."""
import json
import os
import sys

import anthropic
from dotenv import load_dotenv

from meta_ads import MetaAdsClient

load_dotenv()

SYSTEM_PROMPT = """You are an expert Meta Ads (Facebook & Instagram Ads) analyst and media buyer assistant.
You have access to the user's live Meta Ads data via tool calls.
Help users understand their campaign performance, diagnose issues, suggest optimizations, and take actions.

When analyzing data:
- Highlight top and bottom performers
- Flag unusual metrics (very high CPM, low CTR, high frequency)
- Give concrete, actionable recommendations
- Be concise and direct

When taking actions (pausing, enabling, budget changes), always confirm with the user first unless they explicitly ask you to proceed."""

TOOLS = [
    {
        "name": "get_ad_accounts",
        "description": "List all Meta Ads accounts the user has access to.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_campaigns",
        "description": "List campaigns for an ad account.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string", "description": "Ad account ID, e.g. act_123456789"}
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "get_account_insights",
        "description": "Get overall performance metrics for an ad account.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string"},
                "date_preset": {
                    "type": "string",
                    "description": "One of: today, yesterday, last_7d, last_14d, last_30d, this_month, last_month",
                    "default": "last_30d",
                },
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "get_campaign_insights",
        "description": "Get performance metrics for a specific campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string"},
                "date_preset": {"type": "string", "default": "last_30d"},
            },
            "required": ["campaign_id"],
        },
    },
    {
        "name": "get_adsets",
        "description": "List ad sets within a campaign.",
        "input_schema": {
            "type": "object",
            "properties": {"campaign_id": {"type": "string"}},
            "required": ["campaign_id"],
        },
    },
    {
        "name": "get_ads",
        "description": "List ads within an ad set.",
        "input_schema": {
            "type": "object",
            "properties": {"adset_id": {"type": "string"}},
            "required": ["adset_id"],
        },
    },
    {
        "name": "update_campaign_status",
        "description": "Pause or enable a campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string"},
                "status": {"type": "string", "enum": ["ACTIVE", "PAUSED"]},
            },
            "required": ["campaign_id", "status"],
        },
    },
    {
        "name": "update_campaign_budget",
        "description": "Update daily or lifetime budget for a campaign. Amounts are in cents (e.g. 1000 = $10.00).",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string"},
                "daily_budget": {"type": "integer", "description": "Daily budget in cents"},
                "lifetime_budget": {"type": "integer", "description": "Lifetime budget in cents"},
            },
            "required": ["campaign_id"],
        },
    },
]


def run_tool(client: MetaAdsClient, name: str, inputs: dict) -> str:
    try:
        if name == "get_ad_accounts":
            result = client.get_ad_accounts()
        elif name == "get_campaigns":
            result = client.get_campaigns(inputs["account_id"])
        elif name == "get_account_insights":
            result = client.get_account_insights(inputs["account_id"], inputs.get("date_preset", "last_30d"))
        elif name == "get_campaign_insights":
            result = client.get_campaign_insights(inputs["campaign_id"], inputs.get("date_preset", "last_30d"))
        elif name == "get_adsets":
            result = client.get_adsets(inputs["campaign_id"])
        elif name == "get_ads":
            result = client.get_ads(inputs["adset_id"])
        elif name == "update_campaign_status":
            result = client.update_campaign_status(inputs["campaign_id"], inputs["status"])
        elif name == "update_campaign_budget":
            result = client.update_campaign_budget(
                inputs["campaign_id"],
                inputs.get("daily_budget"),
                inputs.get("lifetime_budget"),
            )
        else:
            return json.dumps({"error": f"Unknown tool: {name}"})
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def chat(meta_client: MetaAdsClient, claude: anthropic.Anthropic) -> None:
    messages: list[dict] = []
    print("\nMeta Ads AI Bot ready. Type your question or 'quit' to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        while True:
            response = claude.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )

            assistant_content = response.content
            messages.append({"role": "assistant", "content": assistant_content})

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in assistant_content:
                    if block.type == "tool_use":
                        print(f"  [calling {block.name}...]")
                        result = run_tool(meta_client, block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                messages.append({"role": "user", "content": tool_results})
            else:
                for block in assistant_content:
                    if hasattr(block, "text"):
                        print(f"\nAssistant: {block.text}\n")
                break


def main() -> None:
    missing = [v for v in ("META_ACCESS_TOKEN", "META_APP_ID", "META_APP_SECRET", "ANTHROPIC_API_KEY") if not os.environ.get(v)]
    if missing:
        print(f"Missing environment variables: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in the values.")
        sys.exit(1)

    meta_client = MetaAdsClient()
    claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    chat(meta_client, claude)


if __name__ == "__main__":
    main()
