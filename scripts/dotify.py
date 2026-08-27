#!/usr/bin/env python3
"""
dotify.py - Turn a portrait photo into a dot-matrix SVG vector portrait.
Part of the GitHub Profile README generator suite.
"""

import argparse
import math
import os
import sys
from PIL import Image, ImageOps, ImageFilter

def parse_args():
    parser = argparse.ArgumentParser(description="Convert an image to a dot-matrix SVG portrait.")
    parser.add_argument("image", help="Input image file (JPG or PNG)")
    parser.add_argument("-o", "--output", default="assets/portrait", help="Output file path (without .svg extension)")
    parser.add_argument("--cols", type=int, default=100, help="Grid column count (default: 100)")
    parser.add_argument("--equalize", action="store_true", help="Apply histogram equalization to preserve shadow details")
    parser.add_argument("--detail", type=float, default=0.5, help="Detail enhancement factor 0.0-1.0 (default: 0.5)")
    parser.add_argument("--color", action="store_true", help="Preserve original photo colors in SVG output")
    parser.add_argument("--animate", action="store_true", help="Add subtle shimmer sweep animation across columns")
    parser.add_argument("--reveal", action="store_true", help="Add row-by-row load-in scan animation")
    parser.add_argument("--reveal-time", type=float, default=2.5, help="Total reveal animation duration in seconds")
    parser.add_argument("--reveal-fade", type=float, default=0.45, help="Individual row fade duration in seconds")
    parser.add_argument("--reveal-dir", choices=["down", "up"], default="down", help="Direction of reveal sweep")
    parser.add_argument("--circle", action="store_true", help="Mask portrait into a circle with feathered edge")
    parser.add_argument("--square", action="store_true", help="Crop image to square 1:1 aspect ratio")
    parser.add_argument("--focus", type=str, default="0.5,0.5", help="Focal point X,Y for square crop (0.0-1.0)")
    parser.add_argument("--invert", action="store_true", help="Invert dark/light dot radius logic")
    parser.add_argument("--mode", choices=["dots", "binary"], default="dots", help="Render dots or 0/1 binary matrix")
    return parser.parse_args()

def process_image(img_path, cols, equalize, detail, square, focus_str, circle):
    try:
        img = Image.open(img_path)
    except Exception as e:
        print(f"Error opening image {img_path}: {e}")
        sys.exit(1)

    has_alpha = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
    img = img.convert('RGBA') if has_alpha else img.convert('RGB')

    # Square crop if requested
    if square:
        w, h = img.size
        fx, fy = [float(v) for v in focus_str.split(',')]
        min_dim = min(w, h)
        cx = int(w * fx)
        cy = int(h * fy)
        left = max(0, min(w - min_dim, cx - min_dim // 2))
        top = max(0, min(h - min_dim, cy - min_dim // 2))
        img = img.crop((left, top, left + min_dim, top + min_dim))

    aspect = img.height / img.width
    rows = max(1, int(cols * aspect))
    
    # Downsample
    img_small = img.resize((cols, rows), Image.Resampling.LANCZOS)
    
    # Extract RGB and Alpha/Luminance
    if has_alpha:
        r, g, b, alpha = img_small.split()
        rgb = Image.merge('RGB', (r, g, b))
    else:
        rgb = img_small
        alpha = None

    gray = ImageOps.grayscale(rgb)

    if equalize:
        gray = ImageOps.equalize(gray)

    if detail > 0:
        edges = gray.filter(ImageFilter.FIND_EDGES)
        gray = Image.blend(gray, edges, min(1.0, detail * 0.4))

    return rgb, gray, alpha, cols, rows

def generate_svg(rgb, gray, alpha, cols, rows, args, is_dark_theme=True):
    cell_size = 10.0
    width = cols * cell_size
    height = rows * cell_size

    bg_color = "#0d1117" if is_dark_theme else "#ffffff"
    accent_color = "#39d353" if is_dark_theme else "#1f883d"

    svg_lines = []
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    svg_lines.append(f'  <style>')
    svg_lines.append(f'    .dot {{ transform-box: fill-box; transform-origin: center; }}')
    
    if args.reveal:
        for r in range(rows):
            delay = (r / rows) * (args.reveal_time - args.reveal_fade) if args.reveal_dir == "down" else ((rows - 1 - r) / rows) * (args.reveal_time - args.reveal_fade)
            svg_lines.append(f'    .row-{r} {{ animation: fadeIn {args.reveal_fade}s ease-in-out {delay:.2f}s forwards; opacity: 0; }}')
        svg_lines.append(f'    @keyframes fadeIn {{ to {{ opacity: 1; }} }}')

    if args.animate:
        svg_lines.append(f'    @keyframes shimmer {{ 0%, 100% {{ opacity: 0.4; }} 50% {{ opacity: 1; }} }}')

    svg_lines.append(f'  </style>')
    svg_lines.append(f'  <rect width="100%" height="100%" fill="{bg_color}" rx="8"/>')

    rgb_pixels = rgb.load()
    gray_pixels = gray.load()
    alpha_pixels = alpha.load() if alpha else None

    max_radius = cell_size * 0.45

    for y in range(rows):
        for x in range(cols):
            # Check transparency mask
            if alpha_pixels and alpha_pixels[x, y] < 30:
                continue

            lum = gray_pixels[x, y] / 255.0
            if args.invert:
                lum = 1.0 - lum

            r_val, g_val, b_val = rgb_pixels[x, y]
            color_hex = f'#{r_val:02x}{g_val:02x}{b_val:02x}' if args.color else accent_color

            cx = (x + 0.5) * cell_size
            cy = (y + 0.5) * cell_size

            # Circle mask feather check
            if args.circle:
                norm_x = (x / cols) - 0.5
                norm_y = (y / rows) - 0.5
                dist = math.sqrt(norm_x * norm_x + norm_y * norm_y)
                if dist > 0.48:
                    continue

            class_str = f'class="dot row-{y}"' if args.reveal else 'class="dot"'
            anim_style = f' style="animation: shimmer {2.0 + (x % 3) * 0.5}s ease-in-out infinite;"' if args.animate else ''

            if args.mode == "binary":
                bit = "1" if lum > 0.5 else "0"
                font_sz = cell_size * 0.8
                svg_lines.append(f'  <text x="{cx}" y="{cy + font_sz*0.3}" font-family="monospace" font-size="{font_sz:.1f}" fill="{color_hex}" text-anchor="middle" {class_str}{anim_style}>{bit}</text>')
            else:
                radius = lum * max_radius
                if radius < 0.5:
                    continue
                svg_lines.append(f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius:.2f}" fill="{color_hex}" {class_str}{anim_style}/>')

    svg_lines.append('</svg>')
    return '\n'.join(svg_lines)

def main():
    args = parse_args()
    if not os.path.exists(args.image):
        print(f"Error: Image file '{args.image}' not found.")
        sys.exit(1)

    rgb, gray, alpha, cols, rows = process_image(
        args.image, args.cols, args.equalize, args.detail, args.square, args.focus, args.circle
    )

    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    if args.color:
        svg_content = generate_svg(rgb, gray, alpha, cols, rows, args, is_dark_theme=True)
        out_path = f"{args.output}.svg"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"Generated colored dot portrait: {out_path}")
    else:
        dark_content = generate_svg(rgb, gray, alpha, cols, rows, args, is_dark_theme=True)
        dark_path = f"{args.output}-dark.svg"
        with open(dark_path, "w", encoding="utf-8") as f:
            f.write(dark_content)

        light_content = generate_svg(rgb, gray, alpha, cols, rows, args, is_dark_theme=False)
        light_path = f"{args.output}-light.svg"
        with open(light_path, "w", encoding="utf-8") as f:
            f.write(light_content)

        print(f"Generated theme portraits: {dark_path} and {light_path}")

if __name__ == "__main__":
    main()
