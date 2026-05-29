import os
import json
import re
import logging
import requests
from bs4 import BeautifulSoup
from apify_client import ApifyClient

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def rgb_to_hex(color_str: str) -> str:
    """
    Converts rgb() or rgba() strings to standard #RRGGBB Hex.
    Returns None if unparseable.
    """
    if not color_str:
        return None
    
    color_str = color_str.strip().lower()
    if color_str.startswith('#'):
        return color_str
        
    # Match rgb(255, 255, 255) or rgba(255, 255, 255, 0.5)
    match = re.search(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', color_str)
    if match:
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
        return f"#{r:02x}{g:02x}{b:02x}"
        
    return None

from collections import Counter
import re

def parse_css_from_html(html_content: str, base_url: str = "") -> dict:
    """
    Parses HTML to extract specific CSS properties for body, h1, h2.
    Also extracts a greedy list of popular hex colors on the page including from external stylesheets.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    extracted = {'body': {}, 'h1': {}, 'h2': {}, 'palette': []}
    
    all_css = ""
    
    # 0. Fetch external stylesheets
    from urllib.parse import urljoin
    for link in soup.find_all('link', rel='stylesheet'):
        href = link.get('href')
        if href:
            css_url = urljoin(base_url, href)
            try:
                r = requests.get(css_url, timeout=3, headers={'User-Agent': 'Mozilla/5.0'})
                if r.status_code == 200:
                    all_css += r.text + " "
            except Exception as e:
                logging.debug(f"Could not fetch external CSS {css_url}: {e}")

    # 1. Parse <style> blocks
    for style_tag in soup.find_all('style'):
        if style_tag.string:
            all_css += style_tag.string + " "
            
    # Extract ALL hex colors from stylesheet
    hex_colors = re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}\b', all_css)
    if hex_colors:
        # Standardize to 6 chars
        std_hexs = []
        for h in hex_colors:
            h = h.lower()
            if len(h) == 4:
                h = f"#{h[1]}{h[1]}{h[2]}{h[2]}{h[3]}{h[3]}"
            std_hexs.append(h)
        
        counts = Counter(std_hexs)
        extracted['palette'] = [c[0] for c in counts.most_common(20)]
            
    for tag in ['body', 'h1', 'h2']:
        pattern = rf'\b{tag}\s*{{([^}}]+)}}'
        matches = re.finditer(pattern, all_css, re.IGNORECASE)
        for match in matches:
            rules = match.group(1).split(';')
            for rule in rules:
                if ':' in rule:
                    key, val = rule.split(':', 1)
                    extracted[tag][key.strip().lower()] = val.strip()
                        
    # 2. Parse inline styles (higher priority)
    for tag in ['body', 'h1', 'h2']:
        element = soup.find(tag)
        if element and element.has_attr('style'):
            rules = element['style'].split(';')
            for rule in rules:
                if ':' in rule:
                    key, val = rule.split(':', 1)
                    extracted[tag][key.strip().lower()] = val.strip()

    return extracted

def download_google_font(font_name: str, output_path: str) -> bool:
    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000: 
        return True
    
    parts = font_name.replace("'", "").replace('"', "").split(" ")
    # Replace spaces with + for URL, e.g. Open+Sans
    family = "+".join(parts)
    # try the full name first
    try:
        css_url = f"https://fonts.googleapis.com/css?family={family}"
        headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'}
        r = requests.get(css_url, headers=headers, timeout=5)
        if r.status_code == 200:
            ttf_url_match = re.search(r'url\((https://[^)]+)\)', r.text)
            if ttf_url_match:
                ttf_url = ttf_url_match.group(1)
                r2 = requests.get(ttf_url, timeout=5)
                if r2.status_code == 200:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(r2.content)
                    return True
    except Exception as e:
        logging.error(f"Failed finding font via {family}: {e}")

    # Fallback: maybe just the first word
    family_first = parts[0]
    try:
        css_url = f"https://fonts.googleapis.com/css?family={family_first}"
        headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'}
        r = requests.get(css_url, headers=headers, timeout=5)
        if r.status_code == 200:
            ttf_url_match = re.search(r'url\((https://[^)]+)\)', r.text)
            if ttf_url_match:
                ttf_url = ttf_url_match.group(1)
                r2 = requests.get(ttf_url, timeout=5)
                if r2.status_code == 200:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(r2.content)
                    return True
    except Exception as e:
        logging.error(f"Failed finding font via {family_first}: {e}")
        
    return False

def validate_config(config: dict) -> dict:
    """
    Validates extracted data against the brand_config.json schema.
    Triggers warnings for empty/null colors and applies fallback fonts.
    Returns the sanitized config.
    """
    colors = config.get("colors", {})
    fonts = config.get("fonts", {})
    
    # Validate colors
    for color_key in ["primary", "secondary", "background"]:
        if not colors.get(color_key):
            logging.warning(f"Validation Warning: '{color_key}' color is empty or null.")
            # Apply strict fallbacks to avoid renderer crash
            fallback_map = {"primary": "#ffffff", "secondary": "#cccccc", "background": "#000000"}
            colors[color_key] = fallback_map[color_key]

    # Validate fonts
    default_font_path = "assets/fonts/Default-Sans.ttf"
    for font_key in ["title", "body"]:
        font_path = fonts.get(font_key)
        font_name_raw = os.path.basename(font_path).replace(".ttf", "") if font_path else ""
        
        if font_name_raw and not os.path.exists(font_path):
            success = download_google_font(font_name_raw, font_path)
            if not success:
                logging.warning(f"Validation Warning: {font_key.capitalize()} font '{font_path}' missing and download failed. Falling back to default.")
                fonts[font_key] = default_font_path
        elif not font_name_raw:
            fonts[font_key] = default_font_path
            
    config["colors"] = colors
    config["fonts"] = fonts
    return config

def scrape_brand_data(url: str, apify_token: str) -> dict:
    """
    Scrapes website content using Apify or fallback requests.
    Returns a validated dictionary structured for brand_config.json.
    """
    if not url.startswith('http'):
        url = 'https://' + url
        
    html_content = ""
    if apify_token and apify_token != "LOCAL_TEST_TOKEN":
        try:
            client = ApifyClient(apify_token)
            run_input = {"startUrls": [{"url": url}], "maxCrawlPages": 1}
            run = client.actor("apify/website-content-crawler").call(run_input=run_input)
            items = client.dataset(run["defaultDatasetId"]).list_items().items
            html_content = items[0].get('html', '') if items else ''
        except Exception as e:
            logging.error(f"Apify scraping failed: {e}. Falling back to requests.")
            
    if not html_content:
        # Fallback normal scraping
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            html_content = response.text
        except Exception as e:
            logging.error(f"Requests scraping failed: {e}")
            # Absolute fallback if all scraping fails
            html_content = '''
            <html><head><style>
                body { background-color: #1a1a2e; color: #ffffff; font-family: 'Open Sans', sans-serif; }
                h1 { color: #f9a826; font-family: 'Roboto Bold', sans-serif; }
            </style></head><body><h1>A</h1></body></html>
            '''

    logging.info(f"Extracting styles from {url}...")
    extracted_styles = parse_css_from_html(html_content, base_url=url)
    
    # Extract structural colors first
    bg_raw = extracted_styles['body'].get('background-color') or extracted_styles['body'].get('background')
    body_raw = extracted_styles['body'].get('color')
    h1_raw = extracted_styles['h1'].get('color')
    
    palette = extracted_styles.get('palette', [])
    
    # Infer if structural colors are missing
    bg_hex = rgb_to_hex(bg_raw)
    primary_hex = rgb_to_hex(h1_raw)
    secondary_hex = rgb_to_hex(body_raw)
    
    if not bg_hex and len(palette) > 0:
        # Most common color is usually background
        bg_hex = palette[0]
        
    if not primary_hex and len(palette) > 1:
        # Second most common is often primary text or accent
        primary_hex = palette[1]
        
    if not secondary_hex and len(palette) > 2:
        secondary_hex = palette[2]
        
    if not bg_hex: bg_hex = "#1a1a2e"
    if not primary_hex: primary_hex = "#ffffff"
    if not secondary_hex: secondary_hex = "#cccccc"
    
    # Determine Fonts
    title_font_raw = extracted_styles['h1'].get('font-family', '').split(',')[0].strip(' "\'')
    body_font_raw = extracted_styles['body'].get('font-family', '').split(',')[0].strip(' "\'')
    
    # Construct initial config
    brand_config = {
        "brand_name": url.replace("https://", "").replace("http://", "").split("/")[0],
        "colors": {
            "primary": primary_hex,
            "secondary": secondary_hex,
            "background": bg_hex
        },
        "fonts": {
            "title": f"assets/fonts/{title_font_raw}.ttf" if title_font_raw else "",
            "body": f"assets/fonts/{body_font_raw}.ttf" if body_font_raw else ""
        },
        "layout_settings": {
            "width": 1080,
            "height": 1350,
            "title_y_offset": 500,
            "body_y_offset": 700,
            "margin_x": 100
        }
    }

    logging.info("Validating configurations...")
    valid_config = validate_config(brand_config)
    
    return valid_config

if __name__ == "__main__":
    token = os.getenv("APIFY_TOKEN", "")
    url_to_scrape = "https://example.com"
    
    try:
        config_data = scrape_brand_data(url_to_scrape, token)
        
        with open("brand_config.json", "w") as f:
            json.dump(config_data, f, indent=4)
            
        logging.info("brand_config.json generated and validated successfully.")
    except Exception as e:
        logging.error(f"Error during scraping: {e}")
