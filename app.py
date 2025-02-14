import json
import requests
import os
from flask import Flask, request

app = Flask(__name__)

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

@app.route("/")
def home():
    return "PacketNodes Webhook Service is running!", 200

@app.route("/github", methods=["POST"])
def github_webhook():
    data = request.json
    event_type = request.headers.get("X-GitHub-Event")

    repo_name = data["repository"]["name"]
    repo_url = data["repository"]["html_url"]
    sender = data["sender"]["login"]

    embed = {
        "footer": {"text": f"Powered by PacketNodes | Event by {sender}"},
        "author": {"name": "PacketNodes GitHub Webhook"}
    }

    if event_type == "push":
        embed["title"] = f"🚀 New Push to {repo_name}"
        embed["url"] = repo_url
        embed["color"] = 0x57F287
        embed["fields"] = []
        for commit in data["commits"]:
            embed["fields"].append({
                "name": f"📝 {commit['author']['name']}",
                "value": f"[{commit['message']}]({commit['url']})",
                "inline": False
            })

    elif event_type == "issues":
        issue = data["issue"]
        embed["title"] = f"📌 Issue {data['action']} in {repo_name}"
        embed["url"] = issue["html_url"]
        embed["color"] = 0xF1C40F
        embed["fields"] = [{"name": "Issue", "value": f"[{issue['title']}]({issue['html_url']})", "inline": False}]

    elif event_type == "pull_request":
        pr = data["pull_request"]
        embed["title"] = f"🔀 Pull Request {data['action']} in {repo_name}"
        embed["url"] = pr["html_url"]
        embed["color"] = 0x3498DB
        embed["fields"] = [{"name": "Pull Request", "value": f"[{pr['title']}]({pr['html_url']})", "inline": False}]

    elif event_type == "release":
        release = data["release"]
        embed["title"] = f"📦 New Release: {release['tag_name']} in {repo_name}"
        embed["url"] = release["html_url"]
        embed["color"] = 0x9B59B6
        embed["fields"] = [{"name": "Release Notes", "value": release["body"] or "No description provided.", "inline": False}]

    else:
        return "", 204

    requests.post(DISCORD_WEBHOOK, json={"embeds": [embed]})
    return "", 204

@app.route("/hetrixtools", methods=["POST"])
def hetrixtools_webhook():
    data = request.json

    if data.get("MonitorName") and data.get("MonitorStatus"):
        color = 0x2ECC71 if data["MonitorStatus"].lower() == "up" else 0xE74C3C
        status_emoji = "✅" if data["MonitorStatus"].lower() == "up" else "❌"

        embed = {
            "title": f"{status_emoji} {data['MonitorName']} is now {data['MonitorStatus'].upper()}",
            "color": color,
            "fields": [
                {"name": "Monitor Type", "value": data.get("MonitorType", "Unknown"), "inline": True},
                {"name": "Uptime", "value": f"{data.get('Uptime', 'N/A')}%", "inline": True}
            ],
            "footer": {"text": "Powered by PacketNodes | HetrixTools Monitoring"},
            "timestamp": data.get("Timestamp", "")
        }

        requests.post(DISCORD_WEBHOOK, json={"embeds": [embed]})

    return "", 204

@app.route("/hetrixtools/resource", methods=["POST"])
def hetrixtools_resource_webhook():
    data = request.json

    if data.get("ServerLabel") and data.get("AlertStatus"):
        color = 0xE74C3C if data["AlertStatus"].lower() == "critical" else 0xF39C12

        embed = {
            "title": f"⚠️ {data['ServerLabel']} Resource Alert",
            "color": color,
            "fields": [
                {"name": "Status", "value": data["AlertStatus"].capitalize(), "inline": True},
                {"name": "CPU Usage", "value": f"{data.get('CPU', 'N/A')}%", "inline": True},
                {"name": "RAM Usage", "value": f"{data.get('RAM', 'N/A')}%", "inline": True},
                {"name": "Swap Usage", "value": f"{data.get('Swap', 'N/A')}%", "inline": True},
                {"name": "Disk Usage", "value": f"{data.get('Disk', 'N/A')}%", "inline": True},
                {"name": "Timestamp", "value": data.get("Timestamp", "N/A"), "inline": False}
            ],
            "footer": {"text": "Powered by PacketNodes | HetrixTools Resource Monitoring"}
        }

        requests.post(DISCORD_WEBHOOK, json={"embeds": [embed]})

    return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
