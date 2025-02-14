import json
import requests
import os
from flask import Flask, request

app = Flask(__name__)

# Get Discord Webhook URL from Render Environment Variables
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

@app.route("/")
def home():
    return "Flask GitHub Webhook is running!", 200

@app.route("/github", methods=["POST"])
def github_webhook():
    data = request.json

    if "commits" in data:
        repo_name = data["repository"]["name"]
        commit_messages = "\n".join([f"- {commit['message']} by {commit['author']['name']}" for commit in data["commits"]])
        message = f"New commits pushed to **{repo_name}**:\n{commit_messages}"

        # Send message to Discord
        requests.post(DISCORD_WEBHOOK, json={"content": message})

    return "", 204  # Respond with no content (success)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Render assigns a dynamic port
    app.run(host="0.0.0.0", port=port)
