#!/usr/bin/env python3
import argparse, os, json, requests, sys

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
CURVE_KEY = {"sgd": "rf10y_sgd", "usd": "rf10y_usd"}

def die(msg, code=1):
    print("ERROR:", msg, file=sys.stderr)
    sys.exit(code)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gist-id", required=True)
    p.add_argument("--filename", required=True)
    p.add_argument("--raw-url", required=True)
    p.add_argument("--currency", required=True, choices=["sgd","usd"])
    p.add_argument("--year", required=True, type=str)
    p.add_argument("--month", required=True, type=str)
    p.add_argument("--value", required=True, type=str)
    args = p.parse_args()

    token = os.getenv("GIST_TOKEN")
    if not token:
        die("GIST_TOKEN env var is missing. Add it as a repo secret and expose via workflow.")

    # Validate month and value
    mon = args.month.strip()
    if mon not in MONTHS:
        die(f"Month must be one of: {', '.join(MONTHS)}")
    try:
        val = float(args.value)
    except ValueError:
        die("Value must be a number like 2.70")

    # 1) Fetch current JSON from raw URL
    r = requests.get(args.raw_url, timeout=30)
    r.raise_for_status()
    store = r.json()

    curve = CURVE_KEY[args.currency]
    y = str(args.year)

    # Ensure objects present
    if curve not in store: store[curve] = {}
    if y not in store[curve]: store[curve][y] = {}

    # 2) Update value (numeric, not "2.70%")
    store[curve][y][mon] = round(val, 2)

    # 3) PATCH back to gist
    api_url = f"https://api.github.com/gists/{args.gist_id}"
    payload = {"files": {args.filename: {"content": json.dumps(store, indent=2)}}}
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    resp = requests.patch(api_url, headers=headers, json=payload, timeout=30)
    if resp.status_code != 200:
        die(f"PATCH failed: {resp.status_code} {resp.text}")

    print(f"✅ Updated {curve} {y}-{mon} to {val}% in gist {args.gist_id}/{args.filename}")

if __name__ == "__main__":
    main()
