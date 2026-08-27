import os
import math
from PIL import Image, ImageDraw, ImageFont

def draw_linkedin_icon(draw, x, y, size=26):
    # LinkedIn Blue Box #0A66C2
    draw.rounded_rectangle([x, y, x + size, y + size], radius=5, fill="#0A66C2")
    # White "in"
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
    # LeetCode Orange Box #FFA116
    draw.rounded_rectangle([x, y, x + size, y + size], radius=5, fill="#FFA116")
    # White brackets / L symbol
    draw.line([(x + 7, y + 7), (x + 13, y + 13), (x + 7, y + 19)], fill="#FFFFFF", width=3)
    draw.line([(x + 12, y + 19), (x + 19, y + 19)], fill="#FFFFFF", width=3)

def draw_github_icon(draw, x, y, size=26):
    # GitHub Purple/Dark Circle #6e5494
    cx, cy = x + size // 2, y + size // 2
    r = size // 2
    draw.ellipse([x, y, x + size, y + size], fill="#6e5494")
    
    # Octocat Silhouette Head & Ears
    head_r = 7
    draw.ellipse([cx - head_r, cy - head_r + 1, cx + head_r, cy + head_r + 1], fill="#FFFFFF")
    # Left Ear
    draw.polygon([(cx - 7, cy - 2), (cx - 7, cy - 9), (cx - 1, cy - 5)], fill="#FFFFFF")
    # Right Ear
    draw.polygon([(cx + 7, cy - 2), (cx + 7, cy - 9), (cx + 1, cy - 5)], fill="#FFFFFF")
    # Body/Bust
    draw.polygon([(cx - 8, cy + 12), (cx - 4, cy + 4), (cx + 4, cy + 4), (cx + 8, cy + 12)], fill="#FFFFFF")

def draw_mail_icon(draw, x, y, size=26):
    # Mail Envelope (White outline on dark circle or transparent)
    # Envelope Box
    ex, ey = x + 2, y + 5
    ew, eh = size - 4, size - 10
    draw.rounded_rectangle([ex, ey, ex + ew, ey + eh], radius=3, outline="#FFFFFF", width=2)
    # Envelope Flap V-Line
    draw.line([(ex + 2, ey + 2), (ex + ew // 2, ey + eh // 2 + 1), (ex + ew - 2, ey + 2)], fill="#FFFFFF", width=2)

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
    
    # Calculate widths for smooth horizontal placement on right
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
        
    total_bar_width -= margin_between # remove last margin
    
    # Start X so bar ends around x = 1520
    start_bar_x = max(450, 1530 - total_bar_width)
    curr_x = start_bar_x
    bar_y = 42
    
    for h, item_w in handle_items:
        # Draw Icon
        if h["type"] == "linkedin":
            draw_linkedin_icon(draw, curr_x, bar_y, icon_size)
        elif h["type"] == "leetcode":
            draw_leetcode_icon(draw, curr_x, bar_y, icon_size)
        elif h["type"] == "github":
            draw_github_icon(draw, curr_x, bar_y, icon_size)
        elif h["type"] == "email":
            draw_mail_icon(draw, curr_x, bar_y, icon_size)
            
        # Draw Text
        text_x = curr_x + icon_size + gap
        draw.text((text_x, bar_y + 3), h["text"], fill="#E6EDF3", font=font_handle)
        
        curr_x += item_w + margin_between

    # 2. MAIN NAME & ALIGNED TAGLINE SECTION (RIGHT ALIGNED / CENTERED RELATIVE TO KALP SHAH)
    name_text = "KALP SHAH"
    tagline_text = "Data Driven. Curious. Creative."
    
    # Calculate bounding boxes for exact alignment
    name_bbox = font_name.getbbox(name_text)
    name_width = name_bbox[2] - name_bbox[0]
    name_height = name_bbox[3] - name_bbox[1]
    
    tagline_bbox = font_tagline.getbbox(tagline_text)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]
    
    # Position KALP SHAH on the right (center of name block around x = 1200)
    center_x = 1200
    name_x = center_x - (name_width // 2)
    name_y = 185
    
    # Colors
    title_color = "#F5E0A3" # Cream gold
    rule_color = "#3A3832" # Subtle rule line
    tagline_color = "#D4C8AD" # Muted cream
    
    # Draw Name
    draw.text((name_x, name_y), name_text, fill=title_color, font=font_name)
    
    # Draw Separator Rule directly under KALP SHAH (matching width or slightly wider)
    rule_y = name_y + name_height + 22
    rule_width = max(name_width + 80, tagline_width + 40)
    rule_left = center_x - (rule_width // 2)
    rule_right = center_x + (rule_width // 2)
    
    draw.line([(rule_left, rule_y), (rule_right, rule_y)], fill=rule_color, width=1)
    
    # Draw Tagline Centered Directly Under KALP SHAH and the Rule
    tagline_x = center_x - (tagline_width // 2)
    tagline_y = rule_y + 20
    draw.text((tagline_x, tagline_y), tagline_text, fill=tagline_color, font=font_tagline)
    
    # Save Image
    img.save(output_path, "PNG")
    print(f"Created updated LinkedIn Banner at {output_path}")

if __name__ == "__main__":
    create_linkedin_banner("linkedin-banner.png")
