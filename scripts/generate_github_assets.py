#!/usr/bin/env python3
"""Generate compact self-hosted GitHub overview SVGs and a contribution matrix."""

import json
import os
import urllib.request
from collections import Counter
from pathlib import Path
from datetime import date

USERNAME = os.getenv("GITHUB_USERNAME", "pranavtdhote")
TOKEN = os.getenv("GITHUB_TOKEN", "")
OUT = Path("assets")
OUT.mkdir(exist_ok=True)

def github(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "pranav-github-profile"
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request("https://api.github.com" + path, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def esc(v):
    return str(v).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def overview():
    user = github(f"/users/{USERNAME}")
    repos = [
        r for r in github(f"/users/{USERNAME}/repos?per_page=100&type=owner&sort=updated")
        if not r.get("fork")
    ]
    stars = sum(r.get("stargazers_count", 0) for r in repos)
    forks = sum(r.get("forks_count", 0) for r in repos)

    rows = [
        ("Repositories", user.get("public_repos", 0)),
        ("Followers", user.get("followers", 0)),
        ("Following", user.get("following", 0)),
        ("Public stars", stars),
        ("Repository forks", forks),
    ]

    bg="#050b10"; fg="#00c9ff"; muted="#8aa7b2"
    body=[f'<rect width="900" height="330" rx="18" fill="{bg}"/>',
          f'<text x="35" y="48" fill="{fg}" font-family="monospace" font-size="24" font-weight="700">GitHub Overview</text>']
    y=95
    for k,v in rows:
        body.append(f'<text x="40" y="{y}" fill="{muted}" font-family="monospace" font-size="16">{esc(k)}</text>')
        body.append(f'<text x="650" y="{y}" fill="{fg}" font-family="monospace" font-size="17" text-anchor="end">{esc(v)}</text>')
        y += 42

    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330">'+"".join(body)+"</svg>"
    (OUT/"github-overview.svg").write_text(svg, encoding="utf-8")

    langs=Counter()
    for r in repos:
        try:
            langs.update(github(f"/repos/{USERNAME}/{r['name']}/languages"))
        except Exception:
            pass

    total=sum(langs.values()) or 1
    body=[f'<rect width="900" height="430" rx="18" fill="{bg}"/>',
          f'<text x="35" y="48" fill="{fg}" font-family="monospace" font-size="24" font-weight="700">Language Map</text>']
    y=95
    for lang,n in langs.most_common(8):
        pct=n/total*100
        body.append(f'<text x="40" y="{y}" fill="{muted}" font-family="monospace" font-size="15">{esc(lang)}</text>')
        body.append(f'<rect x="180" y="{y-13}" width="500" height="15" rx="7" fill="#12303a"/>')
        body.append(f'<rect x="180" y="{y-13}" width="{max(2,500*pct/100):.1f}" height="15" rx="7" fill="{fg}"/>')
        body.append(f'<text x="730" y="{y}" fill="{fg}" font-family="monospace" font-size="15">{pct:.1f}%</text>')
        y+=40
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 430">'+"".join(body)+"</svg>"
    (OUT/"language-map.svg").write_text(svg, encoding="utf-8")

def contributions():
    # GitHub GraphQL gives the real contribution calendar.
    if not TOKEN:
        raise SystemExit("GITHUB_TOKEN is required for contribution generation.")

    query = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{contributionCount date}}}}}}"""
    payload=json.dumps({"query":query,"variables":{"login":USERNAME}}).encode()
    req=urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization":f"Bearer {TOKEN}",
            "Content-Type":"application/json",
            "User-Agent":"pranav-github-profile"
        }
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        result=json.load(r)

    if result.get("errors"):
        raise RuntimeError(result["errors"])

    cal=result["data"]["user"]["contributionsCollection"]["contributionCalendar"]

    cell=12; gap=4; left=40; top=70
    width=left+len(cal["weeks"])*(cell+gap)+30
    height=top+7*(cell+gap)+45
    levels=["#0d171c","#064f63","#087d9a","#00a9cf","#00e1ff"]

    body=[f'<rect width="{width}" height="{height}" rx="18" fill="#050b10"/>',
          f'<text x="{left}" y="35" fill="#00c9ff" font-family="monospace" font-size="20" font-weight="700">Contribution Matrix</text>',
          f'<text x="{width-30}" y="35" fill="#8aa7b2" text-anchor="end" font-family="monospace" font-size="13">{cal["totalContributions"]} contributions</text>']

    for x,week in enumerate(cal["weeks"]):
        for d in week["contributionDays"]:
            dow=(date.fromisoformat(d["date"]).weekday()+1)%7
            n=d["contributionCount"]
            level=0 if n==0 else min(4,1+n//4)
            px=left+x*(cell+gap)
            py=top+dow*(cell+gap)
            body.append(f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="3" fill="{levels[level]}"/>')

    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'+"".join(body)+"</svg>"
    (OUT/"contribution-matrix.svg").write_text(svg, encoding="utf-8")

if __name__=="__main__":
    overview()
    contributions()
    print("Generated GitHub analytics assets.")
