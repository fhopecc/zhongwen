def 顯示座標(緯度, 經度): 
    import folium
    import os

    # 1. 設定中心點座標 [緯度, 經度]
    location = [緯度, 經度]

    # 2. 建立地圖物件
    # zoom_start 是初始縮放層級，數字越大越近
    m = folium.Map(location=location, zoom_start=16)

    # 3. 在該座標加上圖釘 (Marker)
    folium.Marker(
        location=location,
        popup="台北 101",        # 點擊圖釘後顯示的文字
        tooltip="點擊查看更多"   # 滑鼠游標懸停時顯示的文字
    ).add_to(m)

    # 4. 儲存成 HTML 檔案或直接顯示
    html = os.path.join(os.environ['TEMP'], "顯示地圖.html")
    m.save(html)
    os.system(f'start {html}')

def 顯示地圖(gdf):
    '''
    一、運用 folium 顯示 geopandas 資料框。
    二、點選各圖徵彈出屬性窗。
    '''
    from folium.features import GeoJsonPopup
    from shapely.geometry import mapping
    from pathlib import Path
    import tempfile
    import folium
    import time
    import os
    gdf = gdf.to_crs(epsg='4326')
    m = folium.Map(location=[gdf.centroid.y.mean(), gdf.centroid.x.mean()], zoom_start=10)
    fields = gdf.columns.tolist()
    fields.remove('geometry')
    popup = GeoJsonPopup(
        fields=fields,
        aliases=fields,
        localize=True,
        labels=True
    )
    folium.GeoJson(
        gdf,
        popup=popup
    ).add_to(m)
    html = os.path.join(os.environ['TEMP'], "顯示地圖.html")
    m.save(html)
    os.system(f'start {html}')

def 顯示地點(gdf):
    import geopandas as gpd
    import folium
    from shapely.geometry import Point

    # 2. 初始化地圖，中心點設為數據的中心
    avg_lat = gdf.geometry.y.mean()
    avg_lon = gdf.geometry.x.mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)

    # 3. 使用 GeoJson 顯示圓點與彈出表格
    # 我們利用 marker_options 讓它顯示為圓點 (CircleMarker)
    popup_fields = gdf.columns.drop('geometry').tolist() # 取得所有欄位名稱（排除幾何欄位）

    folium.GeoJson(
        gdf,
        marker=folium.CircleMarker(
            radius=8,
            fill=True,
            fill_color="blue",
            color="white",
            weight=1
        ),
        tooltip=folium.GeoJsonTooltip(fields=[id_column], aliases=['編號：']), # 懸停顯示編號
        popup=folium.GeoJsonPopup(fields=popup_fields), # 點擊彈出所有欄位表格
    ).add_to(m)

    # 4. 如果你想在圓點旁邊直接標註「數字」（文字標籤）
    # Folium 的 GeoJson 目前不支援直接渲染 text 標籤，通常需手動迴圈添加 Marker
    for idx, row in gdf.iterrows():
        folium.map.Marker(
            [row.geometry.y, row.geometry.x],
            icon=folium.DivIcon(
                icon_size=(150,36),
                icon_anchor=(0,0),
                html=f'<div style="font-size: 12pt; color: red; font-weight: bold;">{row[id_column]}</div>',
            )
        ).add_to(m)

    return m

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-x", type=float, help="經度")
    parser.add_argument("-y", type=float, help="緯度")
    args = parser.parse_args()
    if args.x and args.y:
        顯示座標(args.y, args.x)
