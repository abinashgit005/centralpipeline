import json
import os
import sys
import urllib.request

MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")


def extract_text(data):
    """Pull the answer text out of a Gemini response, or describe what went wrong."""
    if "error" in data:
        return f"Gemini Error: {data['error'].get('message', 'Unknown')}"

    candidates = data.get("candidates") or []
    if not candidates:
        feedback = data.get("promptFeedback", {})
        return f"Gemini returned no answer. {json.dumps(feedback) if feedback else json.dumps(data)[:500]}"

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "\n".join(p["text"] for p in parts if "text" in p and not p.get("thought"))
    if text.strip():
        return text

    reason = candidates[0].get("finishReason", "UNKNOWN")
    return f"Gemini returned an empty answer (finish reason: {reason})."


# Read Gemini response
try:
    with open("/tmp/ai-response.json") as f:
        data = json.load(f)
    ai_text = extract_text(data)
except (OSError, json.JSONDecodeError) as e:
    ai_text = f"Could not read the Gemini response: {e}"

# Environment variables
app_name = os.environ.get("APP_NAME", "unknown")
sha = os.environ.get("SHA", "unknown")
repo = os.environ.get("REPO", "unknown")
token = os.environ.get("GITHUB_TOKEN_VAL", "")

print(f"Posting AI analysis for {app_name}...")
print(f"AI Text: {ai_text[:100]}...")

body = f"""## 🤖 AI Pipeline Failure Analysis

{ai_text}

---
> **App:** {app_name}
> **Commit:** {sha}
> *Analyzed by Google Gemini ({MODEL})* 🤖"""

# GitHub comments are limited to 65536 characters
body = body[:60000]

payload = json.dumps({"body": body}).encode("utf-8")
req = urllib.request.Request(
    f"https://api.github.com/repos/{repo}/commits/{sha}/comments",
    data=payload,
    headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req) as r:
        print(f"Comment posted! Status: {r.status}")
except Exception as e:
    print(f"Error posting comment: {e}")
    sys.exit(1)