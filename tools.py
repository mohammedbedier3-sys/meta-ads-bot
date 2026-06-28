import os
import requests

BASE = "https://graph.facebook.com/v21.0"
TOKEN = os.environ["META_ACCESS_TOKEN"]

ACCOUNTS = {
    "limitless": "act_708854762907241",
    "eva pharma": "act_578700929644364",
    "bellcom": "act_1298995850226988",
    "eva senses": "act_1166696971605528",
    "tc eva": "act_1372297597555728",
    "eva fluoro": "act_1841211936672935",
    "eva one cream": "act_4010511402522996",
    "grounds 2": "act_1230364168393003",
    "dopay": "act_423430391719130",
    "teem app": "act_595668430075029",
    "eman hylooz": "act_247300704",
    "verve": "act_934365664270732",
    "grounds": "act_738703538422919",
    "now sa": "act_1513731155969594",
    "axelerate": "act_471077809386572",
}


def _get(path, params=None):
    params = params or {}
    params["access_token"] = TOKEN
    r = requests.get(f"{BASE}{path}", params=params)
    return r.json()


def _post(path, data=None):
    data = data or {}
    data["access_token"] = TOKEN
    r = requests.post(f"{BASE}{path}", data=data)
    return r.json()


def list_accounts() -> dict:
    """List all accessible ad accounts with status and balance."""
    return _get("/me/adaccounts", {
        "fields": "id,name,account_status,currency,balance,amount_spent"
    })


def get_campaigns(account_id: str) -> dict:
    """Get all active and paused campaigns for an account."""
    return _get(f"/{account_id}/campaigns", {
        "fields": "id,name,status,objective,daily_budget,lifetime_budget",
        "effective_status": "['ACTIVE','PAUSED']",
        "limit": 50,
    })


def get_campaign_insights(campaign_id: str, date_preset: str = "last_7d") -> dict:
    """Get performance metrics for a campaign. date_preset options: today, yesterday, last_7d, last_30d, this_month."""
    return _get(f"/{campaign_id}/insights", {
        "fields": "campaign_name,spend,impressions,reach,clicks,ctr,cpc,cpm,actions,cost_per_action_type",
        "date_preset": date_preset,
    })


def get_account_insights(account_id: str, date_preset: str = "last_7d") -> dict:
    """Get overall account performance metrics."""
    return _get(f"/{account_id}/insights", {
        "fields": "spend,impressions,reach,clicks,ctr,cpc,cpm,actions,cost_per_action_type",
        "date_preset": date_preset,
        "level": "account",
    })


def pause_campaign(campaign_id: str) -> dict:
    """Pause an active campaign."""
    return _post(f"/{campaign_id}", {"status": "PAUSED"})


def resume_campaign(campaign_id: str) -> dict:
    """Resume a paused campaign."""
    return _post(f"/{campaign_id}", {"status": "ACTIVE"})


def update_daily_budget(campaign_id: str, daily_budget_egp: float) -> dict:
    """Update a campaign's daily budget. Amount in EGP (will be converted to piasters)."""
    budget_piasters = int(daily_budget_egp * 100)
    return _post(f"/{campaign_id}", {"daily_budget": budget_piasters})


def update_lifetime_budget(campaign_id: str, lifetime_budget_egp: float) -> dict:
    """Update a campaign's lifetime budget. Amount in EGP."""
    budget_piasters = int(lifetime_budget_egp * 100)
    return _post(f"/{campaign_id}", {"lifetime_budget": budget_piasters})


def search_campaign_by_name(account_id: str, name_fragment: str) -> dict:
    """Search campaigns in an account by partial name match."""
    result = get_campaigns(account_id)
    if "data" not in result:
        return result
    name_lower = name_fragment.lower()
    matches = [c for c in result["data"] if name_lower in c["name"].lower()]
    return {"data": matches}


# Tool definitions for Claude API
TOOL_DEFINITIONS = [
    {
        "name": "list_accounts",
        "description": "List all accessible Meta ad accounts with their status, balance, and currency.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_campaigns",
        "description": "Get all active and paused campaigns for a given ad account.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "The ad account ID (e.g. act_708854762907241). Known accounts: " + str(ACCOUNTS),
                }
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "get_campaign_insights",
        "description": "Get performance metrics (spend, clicks, CTR, CPC, conversions) for a specific campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string", "description": "Campaign ID"},
                "date_preset": {
                    "type": "string",
                    "enum": ["today", "yesterday", "last_7d", "last_14d", "last_30d", "this_month", "last_month"],
                    "description": "Date range for insights",
                },
            },
            "required": ["campaign_id"],
        },
    },
    {
        "name": "get_account_insights",
        "description": "Get overall performance metrics for a Meta ad account.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string", "description": "Ad account ID"},
                "date_preset": {
                    "type": "string",
                    "enum": ["today", "yesterday", "last_7d", "last_14d", "last_30d", "this_month", "last_month"],
                    "description": "Date range for insights",
                },
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "pause_campaign",
        "description": "Pause an active campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string", "description": "Campaign ID to pause"}
            },
            "required": ["campaign_id"],
        },
    },
    {
        "name": "resume_campaign",
        "description": "Resume a paused campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string", "description": "Campaign ID to resume"}
            },
            "required": ["campaign_id"],
        },
    },
    {
        "name": "update_daily_budget",
        "description": "Update a campaign's daily budget.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string", "description": "Campaign ID"},
                "daily_budget_egp": {"type": "number", "description": "New daily budget in EGP"},
            },
            "required": ["campaign_id", "daily_budget_egp"],
        },
    },
    {
        "name": "update_lifetime_budget",
        "description": "Update a campaign's lifetime budget.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string", "description": "Campaign ID"},
                "lifetime_budget_egp": {"type": "number", "description": "New lifetime budget in EGP"},
            },
            "required": ["campaign_id", "lifetime_budget_egp"],
        },
    },
    {
        "name": "search_campaign_by_name",
        "description": "Search for campaigns in an account by partial name. Use this when the user mentions a campaign name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string", "description": "Ad account ID to search in"},
                "name_fragment": {"type": "string", "description": "Partial campaign name to search for"},
            },
            "required": ["account_id", "name_fragment"],
        },
    },
]


def execute_tool(name: str, inputs: dict):
    fn_map = {
        "list_accounts": list_accounts,
        "get_campaigns": get_campaigns,
        "get_campaign_insights": get_campaign_insights,
        "get_account_insights": get_account_insights,
        "pause_campaign": pause_campaign,
        "resume_campaign": resume_campaign,
        "update_daily_budget": update_daily_budget,
        "update_lifetime_budget": update_lifetime_budget,
        "search_campaign_by_name": search_campaign_by_name,
    }
    if name not in fn_map:
        return {"error": f"Unknown tool: {name}"}
    return fn_map[name](**inputs)
