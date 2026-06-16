from pathlib import Path
import re
import json
import csv

text = Path("paste.txt").read_text(encoding="utf-8")

pairs = re.findall(r'(-95\.\d+),30\.(\d+)', text)

features = []
for lon_s, lat_tail in pairs:
    lat_match = re.search(rf'{re.escape(lon_s)},(30\.{lat_tail})', text)
    if lat_match:
        lon = float(lon_s)
        lat = float(lat_match.group(1))
        features.append({
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            }
        })

geojson = {
    "type": "FeatureCollection",
    "name": "bridgesGeoJSON",
    "crs": {
        "type": "name",
        "properties": {
            "name": "EPSG:4326"
        }
    },
    "features": features
}

out = Path("output")
out.mkdir(exist_ok=True)

geojson_file = out / "cleaned_geojson.geojson"
geojson_file.write_text(json.dumps(geojson, indent=2), encoding="utf-8")

summary_csv = out / "cleaned_geojson_summary.csv"
with summary_csv.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["feature_count"])
    w.writerow([len(features)])

print("features", len(features))
print("saved", geojson_file, summary_csv)