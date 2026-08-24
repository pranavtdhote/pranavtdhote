import json, os, urllib.request
from pathlib import Path

USERNAME=os.getenv("GITHUB_USERNAME","pranavtdhote")
TOKEN=os.getenv("GITHUB_TOKEN")
OUT=Path("assets")

QUERY="""query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{contributionCount date}}}}}}"""

def fetch():
    if not TOKEN: raise SystemExit("GITHUB_TOKEN is required.")
    data=json.dumps({"query":QUERY,"variables":{"login":USERNAME}}).encode()
    req=urllib.request.Request("https://api.github.com/graphql",data=data,headers={
        "Authorization":f"Bearer {TOKEN}","Content-Type":"application/json","User-Agent":"profile-generator"})
    with urllib.request.urlopen(req,timeout=30) as r: x=json.load(r)
    if x.get("errors"): raise RuntimeError(x["errors"])
    return x["data"]["user"]["contributionsCollection"]["contributionCalendar"]

def render(cal,dark):
    bg,fg,muted,levels=(
        ("#050b10","#00c9ff","#8aa7b2",["#102027","#064f63","#087d9a","#00a9cf","#00e1ff"])
        if dark else
        ("#f6fbfd","#007f9e","#4f6972",["#e7f5f8","#bde7ef","#7bcddd","#36aec8","#007f9e"])
    )
    cell,gap,left,top=12,4,42,78
    width=left+len(cal["weeks"])*(cell+gap)+30
    height=top+7*(cell+gap)+60
    out=[f'<rect width="100%" height="100%" rx="18" fill="{bg}"/>',
         f'<text x="{left}" y="36" fill="{fg}" font-family="sans-serif" font-size="21" font-weight="700">Contribution Matrix</text>',
         f'<text x="{width-35}" y="36" fill="{muted}" text-anchor="end" font-family="monospace" font-size="13">{cal["totalContributions"]} contributions</text>']
    for x,week in enumerate(cal["weeks"]):
        for day in week["contributionDays"]:
            dow=(__import__("datetime").date.fromisoformat(day["date"]).weekday()+1)%7
            n=day["contributionCount"]
            level=0 if n==0 else min(4,1+n//4)
            px=left+x*(cell+gap); py=top+dow*(cell+gap)
            out.append(f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="3" fill="{levels[level]}"><title>{day["date"]}: {n} contributions</title></rect>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'+"\n".join(out)+"</svg>"

def main():
    cal=fetch(); OUT.mkdir(exist_ok=True)
    (OUT/"contribution-dark.svg").write_text(render(cal,True),encoding="utf-8")
    (OUT/"contribution-light.svg").write_text(render(cal,False),encoding="utf-8")

if __name__=="__main__": main()
