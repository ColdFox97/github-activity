import argparse
import json
import sys
import urllib.request
from urllib.error import HTTPError, URLError

parser = argparse.ArgumentParser(description="CLI for displaying recent Githubactivity")
parser.add_argument("user",type=str, help="whose activity you want to look at")
args = parser.parse_args()

data = None
url = f"https://api.github.com/users/{args.user}/events"
headers = {"User-Agent": "CLI"}
request = urllib.request.Request(url=url, headers=headers)
print("Sending message to github")

try:
    with urllib.request.urlopen(request) as response:
        print(f"Respose Status Code: {response.status}")
        print(f"Respose Message: {response.reason}")
        print(f"Remaining limit: {response.headers.get('X-RateLimit-Remaining')}")
        print("-" * 40)
        
        raw_bytes = response.read()
        json_string = raw_bytes.decode("utf-8")
        data = json.loads(json_string)

except HTTPError as e:
    print(f"[API Error]: Github responded with status code {e.code}")
    if e.code == 404:
        print("-> Hint: Github username couldn't be found")
    elif e.code == 403:
        print("-> Hint: Rate limit exceeded")
    else:
        print(f"-> Reason: {e.reason}")
    sys.exit(1)

except URLError as e:
    print(f"[Network Error] Failed to reach Github")
    print(f"-> Reason: {e.reason}")
    print(f"-> Hint: Check your internet connection or DNS settings")
    sys.exit(1)

except json.JSONDecodeError as e:
    print(f"[Data Error] Received data from Github, but it wasn't valid json")
    sys.exit(1)

except Exception as e:
    print(f"[Unecpected Error] Something went wrong: {e}")
    sys.exit(1)

if data:
    for event in data:
        event_type = event.get("type")
        repo_name = event.get("repo", {}).get("name", "Unknown Repository")
        payload = event.get("payload", {})

        if event_type == "CreateEvent":
            ref_type = payload.get("ref_type")
            ref_name = payload.get("ref")

            if ref_name is None:
                print(f"- Created new repository [{repo_name}]")
            else:
                print(f"- Created {ref_type} [{ref_name}] in [{repo_name}]")

        elif event_type == "DeleteEvent":
            ref_type = payload.get("ref_type")
            ref_name = payload.get("ref")
            print(f"- Deleted {ref_type} [{ref_name}] from {repo_name}")

        elif event_type == "ForkEvent":
            print(f"- Forked [{repo_name}]")

        elif event_type == "IssueCommentEvent":
            issue_data = payload.get("issue", {})
            issue_title = issue_data.get("title")
            issue_number = issue_data.get("number")
            print(f"- Comment on issue #{issue_number} [{issue_title}] in [{repo_name}]")

        elif event_type == "IssuesEvent":
            action = payload.get("action", "").capitalize()
            print(f"- {action} issue in {repo_name}")

        elif event_type == "PullRequestEvent":
            action = payload.get("action")
            pr_number = payload.get("number", "")
            pr_data = payload.get("pull_request", {})
            pr_title = pr_data.get("title", "a pull request")

            if action == "opened":
                print(f"- Opened pull request #{pr_number} [{pr_title}] in [{repo_name}]")
            
            elif action == "closed":
                is_merged = pr_data.get("merged", False)
                if is_merged:
                    print(f"- Merged pull request #{pr_number} [{pr_title}] in [{repo_name}]")
                else:
                    print(f"- Dismissed pull request #{pr_number} in [{repo_name}]")

            else:
                print(f"- {action.capitalize()} pull request #{pr_number} in [{repo_name}]")

        elif event_type == "PushEvent":
            commits = payload.get("commits", [])
            count = len(commits)
            suffix = "commit" if count == 1 else "commits"
            
            if commits:
                print(f"- Pushed {count} {suffix} to [{repo_name}]")

        elif event_type == "WatchEvent":
            print(f"- Starred repo [{repo_name}]")

        else:
            clean_name = "".join([f" {char}" if char.isupper() else char for char in event_type]).strip()
            print(f"- Performed {clean_name} in [{repo_name}]")

else:
    print("Connected, but the user has no recent public activity")
