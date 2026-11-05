#!/usr/bin/env python3
"""Switch Facebook/Instagram policy every 40 minutes; other rules unchanged."""
import base64
import datetime as dt
import json
import os
import urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "MartinezHustle-Os/Baby-VPN")
BRANCH = "main"
PATH = "USABL.conf"
TOKEN = os.environ["GITHUB_TOKEN"]

# UTC and China Standard Time (UTC+8) have the same 80-minute phase:
# 00:00-00:39 allow; 00:40-01:19 block; repeat every 80 minutes.
utc = dt.datetime.now(dt.timezone.utc)
minute_of_day = utc.hour * 60 + utc.minute
allow = (minute_of_day % 80) < 40
target = "PROXY" if allow else "REJECT"

DOMAINS = (
    "cdninstagram.com", "facebook.com", "facebook.net",
    "fb.com", "fb.me", "fbcdn.net", "fbsbx.com",
    "ig.me", "instagram.com", "m.me",
    "messenger.com", "messengerkids.com",
)
KEYWORDS = ("facebook", "instagram")

def request(method, body=None):
    url = "https://api.github.com/repos/" + REPO + "/contents/" + PATH
    if method == "GET":
        url += "?ref=" + BRANCH
    headers = {
        "Authorization": "Bearer " + TOKEN,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Baby-VPN-social-schedule",
    }
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.loads(resp.read())

data = request("GET")
original = base64.b64decode(data["content"]).decode("utf-8")
old_lines = original.splitlines(keepends=True)
updated_lines = []
count = 0
for line in old_lines:
    stripped = line.rstrip("\r\n")
    ending = line[len(stripped):]
    pieces = stripped.split(",")
    if len(pieces) == 3 and (
        (pieces[0] == "DOMAIN-SUFFIX" and pieces[1] in DOMAINS) or
        (pieces[0] == "DOMAIN-KEYWORD" and pieces[1] in KEYWORDS)
    ):
        if pieces[2] not in ("REJECT", "PROXY"):
            raise ValueError("Unexpected policy for " + stripped)
        updated_lines.append(",".join((pieces[0], pieces[1], target)) + ending)
        count += 1
    else:
        updated_lines.append(line)
expected_count = len(DOMAINS) + len(KEYWORDS)
if count != expected_count:
    raise ValueError(f"Expected {expected_count} Facebook/Instagram rules; found {count}.")
updated = "".join(updated_lines)
print(f"Schedule: {utc:%Y-%m-%d %H:%M} UTC; phase={minute_of_day%80}; Facebook/Instagram={target}")
if updated == original:
    print("Already correct, no commit required.")
else:
    request("PUT", {
        "message": "Schedule Facebook/Instagram " + ("ALLOW" if allow else "BLOCK"),
        "content": base64.b64encode(updated.encode()).decode(),
        "sha": data["sha"],
        "branch": BRANCH,
    })
    print("Updated USABL.conf. Shadowrocket clients must refresh manually.")
