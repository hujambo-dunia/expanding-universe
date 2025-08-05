import os, requests, datetime, json

# GitHub search API URL with query
api_url = "https://api.github.com/search/repositories"
stars_min = 250
date_today = datetime.date.today().strftime("%Y-%m-%d")
date_recent_commits = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
stars_aggregate = 0
query = f"(biology OR bioinformatics OR genome OR genomic) in:description stars:>{stars_min} pushed:>={date_recent_commits}"
params = {
    "q": query,
    "sort": "stars",
    "order": "desc",
    "per_page": 100
}

# Optional authentication (not required, but use GITHUB_TOKEN if available for higher rate limit)
headers = {}
token = os.getenv("GITHUB_TOKEN")  # Actions automatically provide this
if token:
    headers["Authorization"] = f"Bearer {token}"

response = requests.get(api_url, params=params, headers=headers)
data = response.json()

items = data.get("items", [])
# Filter out GalaxyProject repos
filtered = [repo for repo in items if repo.get("owner", {}).get("login") != "GalaxyProject"]

# Prepare markdown content
md_lines = []
md_lines.append(f"## Trending Bioinformatics Repositories (Updated: {date_today})\n")
md_lines.append(f"**Showing {len(filtered)} projects matching the criteria ({stars_min}+ stars, recent updates)**\n")
for repo in filtered:
    name = repo["full_name"]        # e.g. owner/name
    stars = repo["stargazers_count"]
    stars_aggregate += stars
    description = (repo["description"] or "").strip()
    url = repo["html_url"]
    md_lines.append(f"- **[{name}]({url})** – ⭐ {stars} – {description}")

# Write to README.md
readme_text = "\n".join(md_lines) + "\n"
with open("README.md", "w") as f:
    f.write(readme_text)

# Update STATS.md with new row
stats_row = f"| {date_today} | {stars_aggregate} | {query} |\n"
try:
    with open("STATS.md", "a", encoding="utf-8") as f2:
        f2.write(stats_row)
        print("Write succeeded to STATS.md")
except Exception as e:
    print("Write failed to STATS.md:", e)
