import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load env vars
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
ENDPOINT = os.getenv("GEMINI_IMAGE_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent")

if not API_KEY:
    print("❌ Error: GEMINI_API_KEY not found in .env")
    print("Please create a .env file with GEMINI_API_KEY=...")
    sys.exit(1)

print(f"🔑 API Key found: {API_KEY[:5]}...")
print(f"🌐 Endpoint: {ENDPOINT}")

def test_generation():
    url = f"{ENDPOINT}?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": "A futuristic city with neons, cinematic style, 8k"}]
        }]
    }
    
    print("\n🚀 Sending request...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response JSON:", json.dumps(data, indent=2))
            
            # Inspect structure
            candidates = data.get("candidates", [])
            if not candidates:
                print("❌ No candidates found.")
                return
            
            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                if "inlineData" in part:
                    print("✅ Image data found (Base64)!")
                    mime = part["inlineData"]["mimeType"]
                    print(f"   Mime: {mime}")
                    print(f"   Data length: {len(part['inlineData']['data'])} chars")
                    
                    # Save image
                    import base64
                    try:
                        image_data = base64.b64decode(part['inlineData']['data'])
                        filename = "gemini_test_image.jpeg"
                        with open(filename, "wb") as f:
                            f.write(image_data)
                        print(f"💾 Saved image to {filename}")
                    except Exception as save_err:
                        print(f"❌ Failed to save image: {save_err}")
                elif "text" in part:
                    print(f"⚠️  Received Text: {part['text']}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_generation()
