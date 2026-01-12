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

def 顯示地點(gdf, 編號欄位='編號'):
    from shapely.geometry import Point
    import geopandas as gpd
    import folium
    import os

    if 編號欄位 not in gdf.columns:
        gdf[編號欄位] = gdf.index

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
        tooltip=folium.GeoJsonTooltip(fields=[編號欄位], aliases=['編號：']), # 懸停顯示編號
        popup=folium.GeoJsonPopup(fields=popup_fields), # 點擊彈出所有欄位表格
    ).add_to(m)

    # 4. 繪製帶有數字編號的實心圓
    for _, row in gdf.iterrows():
        # 使用 DivIcon 自定義 HTML/CSS 畫出實心圓與文字
        icon_html = f"""
        <div style="
            background-color: #0078FF;
            border: 2px solid white;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 12px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        ">
            {row[編號欄位]}
        </div>
        """
        columns_to_show = gdf.columns.drop('geometry').tolist()
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            icon=folium.DivIcon(
                icon_size=(30, 30),
                icon_anchor=(15, 15),
                html=icon_html
            ),
            # 綁定自動生成的表格 Popup
            popup=folium.Popup(row[columns_to_show].to_frame().to_html(classes="table table-striped"), max_width=300)
        ).add_to(m)
    html = os.path.join(os.environ['TEMP'], "顯示地圖.html")
    m.save(html)
    os.system(f'start {html}')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-x", type=float, help="經度")
    parser.add_argument("-y", type=float, help="緯度")
    args = parser.parse_args()
    if args.x and args.y:
        顯示座標(args.y, args.x)
