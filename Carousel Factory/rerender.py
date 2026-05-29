
import os
import json
import sys

# Ensure correct path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/src'))

from renderer.renderer import render_slide

with open('content_plan.json', 'r') as f:
    plan = json.load(f)

output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)


for slide in plan:
    slide_num = slide.get("slide_number", 0)
    output_file = os.path.join(output_dir, f"slide_{slide_num:02d}.jpg")
    render_slide('brand_config.json', slide, output_file)
print("Rerendering complete")
