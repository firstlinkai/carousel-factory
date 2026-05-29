import os
import sys
import json
import logging

# Ensure src/ modules can be imported when running from project root
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from scraper.scraper import scrape_brand_data
from content.generator import generate_carousel_content
from renderer.renderer import render_slide

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def generate_html_gallery(output_dir: str, slide_files: list):
    """
    Generates a simple HTML gallery in the output directory to review the carousel slides.
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carousel Review Gallery</title>
    <style>
        body { font-family: system-ui, sans-serif; background-color: #f4f4f5; margin: 0; padding: 2rem; display: flex; flex-direction: column; align-items: center; }
        h1 { color: #3f3f46; margin-bottom: 2rem; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; width: 100%; max-width: 1400px; }
        .slide-container { display: flex; flex-direction: column; align-items: center; }
        .slide-container span { margin-top: 0.5rem; font-weight: bold; color: #52525b; }
        img { width: 100%; max-width: 400px; height: auto; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); border-radius: 8px; display: block; }
    </style>
</head>
<body>
    <h1>Carousel Factory Review</h1>
    <div class="grid">
"""
    for sf in slide_files:
        filename = os.path.basename(sf)
        html_content += f'        <div class="slide-container">\n'
        html_content += f'            <img src="{filename}" alt="{filename}">\n'
        html_content += f'            <span>{filename}</span>\n'
        html_content += f'        </div>\n'
    
    html_content += """    </div>
</body>
</html>"""
    
    gallery_path = os.path.join(output_dir, "index.html")
    with open(gallery_path, "w") as f:
        f.write(html_content)
    logging.info(f"HTML gallery generated at {gallery_path}")

def main(url: str, topic: str):
    apify_token = os.getenv("APIFY_TOKEN", "")
    config_path = "brand_config.json"
    content_path = "content_plan.json"
    output_dir = "output"
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Step 1: Initialize Brand Intelligence
        logging.info(f"--- STEP 1: Scraping brand data from {url} ---")
        brand_config = scrape_brand_data(url, apify_token)
        with open(config_path, "w") as f:
            json.dump(brand_config, f, indent=4)
            
        # Step 2: Content Generation
        logging.info(f"--- STEP 2: Generating carousel content for topic: '{topic}' ---")
        content_plan = generate_carousel_content(config_path, topic, content_path)
        
        # Step 3: Deterministic Rendering
        logging.info("--- STEP 3: Rendering slides ---")
        rendered_files = []
        for slide in content_plan:
            slide_num = slide.get("slide_number", 0)
            output_file = os.path.join(output_dir, f"slide_{slide_num:02d}.jpg")
            
            logging.info(f"Rendering Slide {slide_num}...")
            render_slide(config_path, slide, output_file)
            rendered_files.append(output_file)
            
        # Step 4: Review Gallery
        logging.info("--- STEP 4: Assembling HTML Gallery ---")
        generate_html_gallery(output_dir, rendered_files)
        
        logging.info("✅ SUCCESS: Carousel Factory pipeline completed.")
        
    except Exception as e:
        logging.error(f"❌ PIPELINE HALTED: An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python src/main.py <target_url> <topic>")
        sys.exit(1)
        
    target_url = sys.argv[1]
    target_topic = sys.argv[2]
    main(target_url, target_topic)
