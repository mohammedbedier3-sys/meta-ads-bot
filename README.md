# Meta Ads AI Bot

A conversational AI bot that connects your Meta Ads (Facebook & Instagram) account to Claude, giving you an intelligent analyst for your campaigns.

## What it does

- Fetches live campaign data from the Meta Ads Graph API
- Lets you ask natural-language questions about your campaigns
- Provides performance analysis, optimization recommendations, and anomaly detection
- Can take actions: pause/enable campaigns, update budgets

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure credentials** — copy `.env.example` to `.env` and fill in:
   - `META_APP_ID`, `META_APP_SECRET`, `META_ACCESS_TOKEN` — from your Meta App dashboard
   - `ANTHROPIC_API_KEY` — from [console.anthropic.com](https://console.anthropic.com)

3. **Run**
   ```bash
   python bot.py
   ```

## Example questions

- "Show me all my ad accounts"
- "How are my campaigns performing this month?"
- "Which campaign has the highest CPC?"
- "Pause campaign 120200..."
- "What's my total spend last 7 days?"

## Files

| File | Purpose |
|------|---------|
| `bot.py` | Main conversational bot with Claude tool-use loop |
| `meta_ads.py` | Meta Graph API client |
| `requirements.txt` | Python dependencies |
| `.env` | Your credentials (not committed) |
