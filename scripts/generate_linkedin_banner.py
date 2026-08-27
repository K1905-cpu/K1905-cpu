import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_linkedin_banner(output_path="linkedin-banner.png"):
    # Standard LinkedIn Background Banner dimensions
    width = 1584
    height = 396
    
    # Create image with dark gradient background
    img = Image.new("RGBA", (width, height), (13, 17, 23, 255))
    draw = ImageDraw.Draw(img)
    
    # 1. Draw subtle background gradient (Dark Charcoal #0D1117 to #161B22 to #05070A)
    for y in range(height):
        # horizontal gradient shift across x and y
        ratio_y = y / height
        for x in range(width):
            ratio_x = x / width
            # radial/subtle glow on right center
            dist_right = math.sqrt((x - width * 0.75)**2 + (y - height * 0.5)**2)
            glow = max(0, 1 - dist_right / 600)
            
            r = int(10 + glow * 15 + ratio_x * 12)
            g = int(13 + glow * 25 + ratio_x * 15)
            b = int(18 + glow * 20 + ratio_x * 18)
            img.putpixel((x, y), (r, g, b, 255))
            
    draw = ImageDraw.Draw(img)
    
    # 2. Add subtle accent lines / grid glow
    accent_color = (57, 211, 83, 40) # #39d353 with alpha
    
    # Load fonts (fallback to default or system sans-serif fonts)
    font_name_size = 54
    font_tagline_size = 22
    font_handle_size = 18
    
    try:
        font_name = ImageFont.truetype("arialbd.ttf", font_name_size)
        font_tagline = ImageFont.truetype("arial.ttf", font_tagline_size)
        font_handle = ImageFont.truetype("arial.ttf", font_handle_size)
        font_bold_handle = ImageFont.truetype("arialbd.ttf", font_handle_size)
    except IOError:
        font_name = ImageFont.load_default()
        font_tagline = ImageFont.load_default()
        font_handle = ImageFont.load_default()
        font_bold_handle = ImageFont.load_default()

    # 3. Draw Social Handles Bar at Top Right (x starting ~650 to 1500)
    handles = [
        {"icon_type": "linkedin", "label": "Kalp Shah", "color": "#0A66C2"},
        {"icon_type": "leetcode", "label": "b0e6CDjMKO", "color": "#FFA116"},
        {"icon_type": "github", "label": "K1905-cpu", "color": "#FFFFFF"},
        {"icon_type": "email", "label": "shahkalp0303@gmail.com", "color": "#EA4335"}
    ]
    
    start_x = 520
    start_y = 45
    spacing = 260
    
    for i, item in enumerate(handles):
        hx = start_x + i * spacing
        hy = start_y
        
        # Draw Icon Placeholder / Custom Vector Icon
        icon_color = item["color"]
        
        # Draw simple stylized icon badge
        if item["icon_type"] == "linkedin":
            # LinkedIn "in" box
            draw.rounded_rectangle([hx, hy, hx + 24, hy + 24], radius=4, fill="#0A66C2")
            draw.text((hx + 5, hy + 2), "in", fill="#FFFFFF", font=font_bold_handle)
        elif item["icon_type"] == "leetcode":
            # LeetCode 'k/L' box
            draw.rounded_rectangle([hx, hy, hx + 24, hy + 24], radius=4, fill="#FFA116")
            draw.text((hx + 7, hy + 2), "L", fill="#000000", font=font_bold_handle)
        elif item["icon_type"] == "github":
            # GitHub Octocat circle
            draw.ellipse([hx, hy, hx + 24, hy + 24], fill="#24292F", outline="#FFFFFF", width=1)
            draw.text((hx + 6, hy + 2), "G", fill="#FFFFFF", font=font_bold_handle)
        elif item["icon_type"] == "email":
            # Email envelope box
            draw.rounded_rectangle([hx, hy, hx + 24, hy + 24], radius=4, fill="#EA4335")
            draw.text((hx + 5, hy + 2), "@", fill="#FFFFFF", font=font_bold_handle)
            
        # Draw text handle
        draw.text((hx + 32, hy + 3), item["label"], fill="#E6EDF3", font=font_handle)

    # 4. Draw Main Name Section (Bottom Right alignment like reference image)
    # Reference image: "SHRIL CARPENTER" in bold cream/gold text, underlined with subtle rule, then tagline
    name_text = "KALP SHAH"
    tagline_text = "AI & ML Developer  •  Data Science  •  Intelligent Systems"
    
    name_x = 1040
    name_y = 195
    
    # Cream / Gold accent color matching reference screenshot (#F5E0A3 / #E2C582 / #39D353)
    title_color = "#F3E4B8"
    rule_color = "#4D4637"
    tagline_color = "#D2C5A5"
    
    # Draw Name (Bold Cream/Gold)
    draw.text((name_x, name_y), name_text, fill=title_color, font=font_name)
    
    # Draw Horizontal Separator Line below name
    line_y = name_y + 75
    line_w = 460
    draw.line([(name_x - 30, line_y), (name_x + line_w, line_y)], fill=rule_color, width=1)
    
    # Draw Tagline below line
    tagline_y = line_y + 25
    draw.text((name_x - 20, tagline_y), tagline_text, fill=tagline_color, font=font_tagline)
    
    # Save Image
    img.save(output_path, "PNG")
    print(f"Created LinkedIn Banner at {output_path}")

if __name__ == "__main__":
    create_linkedin_banner("linkedin-banner.png")
