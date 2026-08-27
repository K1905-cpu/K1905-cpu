import os
import math
import urllib.request
from PIL import Image, ImageDraw, ImageFont

def draw_linkedin_icon(draw, x, y, size=26):
    # LinkedIn Blue Box #0A66C2 with white "in"
    draw.rounded_rectangle([x, y, x + size, y + size], radius=5, fill="#0A66C2")
    # 'i' dot
    draw.ellipse([x + 6, y + 6, x + 9, y + 9], fill="#FFFFFF")
    # 'i' stem
    draw.rectangle([x + 6, y + 11, x + 9, y + 20], fill="#FFFFFF")
    # 'n' stem
    draw.rectangle([x + 12, y + 11, x + 15, y + 20], fill="#FFFFFF")
    # 'n' arch & right stem
    draw.rectangle([x + 15, y + 11, x + 19, y + 14], fill="#FFFFFF")
    draw.rectangle([x + 17, y + 13, x + 20, y + 20], fill="#FFFFFF")

def draw_leetcode_icon(draw, x, y, size=26):
    # Official LeetCode Dark Badge #282828 with Orange Bracket
    draw.rounded_rectangle([x, y, x + size, y + size], radius=5, fill="#282828")
    # Orange LeetCode < Bracket
    draw.line([(x + 15, y + 6), (x + 8, y + 13), (x + 15, y + 20)], fill="#FFA116", width=3)
    # Bottom white underscore line
    draw.line([(x + 12, y + 20), (x + 20, y + 20)], fill="#FFFFFF", width=3)

def draw_github_icon(draw, x, y, size=26):
    # Official GitHub Dark Rounded Badge #181717
    draw.rounded_rectangle([x, y, x + size, y + size], radius=5, fill="#181717")
    cx, cy = x + size // 2, y + size // 2
    
    # Octocat Silhouette Head & Ears
    head_r = 6
    draw.ellipse([cx - head_r, cy - head_r + 1, cx + head_r, cy + head_r + 1], fill="#FFFFFF")
    # Left Ear
    draw.polygon([(cx - 7, cy - 1), (cx - 7, cy - 8), (cx - 2, cy - 4)], fill="#FFFFFF")
    # Right Ear
    draw.polygon([(cx + 7, cy - 1), (cx + 7, cy - 8), (cx + 2, cy - 4)], fill="#FFFFFF")
    # Body
    draw.polygon([(cx - 7, cy + 9), (cx - 4, cy + 3), (cx + 4, cy + 3), (cx + 7, cy + 9)], fill="#FFFFFF")

def draw_mail_icon(draw, x, y, size=26):
    # Mail Envelope Red Badge #EA4335
    draw.rounded_rectangle([x, y, x + size, y + size], radius=5, fill="#EA4335")
    # White Envelope Box
    ex, ey = x + 4, y + 7
    ew, eh = size - 8, size - 14
    draw.rounded_rectangle([ex, ey, ex + ew, ey + eh], radius=2, outline="#FFFFFF", width=2)
    # Envelope Flap V-Line
    draw.line([(ex + 1, ey + 1), (ex + ew // 2, ey + eh // 2 + 1), (ex + ew - 1, ey + 1)], fill="#FFFFFF", width=2)

def create_linkedin_banner(output_path="linkedin-banner.png"):
    width = 1584
    height = 396
    
    # Background: Smooth dark gradient (#0a0d12 to #161b22)
    img = Image.new("RGBA", (width, height), (10, 13, 18, 255))
    draw = ImageDraw.Draw(img)
    
    for y in range(height):
        ratio_y = y / height
        for x in range(width):
            ratio_x = x / width
            dist_right = math.sqrt((x - width * 0.75)**2 + (y - height * 0.5)**2)
            glow = max(0, 1 - dist_right / 550)
            
            r = int(10 + glow * 18 + ratio_x * 12)
            g = int(13 + glow * 24 + ratio_x * 14)
            b = int(18 + glow * 22 + ratio_x * 16)
            img.putpixel((x, y), (r, g, b, 255))
            
    draw = ImageDraw.Draw(img)
    
    # Fonts
    try:
        font_name = ImageFont.truetype("arialbd.ttf", 54)
        font_tagline = ImageFont.truetype("arial.ttf", 22)
        font_handle = ImageFont.truetype("arial.ttf", 18)
    except IOError:
        font_name = ImageFont.load_default()
        font_tagline = ImageFont.load_default()
        font_handle = ImageFont.load_default()

    # 1. TOP RIGHT SOCIAL HANDLES BAR
    handles = [
        {"type": "linkedin", "text": "Kalp Shah"},
        {"type": "leetcode", "text": "Kalp Shah"},
        {"type": "github", "text": "K1905-cpu"},
        {"type": "email", "text": "shahkalp0303@gmail.com"}
    ]
    
    handle_items = []
    icon_size = 26
    gap = 8
    margin_between = 35
    
    total_bar_width = 0
    for h in handles:
        tb = font_handle.getbbox(h["text"])
        tw = tb[2] - tb[0]
        item_w = icon_size + gap + tw
        handle_items.append((h, item_w))
        total_bar_width += item_w + margin_between
        
    total_bar_width -= margin_between
    
    start_bar_x = max(450, 1530 - total_bar_width)
    curr_x = start_bar_x
    bar_y = 42
    
    for h, item_w in handle_items:
        if h["type"] == "linkedin":
            draw_linkedin_icon(draw, curr_x, bar_y, icon_size)
        elif h["type"] == "leetcode":
            draw_leetcode_icon(draw, curr_x, bar_y, icon_size)
        elif h["type"] == "github":
            draw_github_icon(draw, curr_x, bar_y, icon_size)
        elif h["type"] == "email":
            draw_mail_icon(draw, curr_x, bar_y, icon_size)
            
        text_x = curr_x + icon_size + gap
        draw.text((text_x, bar_y + 3), h["text"], fill="#E6EDF3", font=font_handle)
        
        curr_x += item_w + margin_between

    # 2. MAIN NAME & ALIGNED TAGLINE SECTION
    # User instruction: Write "Aspiring AI/ML Developer"
    name_text = "KALP SHAH"
    tagline_text = "Aspiring AI/ML Developer  •  Data Science  •  Intelligent Systems"
    
    name_bbox = font_name.getbbox(name_text)
    name_width = name_bbox[2] - name_bbox[0]
    name_height = name_bbox[3] - name_bbox[1]
    
    tagline_bbox = font_tagline.getbbox(tagline_text)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]
    
    center_x = 1180
    name_x = center_x - (name_width // 2)
    name_y = 185
    
    title_color = "#F5E0A3" # Cream gold
    rule_color = "#3A3832" # Subtle rule line
    tagline_color = "#D4C8AD" # Muted cream
    
    draw.text((name_x, name_y), name_text, fill=title_color, font=font_name)
    
    rule_y = name_y + name_height + 22
    rule_width = max(name_width + 120, tagline_width + 40)
    rule_left = center_x - (rule_width // 2)
    rule_right = center_x + (rule_width // 2)
    
    draw.line([(rule_left, rule_y), (rule_right, rule_y)], fill=rule_color, width=1)
    
    tagline_x = center_x - (tagline_width // 2)
    tagline_y = rule_y + 20
    draw.text((tagline_x, tagline_y), tagline_text, fill=tagline_color, font=font_tagline)
    
    img.save(output_path, "PNG")
    print(f"Created updated LinkedIn Banner at {output_path}")

if __name__ == "__main__":
    create_linkedin_banner("linkedin-banner.png")
