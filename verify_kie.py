#!/usr/bin/env python3
"""
Verificación de Kie.ai Nano Banana API
"""
import sys
import os

# Add engine to path
sys.path.insert(0, os.path.join(os.getcwd(), "engine"))

from engine.adapters.gemini_client import KieNanoBananaClient
from dotenv import load_dotenv

# Load env variables
load_dotenv()

def verify_kie_api():
    print("=" * 60)
    print("🍌 VERIFICACIÓN KIE.AI NANO BANANA API")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ ERROR: KIE_API_KEY no encontrada en .env")
        print("\nPor favor agrega tu clave en el archivo .env:")
        print("KIE_API_KEY=tu_clave_aqui")
        return False
    
    print(f"✅ API Key encontrada: {api_key[:10]}...")

    # Initialize client
    print("\n📦 Inicializando cliente Kie.ai...")
    client = KieNanoBananaClient()

    # Test prompt
    prompt = "A vintage Cuban car in bright turquoise color parked on a colorful street in Havana, golden hour lighting, photorealistic, 8k"
    
    print(f"\n🎨 Prompt: {prompt[:60]}...")
    print("\n🚀 Generando imagen...")
    print("(Esto puede tomar 30-60 segundos)\n")

    try:
        # Generate image
        image_data = client.generate(prompt)
        
        # Save to file for verification
        import base64
        header, encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        
        filename = "kie_test_image.png"
        with open(filename, "wb") as f:
            f.write(image_bytes)
        
        size_kb = len(image_bytes) / 1024
        
        print("=" * 60)
        print("✨ ¡VERIFICACIÓN EXITOSA! ✨")
        print("=" * 60)
        print(f"✅ Imagen generada: {filename}")
        print(f"✅ Tamaño: {size_kb:.1f} KB")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante generación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_kie_api()
    sys.exit(0 if success else 1)
