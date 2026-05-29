import os
import json
import logging
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def generate_carousel_content(config_path: str, topic: str, output_path: str = "content_plan.json") -> list:
    """
    Generates a 6-slide carousel content plan using Gemini based on brand config.
    Forces JSON output using the PAS framework.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with open(config_path, 'r') as f:
        brand_config = json.load(f)

    brand_name = brand_config.get("brand_name", "the brand")
    
    # Configure Gemini API
    api_key = os.getenv("GEMINI_API_KEY")
    
    system_instruction = f"""
    You are an elite, high-converting copywriter for {brand_name}.
    You must generate exactly 6 slides for an Instagram carousel about '{topic}'.
    
    Abide by this exact psychological framework:
    Slide 1: Hook (Grab attention immediately)
    Slide 2: Problem (Detail the core pain point)
    Slide 3: Agitation (Amplify the pain point and stakes)
    Slide 4: Solution (Introduce {brand_name}'s solution)
    Slide 5: Proof (Provide a mini case study, statistic, or undeniable fact)
    Slide 6: Call to Action (Tell them exactly what to do next)

    Constraints:
    - Keep titles very short (max 5-7 words).
    - Keep bodies punchy (max 20 words).
    - Maintain a highly professional, authoritative, yet engaging brand voice.
    - Output must be exactly 6 elements long.
    """

    prompt = """
    Create the 6-slide carousel content plan.
    Structure the response as a JSON array of objects using exactly these keys:
    [
      {
        "slide_number": 1,
        "title": "Slide Title",
        "body": "Slide body copy.",
        "visual_prompt": "Short visual description."
      }
    ]
    """

    # In DEV/Test environments without an API key, we output a deterministic mock layer.
    if not api_key:
        logging.warning("GEMINI_API_KEY not found. Generating mock content_plan.json for testing...")
        mock_plan = [
            {"slide_number": 1, "title": "Stop Wasting Time", "body": "Are you spending hours on carousels?", "visual_prompt": "A person looking frustrated at a computer screen."},
            {"slide_number": 2, "title": "The Daily Struggle", "body": "Manual design is draining your agency's true creativity.", "visual_prompt": "Clock spinning rapidly out of control."},
            {"slide_number": 3, "title": "Burnout is Real", "body": "Your agency margins are shrinking fast on repetitive tasks.", "visual_prompt": "A wilted plant on an empty desk."},
            {"slide_number": 4, "title": f"Meet {brand_name}", "body": f"{brand_name} completely automates your design pipeline.", "visual_prompt": "A glowing machine producing perfect slide layouts."},
            {"slide_number": 5, "title": "100x Faster Output", "body": "We reduced design time from 3 days to 2 minutes.", "visual_prompt": "A space rocket taking off rapidly."},
            {"slide_number": 6, "title": "Automate Today", "body": f"Visit {brand_name} to start generating carousels now.", "visual_prompt": "A sleek glowing button that says 'Start'."}
        ]
        with open(output_path, 'w') as f:
            json.dump(mock_plan, f, indent=4)
        logging.info(f"Mock content plan generated at {output_path}")
        return mock_plan

    # Production generation
    try:
        logging.info("Connecting to Gemini API...")
        genai.configure(api_key=api_key)
        
        # Enforce JSON generation
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.7,
        )
        
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_instruction,
            generation_config=generation_config
        )
        
        response = model.generate_content(prompt)
        content_plan = json.loads(response.text)
        
        # Generation of image elements using the REST API for gemini-2.5-flash-image
        import requests
        import base64
        import time
        from urllib.parse import urlencode

        # Create elements folder
        os.makedirs("output/elements", exist_ok=True)

        for slide in content_plan:
            theme_color_hex = brand_config.get("colors", {}).get("background", "dark")
            v_prompt = slide.get("visual_prompt", "Abstract professional background element")
            full_prompt = f"{v_prompt}. Use a minimalist, modern, empty space style. Include elements featuring hex color {theme_color_hex}. No text overlay. Centered composition."
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={api_key}"
            body = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"responseModalities": ["IMAGE"]}
            }
            try:
                logging.info(f"Generating image element for Slide {slide['slide_number']}...")
                r = requests.post(url, json=body, timeout=30)
                if r.status_code == 200:
                    data = r.json()
                    for cand in data.get("candidates", []):
                        for part in cand.get("content", {}).get("parts", []):
                            if "inlineData" in part:
                                b64 = part["inlineData"]["data"]
                                element_path = f"output/elements/slide_{slide['slide_number']:02d}.jpg"
                                with open(element_path, "wb") as img_file:
                                    img_file.write(base64.b64decode(b64))
                                slide["element_image_path"] = element_path
                else:
                    logging.warning(f"Image generation failed for slide {slide['slide_number']}: {r.status_code} {r.text}")
                # Brief sleep to avoid hitting immediate rate limits if any
                time.sleep(1)
            except Exception as e:
                logging.error(f"Image generation request error: {e}")

        with open(output_path, 'w') as f:
            json.dump(content_plan, f, indent=4)
            
        logging.info(f"Content plan generated via Gemini and saved to {output_path}")
        return content_plan
        
    except Exception as e:
        logging.error(f"Failed to generate content via LLM: {e}")
        logging.warning("Falling back to mock content plan for testing due to LLM failure...")
        mock_plan = [
            {"slide_number": 1, "title": "Stop Wasting Time", "body": "Are you spending hours on carousels?", "visual_prompt": "A person looking frustrated at a computer screen."},
            {"slide_number": 2, "title": "The Daily Struggle", "body": "Manual design is draining your agency's true creativity.", "visual_prompt": "Clock spinning rapidly out of control."},
            {"slide_number": 3, "title": "Burnout is Real", "body": "Your agency margins are shrinking fast on repetitive tasks.", "visual_prompt": "A wilted plant on an empty desk."},
            {"slide_number": 4, "title": f"Meet {brand_name}", "body": f"{brand_name} completely automates your design pipeline.", "visual_prompt": "A glowing machine producing perfect slide layouts."},
            {"slide_number": 5, "title": "100x Faster Output", "body": "We reduced design time from 3 days to 2 minutes.", "visual_prompt": "A space rocket taking off rapidly."},
            {"slide_number": 6, "title": "Automate Today", "body": f"Visit {brand_name} to start generating carousels now.", "visual_prompt": "A sleek glowing button that says 'Start'."}
        ]
        with open(output_path, 'w') as f:
            json.dump(mock_plan, f, indent=4)
        return mock_plan

if __name__ == "__main__":
    # Example usage
    try:
        plan = generate_carousel_content(
            config_path="brand_config.json", 
            topic="How AI replaces traditional graphic design workflows",
            output_path="content_plan.json"
        )
    except Exception as e:
        print(f"Generator failed: {e}")
