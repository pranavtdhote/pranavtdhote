import json, os, urllib.request
from collections import Counter
from pathlib import Path

USERNAME = os.getenv("GITHUB_USERNAME", "pranavtdhote")
TOKEN = os.getenv("GITHUB_TOKEN", "")
OUT = Path("assets")

def gh(path):
    headers = {"Accept":"application/vnd.github+json","User-Agent":"pranav-profile-generator"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request("https://api.github.com"+path, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def esc(x):
    return str(x).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def overview(dark, values):
    bg, fg, muted = (
        ("#050b10","#00c9ff","#8aa7b2") if dark
        else ("#f6fbfd","#007f9e","#4f6972")
    )
    out = [f'<rect width="900" height="330" rx="18" fill="{bg}"/>',
           f'<text x="36" y="48" fill="{fg}" font-family="sans-serif" font-size="25" font-weight="700">GitHub Overview</text>']
    y = 95
    for k,v in values:
        out.append(f'<text x="42" y="{y}" fill="{muted}" font-family="monospace" font-size="16">{esc(k)}</text>')
        out.append(f'<text x="620" y="{y}" fill="{fg}" font-family="monospace" font-size="17" text-anchor="end">{esc(v)}</text>')
        y += 42
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330">' + "\n".join(out) + "</svg>"

def language_map(dark, langs):
    bg, fg, muted, barbg = (
        ("#050b10","#00c9ff","#8aa7b2","#12303a") if dark
        else ("#f6fbfd","#007f9e","#4f6972","#d9eef2")
    )
    total = sum(langs.values()) or 1
    out = [f'<rect width="900" height="430" rx="18" fill="{bg}"/>',
           f'<text x="36" y="48" fill="{fg}" font-family="sans-serif" font-size="25" font-weight="700">Language Map</text>']
    y=92
    for lang,n in langs.most_common(8):
        pct=n/total*100
        out += [
            f'<text x="42" y="{y}" fill="{muted}" font-family="monospace" font-size="15">{esc(lang)}</text>',
            f'<rect x="180" y="{y-13}" width="500" height="16" rx="8" fill="{barbg}"/>',
            f'<rect x="180" y="{y-13}" width="{max(2,500*pct/100):.1f}" height="16" rx="8" fill="{fg}"/>',
            f'<text x="720" y="{y}" fill="{fg}" font-family="monospace" font-size="15">{pct:.1f}%</text>'
        ]
        y+=40
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 430">' + "\n".join(out) + "</svg>"

def main():
    OUT.mkdir(exist_ok=True)
    user = gh(f"/users/{USERNAME}")
    repos = [r for r in gh(f"/users/{USERNAME}/repos?per_page=100&type=owner&sort=updated") if not r.get("fork")]
    stars=sum(r.get("stargazers_count",0) for r in repos)
    forks=sum(r.get("forks_count",0) for r in repos)
    values=[("Repositories",user.get("public_repos",0)),("Followers",user.get("followers",0)),
            ("Following",user.get("following",0)),("Public stars",stars),("Repository forks",forks)]
    for dark,name in [(True,"github-overview-dark.svg"),(False,"github-overview-light.svg")]:
        (OUT/name).write_text(overview(dark,values),encoding="utf-8")

    langs=Counter()
    for r in repos:
        try: langs.update(gh(f"/repos/{USERNAME}/{r['name']}/languages"))
        except Exception: pass
    for dark,name in [(True,"language-map-dark.svg"),(False,"language-map-light.svg")]:
        (OUT/name).write_text(language_map(dark,langs),encoding="utf-8")

if __name__=="__main__":
    main()
