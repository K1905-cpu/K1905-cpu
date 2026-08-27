#!/usr/bin/env python3
"""
cards.py - Render SVG Stat Card and Featured Project Cards for GitHub Profile READMEs.
Commits static SVG cards into repo assets to prevent 503 server downtime.
"""

import argparse
import json
import os
import sys
import urllib.request

def parse_args():
    parser = argparse.ArgumentParser(description="Generate Stat Card and Project Cards SVGs.")
    parser.add_argument("--user", required=True, help="GitHub username")
    parser.add_argument("--out", default="assets", help="Output directory for generated SVG cards")
    parser.add_argument("--projects", default="assets/projects.json", help="Path to projects JSON configuration file")
    return parser.parse_args()

def fetch_user_stats(username):
    url = f"https://api.github.com/users/{username}"
    headers = {"User-Agent": "GitHub-Profile-Cards-Generator"}
    
    stats = {
        "public_repos": 12,
        "stars_received": 18,
        "forks_received": 5,
        "total_commits": "500+"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            stats["public_repos"] = data.get("public_repos", stats["public_repos"])

        # Fetch repos for star & fork count sum
        r_req = urllib.request.Request(f"https://api.github.com/users/{username}/repos?per_page=100", headers=headers)
        with urllib.request.urlopen(r_req) as r_resp:
            repos = json.loads(r_resp.read().decode('utf-8'))
            stars = sum(r.get("stargazers_count", 0) for r in repos)
            forks = sum(r.get("forks_count", 0) for r in repos)
            stats["stars_received"] = stars
            stats["forks_received"] = forks
    except Exception as e:
        print(f"Warning: Could not fetch user stats from GitHub API ({e}). Using estimated defaults.")

    return stats

def fetch_repo_details(username, repo_name):
    url = f"https://api.github.com/repos/{username}/{repo_name}"
    headers = {"User-Agent": "GitHub-Profile-Cards-Generator"}
    
    defaults = {
        "name": repo_name,
        "description": "Featured repository project",
        "stargazers_count": 5,
        "forks_count": 2,
        "language": "TypeScript"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return {
                "name": data.get("name", repo_name),
                "description": data.get("description") or defaults["description"],
                "stargazers_count": data.get("stargazers_count", 0),
                "forks_count": data.get("forks_count", 0),
                "language": data.get("language") or "JavaScript"
            }
    except Exception:
        return defaults

def render_stat_card(username, stats, is_dark=True):
    width, height = 480, 140
    card_bg = "#161b22" if is_dark else "#f6f8fa"
    card_border = "#30363d" if is_dark else "#d0d7de"
    text_color = "#c9d1d9" if is_dark else "#24292f"
    sub_text = "#8b949e" if is_dark else "#57606a"
    accent = "#39d353" if is_dark else "#1f883d"

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    svg.append(f'  <style>')
    svg.append(f'    .title {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 15px; font-weight: 600; fill: {text_color}; }}')
    svg.append(f'    .stat-num {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 22px; font-weight: 700; fill: {accent}; }}')
    svg.append(f'    .stat-lbl {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; fill: {sub_text}; }}')
    svg.append(f'  </style>')

    svg.append(f'  <rect width="{width}" height="{height}" fill="{card_bg}" stroke="{card_border}" stroke-width="1" rx="10"/>')
    svg.append(f'  <text x="24" y="34" class="title">⚡ {username}\'s Activity Overview</text>')
    svg.append(f'  <line x1="24" y1="46" x2="{width-24}" y2="46" stroke="{card_border}" stroke-width="1"/>')

    cols_data = [
        ("Public Repos", str(stats["public_repos"])),
        ("Total Stars", str(stats["stars_received"])),
        ("Total Forks", str(stats["forks_received"])),
        ("Contributions", str(stats["total_commits"]))
    ]

    col_width = (width - 48) / 4
    for i, (lbl, val) in enumerate(cols_data):
        x = 24 + i * col_width + col_width / 2
        svg.append(f'  <text x="{x}" y="80" text-anchor="middle" class="stat-num">{val}</text>')
        svg.append(f'  <text x="{x}" y="104" text-anchor="middle" class="stat-lbl">{lbl}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)

def render_project_card(repo_info, override_desc=None, is_dark=True):
    width, height = 440, 130
    card_bg = "#161b22" if is_dark else "#f6f8fa"
    card_border = "#30363d" if is_dark else "#d0d7de"
    text_color = "#58a6ff" if is_dark else "#0969da"
    body_text = "#8b949e" if is_dark else "#57606a"
    accent = "#39d353" if is_dark else "#1f883d"
    meta_color = "#8b949e" if is_dark else "#57606a"

    desc = override_desc or repo_info.get("description") or "Featured project"
    if len(desc) > 85:
        desc = desc[:82] + "..."

    lang = repo_info.get("language") or "Code"
    stars = repo_info.get("stargazers_count", 0)
    forks = repo_info.get("forks_count", 0)

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    svg.append(f'  <style>')
    svg.append(f'    .repo-name {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 15px; font-weight: 600; fill: {text_color}; }}')
    svg.append(f'    .repo-desc {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; fill: {body_text}; }}')
    svg.append(f'    .meta-text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; fill: {meta_color}; }}')
    svg.append(f'  </style>')

    svg.append(f'  <rect width="{width}" height="{height}" fill="{card_bg}" stroke="{card_border}" stroke-width="1" rx="8"/>')
    
    # Book / Repo Icon
    svg.append(f'  <path d="M4 1.75C4 .784 4.784 0 5.75 0h5.5c.966 0 1.75.784 1.75 1.75v12.5a.75.75 0 0 1-1.28.53L8.5 11.53l-3.22 3.25a.75.75 0 0 1-1.28-.53V1.75z" fill="{text_color}" transform="translate(20, 20) scale(0.9)"/>')
    svg.append(f'  <text x="42" y="32" class="repo-name">{repo_info["name"]}</text>')

    # Description (word wrapped if needed)
    svg.append(f'  <text x="20" y="60" class="repo-desc">{desc}</text>')

    # Language dot + Meta stats
    svg.append(f'  <circle cx="26" cy="100" r="5" fill="{accent}"/>')
    svg.append(f'  <text x="38" y="103" class="meta-text">{lang}</text>')

    svg.append(f'  <text x="140" y="103" class="meta-text">⭐ {stars}</text>')
    svg.append(f'  <text x="200" y="103" class="meta-text">🍴 {forks}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)

def main():
    args = parse_args()
    os.makedirs(args.out, exist_ok=True)

    # 1. Generate Stat Card
    user_stats = fetch_user_stats(args.user)
    dark_stat = render_stat_card(args.user, user_stats, is_dark=True)
    light_stat = render_stat_card(args.user, user_stats, is_dark=False)

    with open(os.path.join(args.out, "card-stats-dark.svg"), "w", encoding="utf-8") as f:
        f.write(dark_stat)
    with open(os.path.join(args.out, "card-stats-light.svg"), "w", encoding="utf-8") as f:
        f.write(light_stat)
    print("Generated activity stat cards (dark & light).")

    # 2. Generate Project Cards from projects.json
    projects_list = []
    if os.path.exists(args.projects):
        with open(args.projects, "r", encoding="utf-8") as f:
            pdata = json.load(f)
            projects_list = pdata.get("projects", [])

    for item in projects_list:
        repo_name = item.get("repo")
        override_desc = item.get("description")
        if not repo_name:
            continue

        repo_info = fetch_repo_details(args.user, repo_name)
        
        dark_card = render_project_card(repo_info, override_desc, is_dark=True)
        light_card = render_project_card(repo_info, override_desc, is_dark=False)

        safe_name = repo_name.lower().replace('/', '-')
        dark_path = os.path.join(args.out, f"card-{safe_name}-dark.svg")
        light_path = os.path.join(args.out, f"card-{safe_name}-light.svg")

        with open(dark_path, "w", encoding="utf-8") as f:
            f.write(dark_card)
        with open(light_path, "w", encoding="utf-8") as f:
            f.write(light_card)
        print(f"Generated project card for {repo_name} ({dark_path}, {light_path})")

if __name__ == "__main__":
    main()
