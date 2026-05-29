import json
import os
from PIL import Image, ImageDraw, ImageFont

def wrap_text(text, font, max_width, draw):
    lines = []
    if not text: return lines
    words = text.split()
    current_line = []
    
    for word in words:
        current_line.append(word)
        bbox = draw.textbbox((0, 0), " ".join(current_line), font=font)
        if (bbox[2] - bbox[0]) > max_width:
            current_line.pop()
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def render_slide(config_path: str, slide_content: dict, output_path: str):
    """
    Renders a single carousel slide based on a brand config and slide content.
    Includes creative elements like grids, varied layouts, and accents.
    """
    with open(config_path, 'r') as f:
        config = json.load(f)

    layout = config.get("layout_settings", {})
    colors = config.get("colors", {})
    fonts = config.get("fonts", {})
    brand_name = config.get("brand_name", "Brand")

    width = layout.get("width", 1080)
    height = layout.get("height", 1350)
    
    bg_color = colors.get("background", "#1a1a2e")
    title_color = colors.get("primary", "#ffffff")
    body_color = colors.get("secondary", "#cccccc")

    image = Image.new("RGB", (width, height), color=bg_color)
    
    element_path = slide_content.get("element_image_path")
    if element_path and os.path.exists(element_path):
        try:
            elem_img = Image.open(element_path).convert("RGBA")
            # Resize and crop to fill the background
            img_ratio = elem_img.width / elem_img.height
            target_ratio = width / height
            if img_ratio > target_ratio:
                new_h = height
                new_w = int(new_h * img_ratio)
            else:
                new_w = width
                new_h = int(new_w / img_ratio)
            elem_img = elem_img.resize((new_w, new_h), Image.LANCZOS)
            x_offset = (new_w - width) // 2
            y_offset = (new_h - height) // 2
            elem_img = elem_img.crop((x_offset, y_offset, x_offset + width, y_offset + height))
            
            # Blend with background color for readability
            if len(bg_color) == 7:
                r, g, b = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
            else:
                r, g, b = (26, 26, 46)
                
            bg_overlay = Image.new("RGBA", (width, height), color=(r, g, b, 200))
            elem_img.alpha_composite(bg_overlay)
            
            image = elem_img.convert("RGB")
        except Exception as e:
            print(f"Failed to load element image: {e}")

    draw = ImageDraw.Draw(image)

    slide_number = slide_content.get("slide_number", 1)

    # -----------------------------
    # Creative Element: Dot Grid Background
    # -----------------------------
    grid_size = 50
    dot_color = title_color + "22"  # very transparent if hex supports it, or just use a muted version
    # Since we can't easily do alpha on basic colors in PIL without RGBA, we'll draw thin lines or dots
    grid_overlay = Image.new("RGBA", (width, height), (0,0,0,0))
    grid_draw = ImageDraw.Draw(grid_overlay)
    
    # Simple plus grid
    for x in range(0, width, grid_size):
        for y in range(0, height, grid_size):
            # parse title color to RGB roughly just to make an alpha version
            h = title_color.lstrip('#')
            if len(h) == 6:
                r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                grid_draw.rectangle([x, y, x+2, y+2], fill=(r, g, b, 30))
                
    image.paste(grid_overlay, (0,0), grid_overlay)

    # -----------------------------
    # Creative Element: Abstract Shapes
    # -----------------------------
    # Draw a big accent shape based on slide number to give variety
    h = title_color.lstrip('#')
    if len(h) == 6:
        r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        accent_color = (r, g, b, 20) # Very faint accent colored shape
        shape_overlay = Image.new("RGBA", (width, height), (0,0,0,0))
        shape_draw = ImageDraw.Draw(shape_overlay)
        
        if slide_number % 3 == 1:
            shape_draw.ellipse([-200, -200, 500, 500], fill=accent_color)
        elif slide_number % 3 == 2:
            shape_draw.polygon([(width, 0), (width, 800), (400, 0)], fill=accent_color)
        else:
            shape_draw.rectangle([width-400, height-400, width+100, height+100], fill=accent_color)
            
        image.paste(shape_overlay, (0,0), shape_overlay)


    # Solid top bar accent
    draw.rectangle([0, 0, width, 24], fill=title_color)

    # Load Fonts
    try:
        font_title = ImageFont.truetype(fonts.get("title", ""), 96)
    except Exception:
        font_title = ImageFont.load_default()

    try:
        font_body = ImageFont.truetype(fonts.get("body", ""), 48)
    except Exception:
        font_body = ImageFont.load_default()

    try:
        font_footer = ImageFont.truetype(fonts.get("body", ""), 32)
    except Exception:
        font_footer = ImageFont.load_default()

    title = slide_content.get("title", "Default Title")
    body = slide_content.get("body", "Default Body")

    max_text_width = width - 240

    # Layout selection
    alignment = "center" if slide_number % 2 == 1 else "left"
    
    # Title Wrapping & Rendering
    title_lines = wrap_text(title, font_title, max_text_width, draw)
    title_y = layout.get("title_y_offset", 350)
    
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        
        if alignment == "center":
            x = (width - line_w) / 2
        else:
            x = 120
            
        # Draw text shadow/glow
        draw.text((x+4, title_y+4), line, font=font_title, fill=(0,0,0,100))
        draw.text((x, title_y), line, font=font_title, fill=title_color)
        title_y += line_h + 24

    # Body Wrapping & Rendering
    body_lines = wrap_text(body, font_body, max_text_width, draw)
    body_y = title_y + 80
    
    for line in body_lines:
        bbox = draw.textbbox((0, 0), line, font=font_body)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        
        if alignment == "center":
            x = (width - line_w) / 2
        else:
            x = 120
            
        draw.text((x, body_y), line, font=font_body, fill=body_color)
        body_y += line_h + 16

    # Footer
    draw.line([120, height - 140, width - 120, height - 140], fill=body_color, width=2)
    
    footer_text = f"{brand_name.upper()}"
    slide_indicator = f"{slide_number} / 6"
    
    # Brand left
    draw.text((120, height - 100), footer_text, font=font_footer, fill=title_color)
    
    # Slide right
    bbox_indicator = draw.textbbox((0, 0), slide_indicator, font=font_footer)
    indicator_w = bbox_indicator[2] - bbox_indicator[0]
    draw.text((width - 120 - indicator_w, height - 100), slide_indicator, font=font_footer, fill=body_color)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    image.save(output_path)
    print(f"Image saved at: {output_path}")

if __name__ == "__main__":
    # Example usage
    sample_content = {
        "title": "Welcome to Carousel Factory",
        "body": "Deterministic, code-based rendering."
    }
    # Using default parameters assuming running from project root
    render_slide("brand_config.json", sample_content, "output/slide_01.jpg")
