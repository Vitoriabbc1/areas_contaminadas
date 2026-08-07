import os
import webbrowser
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import psycopg2
import folium

# ==============================================================================
# 1. Conexão com o banco PostGIS
# ==============================================================================
conn_params = {
    "dbname": "geo_db",
    "user": "admin",
    "password": "adminpassword",
    "host": "localhost",
    "port": "5433",
}

conn = psycopg2.connect(**conn_params)

# ==============================================================================
# 2. Query do Gráfico (Quantitativo)
# ==============================================================================
query_grafico = """
SELECT 
    ap.nome AS area_protegida,
    ap.tipo AS tipo_unidade,
    COUNT(ac.objectid) AS total_focos
FROM public.areas_protegidas ap
JOIN public.areas_contaminadas ac 
  ON ST_DWithin(ST_Transform(ap.geom, 31983), ST_Transform(ac.geom, 31983), 500)
GROUP BY ap.nome, ap.tipo
ORDER BY total_focos DESC;
"""

df_grafico = pd.read_sql(query_grafico, conn)

# Lógica SWD (Destaque do valor máximo)
max_focos = df_grafico['total_focos'].max()
uc_max_focos = df_grafico.loc[df_grafico['total_focos'].idxmax(), 'area_protegida']
color_list = ['#D32F2F' if x == max_focos else '#B0BEC5' for x in df_grafico['total_focos']]

fig = go.Figure(go.Bar(
    x=df_grafico['total_focos'],
    y=df_grafico['area_protegida'],
    orientation='h',
    marker=dict(color=color_list),
    text=df_grafico['total_focos'],
    textposition='outside',
    textfont=dict(size=11, family='Fira Code, monospace')
))

titulo_swd = f"🚨 <b style='color:#D32F2F;'>{uc_max_focos}</b> lidera os focos de contaminação a até 500m"

fig.update_layout(
    title={'text': titulo_swd, 'x': 0.0, 'y': 0.95, 'xanchor': 'left', 'font': dict(size=18, family='Fira Code, monospace')},
    margin=dict(l=220, r=40, t=70, b=40),
    height=800,
    plot_bgcolor='#FAFAFA',
    paper_bgcolor='white',
    xaxis={
        'showgrid': True,
        'gridcolor': '#E0E0E0',
        'gridwidth': 1,
        'title': {'text': 'Total de Focos de Contaminação'},
        'dtick': 2
    },
    yaxis={'showgrid': True, 'gridcolor': '#F5F5F5', 'categoryorder': 'total ascending', 'title': None},
    showlegend=False
)

grafico_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

# ==============================================================================
# 3. Gerar o Mapa Folium a partir dos dados do PostGIS
# ==============================================================================
query_mapa = """
SELECT ap.nome, ap.tipo, ST_Transform(ap.geom, 4326) as geom 
FROM public.areas_protegidas ap
"""
gdf_ap = gpd.read_postgis(query_mapa, conn, geom_col='geom')

query_focos = """
SELECT ac.objectid, ST_Transform(ac.geom, 4326) as geom 
FROM public.areas_contaminadas ac
"""
gdf_focos = gpd.read_postgis(query_focos, conn, geom_col='geom')

conn.close()

# Criar o mapa centralizado no Rio de Janeiro
m = folium.Map(location=[-22.9068, -43.1729], zoom_start=11, tiles="CartoDB positron")

# Adicionar a camada GeoJSON de Áreas Protegidas
folium.GeoJson(
    gdf_ap,
    name="Áreas Protegidas",
    style_function=lambda x: {
        'fillColor': '#4CAF50',
        'color': '#2E7D32',
        'weight': 1,
        'fillOpacity': 0.4
    },
    tooltip=folium.GeoJsonTooltip(fields=['nome', 'tipo'], aliases=['Área:', 'Tipo:'])
).add_to(m)

# Adicionar Focos de Contaminação como marcadores
for _, row in gdf_focos.iterrows():
    folium.CircleMarker(
        location=[row.geom.y, row.geom.x],
        radius=4,
        color="#D32F2F",
        fill=True,
        fill_color="#D32F2F",
        fill_opacity=0.7,
        popup=f"Foco ID: {row['objectid']}"
    ).add_to(m)

folium.LayerControl().add_to(m)

# Salvar o mapa interativo
m.save("mapa.html")

# ==============================================================================
# 4. Montar e Abrir a Dashboard com Fonte Monospace (Fira Code / Linux)
# ==============================================================================
html_dashboard = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Painel de Análise Ambiental - RJ</title>
    <!-- Importação direta da fonte Fira Code -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&display=swap" rel="stylesheet">
    
    <style>
        body {{ 
            font-family: 'Fira Code', monospace; 
            background-color: #F4F6F8; 
            margin: 0; 
            padding: 20px; 
            color: #111111;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        
        .header-title {{
            background: #FFFFFF;
            padding: 25px 30px;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        .header-title h1 {{
            margin: 0;
            font-size: 30px;
            font-weight: 700;
            letter-spacing: -0.5px;
            font-family: 'Fira Code', monospace;
            color: #000000;
        }}
        .header-title p {{
            margin: 8px 0 0 0;
            font-size: 15px;
            font-weight: 400;
            font-family: 'Fira Code', monospace;
            color: #333333;
        }}

        .card {{ 
            background: white; 
            border-radius: 8px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.05); 
            padding: 20px; 
            margin-bottom: 25px; 
        }}
        .card-header h2 {{ 
            margin: 0 0 15px 0; 
            font-size: 20px; 
            color: #2C3E50; 
            font-weight: 500;
            font-family: 'Fira Code', monospace;
        }}
        iframe {{ width: 100%; height: 600px; border: none; border-radius: 6px; }}
    </style>
</head>
<body>
    <div class="container">
        
        <!-- Título Estilo Monospace Terminal -->
        <div class="header-title">
            <h1>Conflito Espacial em Unidades de Conservação</h1>
            <p>Diagnóstico Geoespacial de Vulnerabilidade a Passivos Ambientais no Município do Rio de Janeiro</p>
        </div>

        <!-- Bloco do Gráfico -->
        <div class="card">
            {grafico_html}
        </div>

        <!-- Bloco do Mapa -->
        <div class="card">
            <div class="card-header">
                <h2> Distribuição Espacial: Áreas Protegidas e Focos de Contaminação</h2>
            </div>
            <iframe src="mapa.html"></iframe>
        </div>
    </div>
</body>
</html>
"""

with open("dashboard_ambiental.html", "w", encoding="utf-8") as f:
    f.write(html_dashboard)

print("Abrindo no navegador...")
webbrowser.open("file://" + os.path.realpath("dashboard_ambiental.html"))
