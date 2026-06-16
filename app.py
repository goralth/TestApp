from flask import Flask
import folium
import json
import os

app = Flask(__name__)

@app.route("/")
def index():
    # Create base map (Dubai as example)
    m = folium.Map(location=[25.2048, 55.2708], zoom_start=11)

    # 1) Add a simple marker (optional)
    folium.Marker(
        [25.2048, 55.2708],
        popup="Dubai Center",
        tooltip="Click me"
    ).add_to(m)

    # 2) Load local GeoJSON file
    geojson_path = os.path.join(os.path.dirname(__file__), "data.geojson")
    with open(geojson_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # 3) Add GeoJSON as a new layer
    folium.GeoJson(
        geojson_data,
        name="My layer"
    ).add_to(m)

    # 4) Optional: layer control to toggle on/off
    folium.LayerControl().add_to(m)

    # 5) Return map HTML
    return m._repr_html_()

if __name__ == "__main__":
    app.run(debug=True)
