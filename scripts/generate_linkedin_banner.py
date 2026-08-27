import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_linkedin_banner(output_path="linkedin-banner.png"):
    # Target dimensions: 1584 x 396
    # 4x Super-Sampling scale factor for ultra-sharp, crystal-clear vector & text rendering
    scale = 4
    width = 1584 * scale   # 6336 px
    height = 396 * scale   # 1584 px
    
    # Background: Smooth dark gradient (#0a0d12 to #161b22)
    img = Image.new("RGBA", (width, height), (10, 13, 18, 255))
    
    # Smooth background gradient with right-center glow
    for y in range(height):
        ratio_y = y / height
        for x in range(width):
            ratio_x = x / width
            dist_right = math.sqrt((x - width * 0.75)**2 + (y - height * 0.5)**2)
            glow = max(0, 1 - dist_right / (550 * scale))
            
            r = int(10 + glow * 18 + ratio_x * 12)
            g = int(13 + glow * 24 + ratio_x * 14)
            b = int(18 + glow * 22 + ratio_x * 16)
            img.putpixel((x, y), (r, g, b, 255))
            
    draw = ImageDraw.Draw(img)
    
    # Load fonts with 4x scale factor
    try:
        font_name = ImageFont.truetype("arialbd.ttf", 56 * scale)
        font_tagline = ImageFont.truetype("arial.ttf", 24 * scale)
        font_handle = ImageFont.truetype("arial.ttf", 18 * scale)
    except IOError:
        font_name = ImageFont.load_default()
        font_tagline = ImageFont.load_default()
        font_handle = ImageFont.load_default()

    # Load User-Uploaded Icons from github-profile/assets/custom_icons
    icon_dir = "assets/custom_icons"
    
    handles = [
        {"icon_path": os.path.join(icon_dir, "linkedin.png"), "text": "Kalp Shah"},
        {"icon_path": os.path.join(icon_dir, "leetcode.png"), "text": "Kalp Shah"},
        {"icon_path": os.path.join(icon_dir, "github.png"), "text": "K1905-cpu"},
        {"icon_path": os.path.join(icon_dir, "mail.png"), "text": "shahkalp0303@gmail.com"}
    ]
    
    icon_size = 28 * scale   # 112 px
    gap = 10 * scale         # 40 px
    margin_between = 35 * scale # 140 px
    
    handle_items = []
    total_bar_width = 0
    
    for h in handles:
        tb = font_handle.getbbox(h["text"])
        tw = tb[2] - tb[0]
        item_w = icon_size + gap + tw
        handle_items.append((h, item_w, tw))
        total_bar_width += item_w + margin_between
        
    total_bar_width -= margin_between
    start_bar_x = max(400 * scale, int(1530 * scale - total_bar_width))
    curr_x = start_bar_x
    bar_y = 40 * scale        # 160 px
    
    for h, item_w, tw in handle_items:
        # Load icon image & resize crisply with Lanczos
        if os.path.exists(h["icon_path"]):
            icon_img = Image.open(h["icon_path"]).convert("RGBA")
            icon_img = icon_img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            # Paste icon with alpha mask
            img.paste(icon_img, (int(curr_x), int(bar_y)), icon_img)
            
        # Draw Text perfectly vertically centered relative to the icon height
        tb = font_handle.getbbox(h["text"])
        th = tb[3] - tb[1]
        text_y = bar_y + (icon_size - th) // 2 - tb[1]
        text_x = curr_x + icon_size + gap
        
        draw.text((int(text_x), int(text_y)), h["text"], fill="#E6EDF3", font=font_handle)
        
        curr_x += item_w + margin_between

    # 2. MAIN NAME & TAGLINE SECTION
    name_text = "KALP SHAH"
    tagline_text = "Aspiring AI/ML Developer"
    
    name_bbox = font_name.getbbox(name_text)
    name_width = name_bbox[2] - name_bbox[0]
    name_height = name_bbox[3] - name_bbox[1]
    
    tagline_bbox = font_tagline.getbbox(tagline_text)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]
    
    center_x = 1180 * scale  # 4720 px
    name_x = center_x - (name_width // 2)
    name_y = 185 * scale     # 740 px
    
    title_color = "#F5E0A3"  # Cream gold
    rule_color = "#3A3832"   # Subtle rule line
    tagline_color = "#D4C8AD" # Muted cream
    
    # Draw Name
    draw.text((int(name_x), int(name_y)), name_text, fill=title_color, font=font_name)
    
    # Draw Separator Rule
    rule_y = name_y + name_height + (22 * scale)
    rule_width = max(name_width + (100 * scale), tagline_width + (60 * scale))
    rule_left = center_x - (rule_width // 2)
    rule_right = center_x + (rule_width // 2)
    
    draw.line([(int(rule_left), int(rule_y)), (int(rule_right), int(rule_y))], fill=rule_color, width=1 * scale)
    
    # Draw Tagline Centered Directly Under KALP SHAH and the Rule
    tagline_x = center_x - (tagline_width // 2)
    tagline_y = rule_y + (20 * scale)
    draw.text((int(tagline_x), int(tagline_y)), tagline_text, fill=tagline_color, font=font_tagline)
    
    # Downsample from 4x (6336x1584) to target (1584x396) using Lanczos for crystal-clear HD anti-aliased output
    final_img = img.resize((1584, 396), Image.Resampling.LANCZOS)
    final_img.save(output_path, "PNG", quality=100)
    print(f"Created crystal-clear HD LinkedIn Banner at {output_path}")

if __name__ == "__main__":
    create_linkedin_banner("linkedin-banner.png")
