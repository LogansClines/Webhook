import json
import requests
from flask import Flask, request

app = Flask(__name__)

# Replace with your Discord Webhook URL
DISCORD_WEBHOOK = "YOUR_DISCORD_WEBHOOK_URL"

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
    app.run(port=5000)
