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

    for col in gdf.columns:
        # 檢查該欄位中是否有任何值是 set 類型
        if gdf[col].apply(lambda x: isinstance(x, set)).any():
            gdf[col] = gdf[col].apply(lambda x: list(x) if isinstance(x, set) else x)
            # 註：轉成 list 後 JSON 就能識別了；若要顯示好看，建議用上面方法一的 ', '.join()

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

def 顯示互動地圖(gdf, 數值欄位=None, 分類欄位=None, 圖例名稱=None, 變色範圍='四分位數', 顯示圖例=False):
    """
    使用 explore 顯示交互式地圖。
    - 支援無數值欄位模式（僅顯示分類或單色）。
    - 點擊路段會彈出包含「所有欄位」的視窗。
    """
    import numpy as np
    import webbrowser
    import os
    import tempfile
    import matplotlib.colors as mcolors
    if gdf is None or gdf.empty:
        print("資料為空")
        return None

    # 1. 處理數值映射邏輯 (僅在有數值欄位時執行)
    vmin, vmax = None, None
    if 數值欄位 and 數值欄位 in gdf.columns:
        if 變色範圍 == '四分位數':
            vmin = gdf[數值欄位].quantile(0.25)
            vmax = gdf[數值欄位].quantile(0.75)
        elif 變色範圍 == '眾數':
            mode_series = gdf[數值欄位].mode()
            眾數 = mode_series.iloc[0] if not mode_series.empty else gdf[數值欄位].median()
            std = gdf[數值欄位].std()
            vmin = max(gdf[數值欄位].min(), 眾數 - 0.5 * std)
            vmax = min(gdf[數值欄位].max(), 眾數 + 0.5 * std)
        else:
            vmin, vmax = gdf[數值欄位].min(), gdf[數值欄位].max()

        if vmin is not None and vmax is not None and vmin >= vmax:
            vmin, vmax = gdf[數值欄位].min(), gdf[數值欄位].max()
            if vmin == vmax: vmax += 1

    # 2. 核心繪圖邏輯
    # 判斷要使用的顏色欄位（優先用分類，次之用數值）
    color_col = 分類欄位 if 分類欄位 else 數值欄位
    
    # 建立樣式函數 (只有在同時有 分類 與 數值 時才啟用透明度映射)
    style_kwds = {'weight': 5}
    if 分類欄位 and 數值欄位 and 數值欄位 in gdf.columns:
        categories = gdf[分類欄位].unique()
        colors = list(mcolors.TABLEAU_COLORS.values())
        color_map = {cat: colors[i % len(colors)] for i, cat in enumerate(categories)}
        
        def style_fn(feature):
            val = feature['properties'].get(數值欄位, 0)
            cat = feature['properties'].get(分類欄位, None)
            # 透明度映射
            norm_val = (val - vmin) / (vmax - vmin) if (vmax - vmin) != 0 else 1.0
            alpha = float(np.clip(norm_val, 0.4, 1.0)) 
            return {
                "color": color_map.get(cat, "#3388ff"),
                "weight": 5,
                "opacity": alpha
            }
        style_kwds["style_function"] = style_fn

    # 3. 呼叫 explore
    m = gdf.explore(
        column=color_col,
        cmap="YlOrRd" if 數值欄位 and not 分類欄位 else None, # 僅數值模式用色階
        vmin=vmin,
        vmax=vmax,
        tiles="OpenStreetMap", 
        legend=顯示圖例,
        tooltip=True,      
        popup=True,        # 彈出所有欄位
        style_kwds=style_kwds
    )

    # 4. 儲存與自動開啟
    fd, path = tempfile.mkstemp(suffix='.html')
    try:
        m.save(path)
        webbrowser.open(f'file://{os.path.realpath(path)}')
    finally:
        os.close(fd)

    return m

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-x", type=float, help="經度")
    parser.add_argument("-y", type=float, help="緯度")
    args = parser.parse_args()
    if args.x and args.y:
        顯示座標(args.y, args.x)
