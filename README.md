# Meta Ads WhatsApp Bot

A WhatsApp bot powered by Claude that lets you manage Meta (Facebook/Instagram) ad campaigns via chat. Deploy on Railway.

## Features

- View all ad accounts, campaigns, and performance metrics
- Pause / resume campaigns
- Update daily or lifetime budgets
- Search campaigns by name
- Responds in Arabic or English
- Secured to your WhatsApp number only

## Environment Variables

| Variable | Description |
|----------|-------------|
| `META_ACCESS_TOKEN` | Meta Ads Graph API access token |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `WHATSAPP_TOKEN` | WhatsApp Business API token |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp phone number ID |
| `WEBHOOK_VERIFY_TOKEN` | Any secret string for webhook verification |
| `ALLOWED_WHATSAPP_NUMBER` | Your WhatsApp number (e.g. 201012345678) |

## Deploy on Railway

1. Push this repo to GitHub
2. Create a new Railway project from the repo
3. Set all environment variables above
4. Railway will build and deploy automatically
5. Set the webhook URL in Meta App Dashboard: `https://your-app.railway.app/webhook`

## Ad Accounts

15 accounts pre-configured in `tools.py` (Limitless, Eva Pharma, Bellcom, Eva Senses, TC Eva, Eva Fluoro, Eva One Cream, Grounds 2, Dopay, Teem App, Eman Hylooz, Verve, Grounds, Now SA, Axelerate).

## Example WhatsApp Messages

- "show me eva pharma campaigns"
- "what's the spend on limitless this month?"
- "pause campaign 120200xxx"
- "set dopay daily budget to 500 EGP"
- "اعرض حملات grounds"
