#!/usr/bin/env python3
"""
Verificación de Kie.ai Veo API (text-to-video)
"""
import sys
import os

# Add engine to path
sys.path.insert(0, os.path.join(os.getcwd(), "engine"))

from engine.adapters.veo_client import KieVeoClient
from dotenv import load_dotenv

# Load env variables
load_dotenv()

def verify_kie_veo():
    print("=" * 60)
    print("🎬 VERIFICACIÓN KIE.AI VEO API")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ ERROR: KIE_API_KEY no encontrada en .env")
        return False
    
    print(f"✅ API Key encontrada: {api_key[:10]}...")

    # Initialize client
    print("\n📦 Inicializando cliente Kie.ai Veo...")
    client = KieVeoClient()

    # Test prompt
    prompt = "A vintage Cuban car in bright turquoise color driving slowly through a colorful street in Old Havana, smooth camera dolly forward movement, cinematic, golden hour lighting, 4k"
    
    print(f"\n🎨 Prompt: {prompt[:60]}...")
    print("\n🚀 Generando video...")
    print("(Esto puede tomar 2-5 minutos)\n")

    try:
        # Generate video (text-to-video since we don't have image URL upload yet)
        # Passing empty string for image_path to use text-to-video
        video_data = client.generate("", prompt)
        
        # Save to file for verification
        import base64
        header, encoded = video_data.split(",", 1)
        video_bytes = base64.b64decode(encoded)
        
        filename = "kie_veo_test_video.mp4"
        with open(filename, "wb") as f:
            f.write(video_bytes)
        
        size_mb = len(video_bytes) / (1024 * 1024)
        
        print("=" * 60)
        print("✨ ¡VERIFICACIÓN EXITOSA! ✨")
        print("=" * 60)
        print(f"✅ Video generado: {filename}")
        print(f"✅ Tamaño: {size_mb:.1f} MB")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante generación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_kie_veo()
    sys.exit(0 if success else 1)
