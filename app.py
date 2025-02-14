import json
import requests
import os
from flask import Flask, request

app = Flask(__name__)

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

@app.route("/")
def home():
    return "PacketNodes GitHub Webhook is running!", 200

@app.route("/github", methods=["POST"])
def github_webhook():
    data = request.json

    if "commits" in data:
        repo_name = data["repository"]["name"]
        repo_url = data["repository"]["html_url"]
        pusher = data["pusher"]["name"]
        avatar_url = data["sender"]["avatar_url"]

        embed = {
            "title": f"🚀 New Push to {repo_name}",
            "url": repo_url,
            "color": 0x57F287,
            "fields": [],
            "footer": {
                "text": f"Powered by PacketNodes | Commit pushed by {pusher}",
                "icon_url": avatar_url
            },
            "timestamp": data["repository"]["updated_at"],
            "author": {
                "name": "PacketNodes Webhook Service",
                "icon_url": avatar_url
            }
        }

        for commit in data["commits"]:
            commit_msg = commit["message"]
            commit_author = commit["author"]["name"]
            commit_url = commit["url"]

            embed["fields"].append({
                "name": f"📝 {commit_author}",
                "value": f"[{commit_msg}]({commit_url})",
                "inline": False
            })

        payload = {"embeds": [embed]}

        requests.post(DISCORD_WEBHOOK, json=payload)

    return "", 204

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
