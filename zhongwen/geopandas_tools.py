def show_map(gdf):
    '運用 folium 顯示 geopandas 資料框'
    from shapely.geometry import mapping
    from pathlib import Path
    import folium
    import os
    gdf = gdf.to_crs(epsg='4326')
    m = folium.Map(location=[gdf.centroid.y.mean(), gdf.centroid.x.mean()], zoom_start=10)

    for idx, row in gdf.iterrows():
        geojson = mapping(row.geometry)
        folium.GeoJson(geojson).add_to(m)

    html = Path.home() / 'TEMP' / 'output.html'
    m.save(html)
    os.system(f'start {html}')
