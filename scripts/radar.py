#!/usr/bin/env python3
"""
radar.py - Render SVG skill and language radar charts for GitHub Profile READMEs.
Supports self-rated values from JSON and live byte-counts from GitHub API.
"""

import argparse
import html
import json
import math
import os
import sys
import urllib.request

def parse_args():
    parser = argparse.ArgumentParser(description="Generate radar chart SVGs (Dark and Light themes).")
    parser.add_argument("--data", help="Path to JSON file containing skills data")
    parser.add_argument("--github", help="GitHub username to fetch language statistics from")
    parser.add_argument("-o", "--output", default="assets/radar", help="Output filename prefix (without -dark.svg/-light.svg)")
    parser.add_argument("--limit", type=int, default=7, help="Maximum number of radar axes (default: 7)")
    parser.add_argument("--curve", type=float, default=0.4, help="Non-linear exponent curve for scaling raw byte counts (default: 0.4)")
    parser.add_argument("--values", action="store_true", help="Display numeric value text beside axis labels")
    parser.add_argument("--exclude", default="shell,html,css,makefile,dockerfile,batchfile,procfile", help="Comma-separated languages to exclude from GitHub API counts")
    return parser.parse_args()

def fetch_github_languages(username, exclude_list):
    url = f"https://api.github.com/users/{username}/repos?per_page=100"
    headers = {"User-Agent": "GitHub-Profile-Radar-Generator"}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            repos = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Warning: Failed to fetch repos from GitHub API ({e}). Using mock language data.")
        return [
            {"label": "Python", "value": 85},
            {"label": "TypeScript", "value": 80},
            {"label": "JavaScript", "value": 78},
            {"label": "PHP", "value": 70},
            {"label": "C++", "value": 65},
            {"label": "C", "value": 60}
        ]

    lang_counts = {}
    exclude_set = {x.strip().lower() for x in exclude_list.split(',')}

    for repo in repos:
        if repo.get('fork', False):
            continue
        lang_url = repo.get('languages_url')
        if not lang_url:
            continue
        try:
            l_req = urllib.request.Request(lang_url, headers=headers)
            with urllib.request.urlopen(l_req) as l_resp:
                l_data = json.loads(l_resp.read().decode('utf-8'))
                for lang, bytes_cnt in l_data.items():
                    if lang.lower() in exclude_set:
                        continue
                    lang_counts[lang] = lang_counts.get(lang, 0) + bytes_cnt
        except Exception:
            continue

    if not lang_counts:
        return [
            {"label": "Python", "value": 85},
            {"label": "React", "value": 80},
            {"label": "PHP", "value": 75},
            {"label": "C++", "value": 70}
        ]

    sorted_langs = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"label": lang, "raw_bytes": cnt} for lang, cnt in sorted_langs]

def process_axes_data(raw_items, limit, curve):
    items = raw_items[:limit]
    if not items:
        return []

    if "raw_bytes" in items[0]:
        max_bytes = max(item["raw_bytes"] for item in items)
        processed = []
        for item in items:
            raw = item["raw_bytes"]
            # Exponent curve scaling
            scaled = (raw / max_bytes) ** curve if max_bytes > 0 else 0
            val_percent = int(scaled * 100)
            
            # Format byte label (KB or MB)
            if raw > 1024 * 1024:
                lbl_val = f"{raw / (1024*1024):.1f}MB"
            elif raw > 1024:
                lbl_val = f"{raw / 1024:.0f}KB"
            else:
                lbl_val = f"{raw}B"

            processed.append({
                "label": item["label"],
                "value": val_percent,
                "display_val": lbl_val
            })
        return processed
    else:
        for item in items:
            item["display_val"] = f"{item['value']}%"
        return items

def render_radar_svg(axes, title, is_dark=True, show_values=False):
    width, height = 480, 420
    cx, cy = width / 2, (height / 2) + 10
    max_r = 135

    bg_color = "#0d1117" if is_dark else "#ffffff"
    card_bg = "#161b22" if is_dark else "#f6f8fa"
    card_border = "#30363d" if is_dark else "#d0d7de"
    text_color = "#c9d1d9" if is_dark else "#24292f"
    sub_text = "#8b949e" if is_dark else "#57606a"
    accent = "#39d353" if is_dark else "#1f883d"
    fill_alpha = "rgba(57, 211, 83, 0.25)" if is_dark else "rgba(31, 136, 61, 0.20)"
    grid_stroke = "#30363d" if is_dark else "#e1e4e8"

    n_axes = len(axes)
    if n_axes < 3:
        return ""

    angle_step = (2 * math.pi) / n_axes
    start_angle = -math.pi / 2

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    svg.append(f'  <style>')
    svg.append(f'    .title {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 600; fill: {text_color}; }}')
    svg.append(f'    .label {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; font-weight: 500; fill: {text_color}; }}')
    svg.append(f'    .val-text {{ font-family: monospace; font-size: 11px; fill: {sub_text}; }}')
    svg.append(f'  </style>')

    # Background card
    svg.append(f'  <rect width="{width}" height="{height}" fill="{card_bg}" stroke="{card_border}" stroke-width="1" rx="10"/>')
    svg.append(f'  <text x="{width/2}" y="32" text-anchor="middle" class="title">{html.escape(title)}</text>')

    # Concentric grid polygons (20%, 40%, 60%, 80%, 100%)
    for level in [0.2, 0.4, 0.6, 0.8, 1.0]:
        r = max_r * level
        points = []
        for i in range(n_axes):
            angle = start_angle + i * angle_step
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            points.append(f"{px:.1f},{py:.1f}")
        pts_str = " ".join(points)
        svg.append(f'  <polygon points="{pts_str}" fill="none" stroke="{grid_stroke}" stroke-width="1" stroke-dasharray="{ "none" if level == 1.0 else "3 3" }"/>')

    # Axis rays & Labels
    data_points = []
    for i, axis in enumerate(axes):
        angle = start_angle + i * angle_step
        val_ratio = min(100, max(0, axis["value"])) / 100.0
        r_val = max_r * val_ratio

        # Ray end point
        rx = cx + max_r * math.cos(angle)
        ry = cy + max_r * math.sin(angle)
        svg.append(f'  <line x1="{cx:.1f}" y1="{cy:.1f}" x2="{rx:.1f}" y2="{ry:.1f}" stroke="{grid_stroke}" stroke-width="1"/>')

        # Data point
        dx = cx + r_val * math.cos(angle)
        dy = cy + r_val * math.sin(angle)
        data_points.append((dx, dy))

        # Label positioning
        lbl_r = max_r + 25
        lx = cx + lbl_r * math.cos(angle)
        ly = cy + lbl_r * math.sin(angle)

        anchor = "middle"
        if math.cos(angle) > 0.3:
            anchor = "start"
        elif math.cos(angle) < -0.3:
            anchor = "end"

        val_suffix = f" ({axis['display_val']})" if show_values else ""
        escaped_label = html.escape(str(axis["label"]))
        escaped_suffix = html.escape(str(val_suffix))
        svg.append(f'  <text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" dominant-baseline="central" class="label">{escaped_label}<tspan class="val-text">{escaped_suffix}</tspan></text>')

    # Data Polygon Fill & Stroke
    pts_data_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in data_points)
    svg.append(f'  <polygon points="{pts_data_str}" fill="{fill_alpha}" stroke="{accent}" stroke-width="2.5"/>')

    # Data Vertex Dots
    for dx, dy in data_points:
        svg.append(f'  <circle cx="{dx:.1f}" cy="{dy:.1f}" r="4" fill="{accent}" stroke="{card_bg}" stroke-width="1.5"/>')

    svg.append('</svg>')
    return '\n'.join(svg)

def main():
    args = parse_args()
    title = "Skill Radar"

    if args.data and os.path.exists(args.data):
        with open(args.data, "r", encoding="utf-8") as f:
            jdata = json.load(f)
            title = jdata.get("title", "Skill Radar")
            raw_items = jdata.get("axes", [])
    elif args.github:
        title = "Language Bytes (GitHub API)"
        raw_items = fetch_github_languages(args.github, args.exclude)
    else:
        print("Error: Specify either --data path/to/skills.json or --github username")
        sys.exit(1)

    axes = process_axes_data(raw_items, args.limit, args.curve)

    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    dark_svg = render_radar_svg(axes, title, is_dark=True, show_values=args.values)
    dark_path = f"{args.output}-dark.svg"
    with open(dark_path, "w", encoding="utf-8") as f:
        f.write(dark_svg)

    light_svg = render_radar_svg(axes, title, is_dark=False, show_values=args.values)
    light_path = f"{args.output}-light.svg"
    with open(light_path, "w", encoding="utf-8") as f:
        f.write(light_svg)

    print(f"Generated radar charts: {dark_path} and {light_path}")

if __name__ == "__main__":
    main()
