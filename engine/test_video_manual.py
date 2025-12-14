import sys
import os
import logging
from unittest.mock import MagicMock

# Add current directory to path
sys.path.append(os.getcwd())

from adapters.veo_client import KieVeoClient
from adapters.logger import Logger

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- CONFIGURATION ---
# Replace these with the URL and Prompt you want to test
IMAGE_URL = "https://engine.srv954959.hstgr.cloud/assets/catalog_files/HL_Core_Lab_Isometric_Main_v01.jpeg" 
VIDEO_PROMPT = "Add a cow, Cinematic slow zoom in, maintaining the dark institutional atmosphere."
# ---------------------

def run_manual_test():
    print("🚀 Starting MANUAL Veo Video Generation Test...")
    print(f"📷 Image URL: {IMAGE_URL}")
    print(f"🎬 Prompt: {VIDEO_PROMPT}")

    # Instantiate Client
    client = KieVeoClient()
    
    # --- MONKEY PATCHING ---
    # We want to bypass the local file check and URL conversion in _get_public_image_url
    # because we are providing a raw URL directly.
    print("🔧 Patching client to accept raw URL...")
    client._get_public_image_url = lambda path: path 
    
    try:
        # call generate (using the raw URL as the 'image_path' argument)
        video_data_uri = client.generate(IMAGE_URL, VIDEO_PROMPT)
        
        print("\n✅ Video Generation Successful!")
        print(f"📦 Data URI Length: {len(video_data_uri)} chars")
        
        # Save to file for verification
        output_file = "manual_test_video.mp4"
        import base64
        
        # Extract base64 part
        if "," in video_data_uri:
            b64_str = video_data_uri.split(",")[1]
            video_bytes = base64.b64decode(b64_str)
            
            with open(output_file, "wb") as f:
                f.write(video_bytes)
                
            print(f"💾 Video saved to: {output_file}")
            print(f"   Size: {len(video_bytes)} bytes")
            
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_manual_test()
