#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from workspace import ROOT, load_defaults

FONT_REGULAR_CANDIDATES = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
]
FONT_BOLD_CANDIDATES = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
]
VARIANTS = {
    'midnight-premium': {'top': (8, 12, 24), 'bottom': (30, 18, 64), 'panel': (18, 22, 40), 'outline': (65, 79, 130), 'blue': (46, 112, 201), 'purple': (123, 92, 255), 'white': (245, 247, 255), 'muted': (187, 194, 225), 'footer': (210, 216, 240)},
    'slate-cobalt': {'top': (10, 14, 22), 'bottom': (26, 24, 58), 'panel': (22, 27, 42), 'outline': (70, 86, 124), 'blue': (66, 134, 244), 'purple': (116, 76, 222), 'white': (246, 247, 252), 'muted': (189, 196, 219), 'footer': (214, 219, 236)},
    'indigo-steel': {'top': (11, 15, 28), 'bottom': (20, 28, 54), 'panel': (19, 24, 39), 'outline': (72, 92, 138), 'blue': (74, 124, 186), 'purple': (134, 92, 240), 'white': (246, 248, 255), 'muted': (184, 192, 221), 'footer': (212, 218, 241)},
}

def load_font(candidates, size):
    for path in candidates:
        p = Path(path)
        if p.exists():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ''
    for word in words:
        trial = word if not current else f'{current} {word}'
        width = draw.textbbox((0, 0), trial, font=font)[2]
        if width <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def draw_gradient(img, top_color, bottom_color):
    width, height = img.size
    draw = ImageDraw.Draw(img)
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = tuple(int(top_color[i] * (1 - ratio) + bottom_color[i] * ratio) for i in range(3))
        draw.line([(0, y), (width, y)], fill=color)

def render_linkedin_card(headline: str, subtext: str, output_path: str, brand_name: str | None = None, variant: str = 'midnight-premium'):
    defaults = load_defaults()
    theme = VARIANTS[variant]
    brand_name = brand_name or defaults.get('brand_display_name', 'Your Brand')
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1200, 627
    img = Image.new('RGB', (width, height), color=theme['top'])
    draw_gradient(img, theme['top'], theme['bottom'])
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((58, 52, 1142, 575), radius=36, fill=theme['panel'], outline=theme['outline'], width=2)
    draw.ellipse((905, -40, 1210, 265), fill=theme['blue'])
    draw.ellipse((835, 15, 1080, 260), fill=theme['purple'])
    draw.rounded_rectangle((92, 92, 190, 104), radius=6, fill=theme['blue'])
    draw.rounded_rectangle((92, 110, 240, 120), radius=6, fill=theme['purple'])
    font_brand = load_font(FONT_REGULAR_CANDIDATES, 28)
    font_headline = load_font(FONT_BOLD_CANDIDATES, 72)
    font_subtext = load_font(FONT_REGULAR_CANDIDATES, 34)
    font_footer = load_font(FONT_REGULAR_CANDIDATES, 22)
    font_badge = load_font(FONT_BOLD_CANDIDATES, 18)
    badge_text = 'LINKEDIN INSIGHT'
    badge_box = (92, 138, 300, 176)
    draw.rounded_rectangle(badge_box, radius=16, fill=(27, 34, 62), outline=(80, 95, 150), width=1)
    draw.text((badge_box[0] + 18, badge_box[1] + 9), badge_text, fill=theme['white'], font=font_badge)
    draw.text((92, 198), brand_name, fill=theme['muted'], font=font_brand)
    y = 246
    for line in wrap_text(draw, headline, font_headline, max_width=690)[:3]:
        draw.text((92, y), line, fill=theme['white'], font=font_headline)
        y += 82
    y += 14
    for line in wrap_text(draw, subtext, font_subtext, max_width=720)[:3]:
        draw.text((92, y), line, fill=theme['muted'], font=font_subtext)
        y += 42
    footer_text = defaults.get('visual_footer_text', 'systems • clarity • consistency • leverage')
    draw.rounded_rectangle((92, 520, 1108, 552), radius=12, fill=(27, 34, 62))
    draw.text((112, 525), footer_text, fill=theme['footer'], font=font_footer)
    img.save(out)
    print(json.dumps({'created': True, 'path': str(out), 'variant': variant}, indent=2))

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd', required=True)
    p_render = sub.add_parser('render-placeholder')
    p_render.add_argument('--headline', required=True)
    p_render.add_argument('--subtext', required=True)
    p_render.add_argument('--output', required=True)
    p_render.add_argument('--brand-name')
    p_render.add_argument('--variant', choices=sorted(VARIANTS.keys()), default='midnight-premium')
    args = parser.parse_args()
    if args.cmd == 'render-placeholder':
        render_linkedin_card(args.headline, args.subtext, args.output, args.brand_name, args.variant)

if __name__ == '__main__':
    main()
