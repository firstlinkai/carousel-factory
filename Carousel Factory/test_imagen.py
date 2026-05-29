import requests, os, json
api_key = os.getenv("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image:generateContent?key={api_key}"
body = {
  "contents": [
    {
      "parts": [{"text": "A robot holding a red skateboard."}]
    }
  ],
  "generationConfig": { "responseModalities": ["IMAGE"] }
}
r = requests.post(url, json=body)
print(r.status_code)
open("test_img_resp.json", "w").write(r.text)
