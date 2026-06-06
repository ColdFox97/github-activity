import argparse
import json
import sys
import urllib.request

user = "ColdFox97"
url = f"https://api.github.com/users/{user}/events"

headers = {
    "User-Agent": "" 
}

request = urllib.request.Request(url=url, headers=headers)
print("Sending message to github")

with urllib.request.urlopen(request) as response:
    print(f"Respose Status Code: {response.status}")
    print(f"Respose Message: {response.reason}")
    print(f"Remaining limit: {response.headers.get("X-RateLimit-Remaining")}")
    print("-" * 40)

    raw_bytes = response.read()
    json_string = raw_bytes.decode("utf-8")
    data = json.loads(json_string)

    if data:
        event = data[0]
        print("Connection successful! Here is the latest event:")
        print(f"Event ID: {event.get("id")}")
        print(f"Type:     {event.get("type")}")
        print(f"Repo:     {event.get("repo", {}).get("name")}")
        print("-" * 40, "\n")
    else:
        print("Connected, but the user has no recent public activity")