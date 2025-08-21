import requests
import os

GIST_ID = "fb7a8e9b365b5a05f47c6223b54c6676"  # your gist id
FILENAME = "rf10y"  # the file name inside gist

# Example new data you want to add:
year = "2025"
month = "Aug"
value = "2.8%"

token = os.environ["GIST_TOKEN"]

# Fetch current gist content
r = requests.get(f"https://api.github.com/gists/{GIST_ID}")
data = r.json()
content = data["files"][FILENAME]["content"]

# Append new line
new_line = f"{year}\t{month}\t{value}"
content += "\n" + new_line

# Push update
payload = {
    "files": {
        FILENAME: {
            "content": content
        }
    }
}
requests.patch(
    f"https://api.github.com/gists/{GIST_ID}",
    headers={"Authorization": f"token {token}"},
    json=payload
)
print("✅ Gist updated")
