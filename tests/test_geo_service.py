from fastapi.testclient import TestClient

from geo_service.main import app

# sys.path.append(str(Path(__file__).resolve().parent.parent))
client = TestClient(app)

test_params = {
    "lng": 7.8325,
    "lat": 49.1508,
    "radius": 3000,
}


def test_get_power_infrastructure():

    response = client.get("/geo/power", params=test_params)

    assert response.status_code == 200
    data = response.json()

    expected_keys = [
        "nearest_substation_distance_m",
        "nearest_powerline_distance_m",
    ]
    for key in expected_keys:
        assert key in data


def test_get_forest_overlap():

    response = client.get("/geo/forest", params=test_params)

    assert response.status_code == 200
    data = response.json()

    expected_keys = [
        "forest_coverage_percent",
    ]
    for key in expected_keys:
        assert key in data


def test_get_protected_areas():

    response = client.get("/geo/protection", params=test_params)

    assert response.status_code == 200
    data = response.json()

    expected_keys = [
        "in_protected_area",
    ]
    for key in expected_keys:
        assert key in data


def test_get_buildings_in_area():

    response = client.get("/geo/builtup", params=test_params)

    assert response.status_code == 200
    data = response.json()

    expected_keys = [
        "urban_building_density",
        "on_existing_building",
    ]
    for key in expected_keys:
        assert key in data
