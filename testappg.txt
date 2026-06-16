# Complete Flask App: Interactive GIS Dashboard with Charts + Map
# Uses your pandas data + Plotly charts + Folium map
# pip install flask plotly pandas numpy folium

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
import json
import plotly.utils
from flask import Flask, render_template_string

app = Flask(__name__)

# Your GIS sample data (Bangalore flood zones + revenue)
def generate_gis_data():
    np.random.seed(42)
    dates = pd.date_range('2025-01-01', periods=200, freq='D')
    regions = np.random.choice(['Bangalore North', 'Bangalore South', 'Bangalore East', 'Mumbai'], 200)
    lat = np.random.normal(12.97, 0.05, 200)  # Bangalore coords
    lon = np.random.normal(77.59, 0.05, 200)
    revenue = np.random.uniform(5000, 100000, 200)
    flood_risk = np.random.choice(['Low', 'Medium', 'High'], 200, p=[0.5, 0.3, 0.2])
    
    df = pd.DataFrame({
        'date': dates, 
        'region': regions, 
        'lat': lat, 
        'lon': lon,
        'revenue': revenue,
        'flood_risk': flood_risk
    })
    return df

@app.route('/')
def dashboard():
    df = generate_gis_data()
    
    # Chart 1: Revenue by Region (Bar)
    region_rev = df.groupby('region')['revenue'].sum().reset_index()
    fig1 = px.bar(region_rev, x='region', y='revenue', 
                  title='Total Revenue by Region',
                  color='revenue', color_continuous_scale='Viridis')
    
    # Chart 2: Flood Risk Distribution (Pie)
    risk_dist = df['flood_risk'].value_counts().reset_index()
    fig2 = px.pie(risk_dist, values='count', names='flood_risk',
                  title='Flood Risk Distribution')
    
    # Chart 3: Revenue vs Time (Line)
    df_monthly = df.groupby(df['date'].dt.to_period('M'))['revenue'].sum().reset_index()
    df_monthly['month'] = df_monthly['date'].astype(str)
    fig3 = px.line(df_monthly, x='month', y='revenue',
                   title='Monthly Revenue Trend')
    
    # Folium Map with markers
    m = folium.Map(location=[12.97, 77.59], zoom_start=11)
    for idx, row in df.head(50).iterrows():  # First 50 points
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=5,
            popup=f"{row['region']}<br>₹{row['revenue']:,.0f}<br>{row['flood_risk']}",
            color='red' if row['flood_risk']=='High' else 'orange',
            fill=True
        ).add_to(m)
    
    # Convert to HTML
    map_html = m._repr_html_()
    graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Summary stats
    total_revenue = df['revenue'].sum()
    high_risk_count = (df['flood_risk'] == 'High').sum()
    
    template = '''
    <!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <title>GIS Dashboard - Bangalore Revenue & Flood Risk</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        .chart-container { width: 48%; display: inline-block; margin: 1%; height: 400px; }
        .map-container { width: 100%; height: 500px; margin: 20px 0; }
        .stats { background: #f0f0f0; padding: 20px; margin: 20px 0; }
        h2 { color: #333; }
    </style>
</head>
<body>
    <h1>🏙️ Bangalore GIS Dashboard</h1>
    
    <div class="stats">
        <h3>Key Metrics</h3>
        <p>Total Revenue: ₹{{ total_revenue|round(0)|int }}</p>
        <p>High Risk Zones: {{ high_risk_count }}</p>
        <p>Total Records: {{ df_rows }}</p>
    </div>
    
    <div class="chart-container">
        <h2>Revenue by Region</h2>
        <div id="chart1" style="width:100%;height:100%;"></div>
    </div>
    
    <div class="chart-container">
        <h2>Flood Risk</h2>
        <div id="chart2" style="width:100%;height:100%;"></div>
    </div>
    
    <div style="clear:both;"></div>
    
    <div class="chart-container" style="width:100%;">
        <h2>Monthly Trend</h2>
        <div id="chart3" style="width:100%;height:400px;"></div>
    </div>
    
    <div class="map-container">
        <h2>Flood Risk Map</h2>
        {{ map_html|safe }}
    </div>
    
    <script>
        // Chart 1: Revenue by Region
        var graph1 = {{ graphJSON1 | safe }};
        Plotly.newPlot('chart1', graph1.data, graph1.layout || {});
        
        // Chart 2: Flood Risk Pie
        var graph2 = {{ graphJSON2 | safe }};
        Plotly.newPlot('chart2', graph2.data, graph2.layout || {});
        
        // Chart 3: Monthly Trend
        var graph3 = {{ graphJSON3 | safe }};
        Plotly.newPlot('chart3', graph3.data, graph3.layout || {});
    </script>
</body>
</html>
    '''
    
    return render_template_string(template, 
                                graphJSON1=graphJSON1,
                                graphJSON2=graphJSON2,
                                graphJSON3=graphJSON3,
                                map_html=map_html,
                                total_revenue=total_revenue,
                                high_risk_count=high_risk_count,
                                df_rows=len(df))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
