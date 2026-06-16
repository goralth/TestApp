from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import random
import time
import threading

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def index():
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Live Leaflet Map with Flask-SocketIO</title>
        <style>
            #map { height: 500px; width: 100%; margin-top: 20px; }
            button { padding: 10px 20px; font-size: 16px; margin: 5px; }
        </style>
        <!-- Leaflet CSS -->
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    </head>
    <body>
        <h2>🗺️ Live Markers (Open in 2+ Tabs)</h2>
        <button id="addBtn">➕ Add Random Point</button>
        <button id="clearBtn">🗑️ Clear Points</button>
        <div id="status">Connecting...</div>
        <div id="map"></div>

        <!-- Leaflet JS -->
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <!-- Socket.IO -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>

        <script>
            // Create Leaflet map centered at Dubai
            var map = L.map('map').setView([25.2048, 55.2708], 11);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

            // Add static Dubai marker
            L.marker([25.2048, 55.2708]).bindPopup('Dubai Center').addTo(map);

            var liveMarkers = [];
            var statusDiv = document.getElementById('status');
            var socket = io();

            // WebSocket connect
            socket.on('connect', function() {
                statusDiv.innerHTML = '✅ Connected - Live Ready!';
            });

            // On new point, add marker on map
            socket.on('new_point', function(data) {
                console.log('📍 New point:', data);
                var marker = L.marker([data.geometry.coordinates[1], data.geometry.coordinates[0]])
                    .bindPopup(`<b>${data.properties.name}</b>`)
                    .addTo(map);
                liveMarkers.push(marker);
                marker.openPopup();
                setTimeout(() => marker.closePopup(), 2000);
            });

            // On clear command, remove all live markers
            socket.on('clear_points', function() {
                console.log('🗑️ Clearing markers');
                liveMarkers.forEach(marker => map.removeLayer(marker));
                liveMarkers = [];
            });

            // Button handlers emit socket messages
            document.getElementById('addBtn').onclick = function() {
                socket.emit('request_point');
            };
            document.getElementById('clearBtn').onclick = function() {
                socket.emit('clear_points');
            };
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@socketio.on("request_point")
def handle_request_point():
    new_point = {
        "type": "Feature",
        "properties": {"name": f"Live Point {int(time.time())}"},
        "geometry": {
            "type": "Point",
            "coordinates": [
                55.25 + random.uniform(-0.05, 0.05),
                25.20 + random.uniform(-0.05, 0.05),
            ],
        },
    }
    emit("new_point", new_point, broadcast=True)

@socketio.on("clear_points")
def handle_clear_points():
    emit("clear_points", {}, broadcast=True)

def background_live_updates():
    while True:
        time.sleep(10)
        fake_sensor_data = {
            "type": "Feature",
            "properties": {"name": "Sensor Update", "value": round(random.uniform(10, 100), 2)},
            "geometry": {"type": "Point", "coordinates": [55.28, 25.22]},
        }
        socketio.emit("new_point", fake_sensor_data, broadcast=True)

if __name__ == "__main__":
    threading.Thread(target=background_live_updates, daemon=True).start()
    socketio.run(app, debug=True, port=5000)
