import os
import json
import requests
import anthropic
from fastapi import FastAPI, Request, Response
from tools import TOOL_DEFINITIONS, execute_tool, ACCOUNTS

app = FastAPI()

WHATSAPP_TOKEN = os.environ["WHATSAPP_TOKEN"]
VERIFY_TOKEN = os.environ["WEBHOOK_VERIFY_TOKEN"]
PHONE_NUMBER_ID = os.environ["WHATSAPP_PHONE_NUMBER_ID"]
ALLOWED_NUMBER = os.environ.get("ALLOWED_WHATSAPP_NUMBER", "")  # your personal number

claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """You are an AI media buying assistant for Mohammed Bedier. You manage Meta (Facebook) ad campaigns across multiple client accounts.

You have tools to:
- List ad accounts
- View and search campaigns
- Get performance insights (spend, clicks, CTR, CPC, conversions)
- Pause / resume campaigns
- Update daily or lifetime budgets

Key account shortcuts (user may refer to these by short name):
""" + "\n".join(f"- {name}: {id}" for name, id in ACCOUNTS.items()) + """

Rules:
- Always confirm destructive actions (pause, budget change) before executing UNLESS the user says "confirm" or "yes do it"
- When showing numbers: format budgets in EGP with commas, show spend in the account's currency
- Be concise — this is a WhatsApp chat, keep replies short and clear
- If unsure which campaign the user means, list matching options and ask them to confirm
- Respond in the same language the user writes in (Arabic or English)"""


def send_whatsapp_message(to: str, text: str):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    requests.post(url, headers=headers, json=payload)


def run_claude(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "Done."

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return "Something went wrong. Please try again."


@app.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    if params.get("hub.verify_token") == VERIFY_TOKEN and params.get("hub.mode") == "subscribe":
        return Response(content=params["hub.challenge"], media_type="text/plain")
    return Response(status_code=403)


@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()
    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" not in value:
            return {"status": "ok"}

        msg = value["messages"][0]
        sender = msg["from"]

        # Security: only respond to your own number
        if ALLOWED_NUMBER and sender != ALLOWED_NUMBER:
            return {"status": "ignored"}

        if msg["type"] != "text":
            send_whatsapp_message(sender, "Please send text messages only.")
            return {"status": "ok"}

        user_text = msg["text"]["body"]
        reply = run_claude(user_text)
        send_whatsapp_message(sender, reply)

    except (KeyError, IndexError):
        pass

    return {"status": "ok"}


@app.get("/")
async def health():
    return {"status": "running", "bot": "Meta Media Buyer"}
