import json
import requests
import os
import sys
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
    
    print(f"GitHub Webhook Received: {json.dumps(data, indent=4)}", file=sys.stderr)

    if not data:
        return "Invalid JSON", 400

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

    else:
        return "Event not supported", 204

    requests.post(DISCORD_WEBHOOK, json={"embeds": [embed]})
    return "", 204

@app.route("/hetrixtools", methods=["POST"])
def hetrixtools_webhook():
    data = request.json

    print(f"HetrixTools Webhook Received: {json.dumps(data, indent=4)}", file=sys.stderr)

    if not data:
        return "Invalid JSON", 400

    if "monitor_name" not in data or "monitor_status" not in data:
        print("Missing required fields", file=sys.stderr)
        return "Missing required fields", 400

    color = 0x2ECC71 if data["monitor_status"].lower() == "online" else 0xE74C3C
    status_emoji = "✅" if data["monitor_status"].lower() == "online" else "❌"

    embed = {
        "title": f"{status_emoji} {data['monitor_name']} is now {data['monitor_status'].upper()}",
        "color": color,
        "fields": [
            {"name": "Monitor Type", "value": data.get("monitor_type", "Unknown"), "inline": True},
            {"name": "Category", "value": data.get("monitor_category", "N/A"), "inline": True},
            {"name": "Target", "value": data["monitor_target"], "inline": False}
        ],
        "footer": {"text": "Powered by PacketNodes | HetrixTools Monitoring"},
        "timestamp": str(data.get("timestamp", ""))
    }

    if data["monitor_status"].lower() == "offline" and "monitor_errors" in data:
        error_details = "\n".join([f"**{loc}**: {msg}" for loc, msg in data["monitor_errors"].items()])
        embed["fields"].append({"name": "Error Details", "value": error_details, "inline": False})

    response = requests.post(DISCORD_WEBHOOK, json={"embeds": [embed]})
    print(f"Discord Response: {response.status_code} {response.text}", file=sys.stderr)

    return "", 204

@app.route("/hetrixtools/resource", methods=["POST"])
def hetrixtools_resource_webhook():
    data = request.json

    print(f"HetrixTools Resource Webhook Received: {json.dumps(data, indent=4)}", file=sys.stderr)

    if not data:
        return "Invalid JSON", 400

    if "ServerLabel" not in data or "AlertStatus" not in data:
        print("Missing required fields", file=sys.stderr)
        return "Missing required fields", 400

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
            {"name": "Timestamp", "value": str(data.get("Timestamp", "N/A")), "inline": False}
        ],
        "footer": {"text": "Powered by PacketNodes | HetrixTools Resource Monitoring"}
    }

    response = requests.post(DISCORD_WEBHOOK, json={"embeds": [embed]})
    print(f"Discord Response: {response.status_code} {response.text}", file=sys.stderr)

    return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
