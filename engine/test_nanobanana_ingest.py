import sys
import os
import json
from fastapi.testclient import TestClient

# Add current directory to path
sys.path.append(os.getcwd())

from main import app
from domain.nanobanana_models import NanoBananaRequest

client = TestClient(app)

def test_ingest_nanobanana():
    # Load the JSON file
    # Assuming running from engine directory or similar context
    # Adjust path relative to where we run the test
    json_path = "../context/shot_v3/NanoBananaPro.txt"
    if not os.path.exists(json_path):
        # try absolute path fallback
        json_path = "/home/roiky/Espacio/hintsly-video-factory/context/shot_v3/NanoBananaPro.txt"
    
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    # Send POST request
    response = client.post("/nanobanana/ingest", json=data)
    
    # Assertions
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["project_id"] == data["project"]["project_id"]
    print("✅ NanoBanana Ingestion Test Passed!")

if __name__ == "__main__":
    test_ingest_nanobanana()
