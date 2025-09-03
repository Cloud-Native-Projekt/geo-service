params_protected_area = {
    "lng": 11.0605066,
    "lat": 49.4857068,
}
params_in_forest = {
    "lng": 7.8325,
    "lat": 49.1508
}
"""
"type": "relation",
  "id": 287997,
 "bounds": {
    "minlat": 49.4857066,
    "minlon": 11.0605060,
    "maxlat": 49.5149067,
    "maxlon": 11.1281047
  },
  "tags": {
    "boundary": "protected_area",
    "loc_ref": "325.520",
    "name": "Kraftshofer Forst",
    "protect_class": "5",
    "protection_title": "Landschaftsschutzgebiet",
    "source": "Verordnung vom 22.7.2005 mit Anlage 8.1",
    "type": "multipolygon",
    "wikidata": "Q59528003"
  }"""
def test_get_power_infrastructure(test_app):
    response = test_app.get("/geo/power", params=test_params)
    assert response.status_code == 200
    data = response.json()
    expected_keys = [
        "nearest_substation_distance_m",
        "nearest_powerline_distance_m",
    ]
    for key in expected_keys:
        assert key in data

def test_get_forest_overlap(test_app):
    response = test_app.get("/geo/forest", params=params_in_forest)
    assert response.status_code == 200
    data = response.json()
    expected_keys = [
        "forest_coverage_percent",
    ]
    for key in expected_keys:
        assert key in data

def test_get_protected_areas(test_app):
    response = test_app.get("/geo/protection", params=params_protected_area)
    assert response.status_code == 200
    data = response.json()
    expected_keys = [
        "in_protected_area",
    ]
    for key in expected_keys:
        assert key in data

def test_get_buildings_in_area(test_app):
    response = test_app.get("/geo/builtup", params=test_params)
    assert response.status_code == 200
    data = response.json()
    expected_keys = [
        "urban_building_density",
        "on_existing_building",
    ]
    for key in expected_keys:
        assert key in data
