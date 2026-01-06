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
    from shapely.geometry import mapping
    from folium.features import GeoJsonPopup
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

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-x", type=float, help="緯度")
    parser.add_argument("-y", type=float, help="經度")
    args = parser.parse_args()
    if args.x and args.y:
        顯示座標(args.x, args.y)
