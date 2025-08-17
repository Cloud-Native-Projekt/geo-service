import json

from fastapi.testclient import TestClient

from geo_cond_service.main import app

client = TestClient(app)

def test_geo_evaluate_success():
    payload = {
        "lon": 7.8325,
        "lat": 49.1508,
        "radius_km": 3,
        "geo_cond_id": 1,
        "geo_cond_name": "Test Condition"
    }

    response = client.post("http://localhost:8000/geo-cond", json=payload)
    
    assert response.status_code == 200
    data = response.json()

    assert "near_powerline" in data
    assert "has_substation" in data
    assert "in_nature_reserve" in data
    assert "forest_coverage_percent" in data
    assert "urban_building_density" in data
    assert "on_existing_building" in data

    # Beispiel: sinnvolle Werte prüfen
    assert isinstance(data["near_powerline"], bool)
    assert isinstance(data["has_substation"], bool)
    
    print(data)
