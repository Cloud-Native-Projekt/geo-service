import requests
import sqlite3

# Overpass API query for Bayern: Einspeisepunkte (substations) and Stromleitungen (power lines)
overpass_url = "http://overpass-api.de/api/interpreter"
query = """
[out:json][timeout:60];
area["name"="Bayern"]["boundary"="administrative"]["admin_level"="4"]->.searchArea;
(
    node["power"="substation"](area.searchArea);
    way["power"="line"](area.searchArea);
    relation["power"="line"](area.searchArea);
);
out body;
>;
out skel qt;
"""

# Fetch data from Overpass API
response = requests.post(overpass_url, data={'data': query})
data = response.json()

# Create SQLite database and tables
conn = sqlite3.connect('bayern_power.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS substations (
        id INTEGER PRIMARY KEY,
        lat REAL,
        lon REAL,
        tags TEXT
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS power_lines (
        id INTEGER PRIMARY KEY,
        type TEXT,
        nodes TEXT,
        tags TEXT
)
''')

# Insert nodes (substations)
for element in data['elements']:
        if element['type'] == 'node' and element.get('tags', {}).get('power') == 'substation':
                c.execute(
                        'INSERT OR IGNORE INTO substations (id, lat, lon, tags) VALUES (?, ?, ?, ?)',
                        (element['id'], element['lat'], element['lon'], str(element.get('tags', {})))
                )

# Insert ways and relations (power lines)
for element in data['elements']:
        if element['type'] in ['way', 'relation'] and element.get('tags', {}).get('power') == 'line':
                nodes = str(element.get('nodes', element.get('members', [])))
                c.execute(
                        'INSERT OR IGNORE INTO power_lines (id, type, nodes, tags) VALUES (?, ?, ?, ?)',
                        (element['id'], element['type'], nodes, str(element.get('tags', {})))
                )

conn.commit()
conn.close()