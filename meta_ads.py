"""Meta Ads API client using the Graph API."""
import os
import requests


GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


class MetaAdsClient:
    def __init__(self):
        self.access_token = os.environ["META_ACCESS_TOKEN"]
        self.app_id = os.environ["META_APP_ID"]
        self.app_secret = os.environ["META_APP_SECRET"]

    def _get(self, path: str, params: dict = None) -> dict:
        params = params or {}
        params["access_token"] = self.access_token
        resp = requests.get(f"{GRAPH_API_BASE}/{path}", params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_ad_accounts(self) -> list[dict]:
        data = self._get("me/adaccounts", {"fields": "id,name,currency,account_status,balance"})
        return data.get("data", [])

    def get_campaigns(self, account_id: str) -> list[dict]:
        data = self._get(
            f"{account_id}/campaigns",
            {"fields": "id,name,status,objective,daily_budget,lifetime_budget,start_time,stop_time"},
        )
        return data.get("data", [])

    def get_campaign_insights(self, campaign_id: str, date_preset: str = "last_30d") -> dict:
        data = self._get(
            f"{campaign_id}/insights",
            {
                "fields": "impressions,clicks,spend,ctr,cpm,cpc,reach,frequency,actions",
                "date_preset": date_preset,
            },
        )
        return data.get("data", [{}])[0] if data.get("data") else {}

    def get_adsets(self, campaign_id: str) -> list[dict]:
        data = self._get(
            f"{campaign_id}/adsets",
            {"fields": "id,name,status,daily_budget,lifetime_budget,targeting,optimization_goal,billing_event"},
        )
        return data.get("data", [])

    def get_ads(self, adset_id: str) -> list[dict]:
        data = self._get(
            f"{adset_id}/ads",
            {"fields": "id,name,status,creative{title,body,image_url}"},
        )
        return data.get("data", [])

    def get_account_insights(self, account_id: str, date_preset: str = "last_30d") -> dict:
        data = self._get(
            f"{account_id}/insights",
            {
                "fields": "impressions,clicks,spend,ctr,cpm,cpc,reach,frequency,actions,account_name",
                "date_preset": date_preset,
            },
        )
        return data.get("data", [{}])[0] if data.get("data") else {}

    def update_campaign_status(self, campaign_id: str, status: str) -> dict:
        """status: ACTIVE or PAUSED"""
        resp = requests.post(
            f"{GRAPH_API_BASE}/{campaign_id}",
            data={"status": status, "access_token": self.access_token},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def update_campaign_budget(self, campaign_id: str, daily_budget: int | None = None, lifetime_budget: int | None = None) -> dict:
        """Budgets in cents (e.g. 1000 = $10.00)."""
        payload: dict = {"access_token": self.access_token}
        if daily_budget is not None:
            payload["daily_budget"] = str(daily_budget)
        if lifetime_budget is not None:
            payload["lifetime_budget"] = str(lifetime_budget)
        resp = requests.post(f"{GRAPH_API_BASE}/{campaign_id}", data=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
