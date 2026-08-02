import json
import urllib.request
import os
import sys

# Read Gemini response
with open('/tmp/ai-response.json') as f:
    data = json.load(f)

# Extract AI text
if 'candidates' in data:
    ai_text = data['candidates'][0]['content']['parts'][0]['text']
elif 'error' in data:
    ai_text = f"Gemini Error: {data['error'].get('message', 'Unknown')}"
else:
    ai_text = f"Unexpected response: {json.dumps(data)}"

# Get environment variables
app_name = os.environ.get('APP_NAME', 'unknown')
sha = os.environ.get('SHA', 'unknown')
repo = os.environ.get('REPO', 'unknown')
token = os.environ.get('GITHUB_TOKEN_VAL', '')

print(f"Posting AI analysis for {app_name}...")
print(f"AI Text: {ai_text[:100]}...")

# Build comment body
body = f"""## 🤖 AI Pipeline Failure Analysis

{ai_text}

---
> **App:** {app_name}
> **Commit:** {sha}
> *Analyzed by Google Gemini 2.5 Flash* 🤖"""

# Post to GitHub
payload = json.dumps({"body": body}).encode('utf-8')

req = urllib.request.Request(
    f"https://api.github.com/repos/{repo}/commits/{sha}/comments",
    data=payload,
    headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req) as r:
        print(f"Comment posted! Status: {r.status}")
except Exception as e:
    print(f"Error posting comment: {str(e)}")
    sys.exit(1)