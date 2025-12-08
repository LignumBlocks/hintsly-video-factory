#!/usr/bin/env python3
"""
Verificación completa: Kie.ai Nano Banana (imagen) + Kie.ai Veo (video)
Tema: Cuba

IMPORTANTE: Este script requiere que el servidor FastAPI esté corriendo
para servir las imágenes públicamente.

Ejecutar en otra terminal:
  cd engine && uvicorn main:app --reload
"""
import sys
import os
import shutil
from pathlib import Path

# Add engine to path
sys.path.insert(0, os.path.join(os.getcwd(), "engine"))

from engine.domain.entities import Shot
from engine.usecases.process_shot import ProcessShot
from engine.usecases.utils_prompt import PromptService
from engine.adapters.fs_adapter import FSAdapter
from engine.adapters.gemini_client import KieNanoBananaClient
from engine.adapters.veo_client import KieVeoClient
from engine.adapters.logger import Logger
from dotenv import load_dotenv

# Load env variables
load_dotenv()

def verify_full_kie_pipeline():
    print("=" * 60)
    print("🇨🇺 VERIFICACIÓN COMPLETA KIE.AI - TEMA: CUBA")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ ERROR: KIE_API_KEY no encontrada en .env")
        return False
    
    print(f"✅ API Key encontrada: {api_key[:10]}...")
    
    # Check PUBLIC_BASE_URL
    public_url = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")
    print(f"✅ Public URL: {public_url}")
    print("\n⚠️  IMPORTANTE: Asegúrate de que el servidor FastAPI esté corriendo:")
    print("   cd engine && uvicorn main:app --reload\n")
    
    input("Presiona ENTER cuando el servidor esté listo...")

    # Cleanup previous test
    test_video_id = "cuba_kie_test_v1"
    assets_dir = Path("assets/videos") / test_video_id
    if assets_dir.exists():
        shutil.rmtree(assets_dir)
        print(f"🧹 Limpiado directorio anterior: {assets_dir}")

    # Initialize components
    print("\n📦 Inicializando componentes...")
    logger = Logger()
    fs = FSAdapter()
    prompts = PromptService()
    gemini = KieNanoBananaClient()
    veo = KieVeoClient()

    usecase = ProcessShot(fs, prompts, gemini, veo, logger)

    # Create test shot with Cuba theme
    shot = Shot(
        video_id=test_video_id,
        bloque="1",
        plano=1,
        descripcion_visual="A classic 1950s American car in vibrant teal color parked on a colorful street in Old Havana, Cuba. Colonial buildings with pastel facades in the background, warm golden hour lighting",
        movimiento_camara="Slow cinematic dolly forward approaching the car"
    )

    print(f"\n🎬 Shot a procesar:")
    print(f"   Video ID: {shot.video_id}")
    print(f"   Descripción: {shot.descripcion_visual[:60]}...")
    print(f"   Movimiento: {shot.movimiento_camara}")

    # Execute the full pipeline
    print("\n" + "=" * 60)
    print("🚀 EJECUTANDO PIPELINE COMPLETO")
    print("=" * 60)
    
    try:
        result = usecase.execute(shot)
    except Exception as e:
        print(f"\n❌ Error durante ejecución: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Check results
    print("\n" + "=" * 60)
    print("📊 RESULTADOS")
    print("=" * 60)
    
    print(f"Estado: {result.estado}")
    
    if result.estado == "ERROR":
        print(f"❌ Error: {result.error_message}")
        return False

    # Verify files
    files_to_check = [
        ("Imagen", result.image_path),
        ("Video", result.video_path),
        ("Metadata", str(Path(result.image_path).parent / "metadata.json") if result.image_path else None)
    ]
    
    all_exist = True
    for name, fpath in files_to_check:
        if fpath and os.path.exists(fpath):
            size = os.path.getsize(fpath)
            size_str = f"{size / 1024:.1f} KB" if size < 1024*1024 else f"{size / (1024*1024):.1f} MB"
            print(f"✅ {name}: {fpath} ({size_str})")
        else:
            print(f"❌ {name}: No encontrado - {fpath}")
            all_exist = False

    # Show prompts used
    print(f"\n📝 Prompts generados:")
    print(f"   Imagen: {result.prompt_imagen[:80]}...")
    print(f"   Video: {result.prompt_video[:80]}...")

    if all_exist:
        print("\n" + "=" * 60)
        print("✨ ¡VERIFICACIÓN EXITOSA! ✨")
        print(f"📁 Assets guardados en: {assets_dir}")
        print("=" * 60)
        return True
    else:
        print("\n⚠️  Verificación completada con archivos faltantes")
        return False

if __name__ == "__main__":
    success = verify_full_kie_pipeline()
    sys.exit(0 if success else 1)
