from diskcache import Cache
from pathlib import Path

cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

@cache.memoize('載入鄉鎮市區界線')
def 載入鄉鎮市區界線(鄉鎮市區界線圖檔):
    """
    一、載入內政部國土測繪中心鄉鎮市區界線圖檔。
    二、下載網址：https://data.gov.tw/dataset/7441
    三、圖檔座標系：TWD 97(EPSG 3826)。
    """
    import geopandas as gpd
    import os
    shp_path = 鄉鎮市區界線圖檔
    print(f"正在載入圖資：{os.path.basename(shp_path)}")
    try:
        gdf = gpd.read_file(shp_path)
        # 內政部圖資若未標註 CRS，通常是 TWD97 (EPSG:3826)
        if gdf.crs is None:
            print("警告：圖資未包含座標系統資訊，手動設定為 EPSG:3826 (TWD97)。")
            gdf.set_crs(epsg=3826, inplace=True)
        return gdf
    except Exception as e:
        print(f"載入失敗: {e}")
        return None

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
    import folium
    import os

    if 編號欄位 not in gdf.columns:
        gdf[編號欄位] = gdf.index

    # 2. 初始化地圖，中心點設為數據的中心
    avg_lat = gdf.geometry.y.mean()
    avg_lon = gdf.geometry.x.mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)

    # 3. 使用 GeoJson 顯示圓點與彈出表格
    popup_fields = gdf.columns.drop('geometry').tolist() # 取得所有欄位名稱（排除幾何欄位）

    for col in gdf.columns:
        # 檢查該欄位中是否有任何值是 set 類型
        if gdf[col].apply(lambda x: isinstance(x, set)).any():
            gdf[col] = gdf[col].apply(lambda x: list(x) if isinstance(x, set) else x)

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

def 顯示互動地圖(gdf, 數值欄位=None, 分類欄位=None, 標記欄位=None, 
            圖例名稱=None, 變色範圍='四分位數', 顯示圖例=False, 緩衝區半徑公尺長=None):
    """
    使用 explore 顯示交互式地圖。
    - 支援「緩衝區半徑公尺長」參數：可畫出以幾何為中心（如點）的半透明緩衝區，緩衝區顏色深淺由「數值欄位」決定 (透明度上限為 50%)。
    - 標記偏移：若多個標記位置相同，透過微幅隨機偏移避免重疊。
    """
    import numpy as np
    import webbrowser
    import os
    import tempfile
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import folium
    import random

    if gdf is None or gdf.empty:
        print("資料為空")
        return None

    # 1. 處理數值映射邏輯 (用於透明度與深淺計算)
    vmin, vmax = None, None
    if 數值欄位 and 數值欄位 in gdf.columns:
        if 變色範圍 == '四分位數':
            vmin, vmax = gdf[數值欄位].quantile(0.25), gdf[數值欄位].quantile(0.75)
        elif 變色範圍 == '眾數':
            mode_series = gdf[數值欄位].mode()
            眾數 = mode_series.iloc[0] if not mode_series.empty else gdf[數值欄位].median()
            std = gdf[數值欄位].std()
            vmin, vmax = max(gdf[數值欄位].min(), 眾數 - 0.5 * std), min(gdf[數值欄位].max(), 眾數 + 0.5 * std)
        else:
            vmin, vmax = gdf[數值欄位].min(), gdf[數值欄位].max()
        if vmin is not None and vmax is not None and vmin >= vmax:
            vmin, vmax = gdf[數值欄位].min(), gdf[數值欄位].max()
            if vmin == vmax: vmax += 1

    # 2. 處理緩衝區圖層 (若有指定緩衝區半徑，自動轉為公尺投影坐標系計算再轉回 EPSG:4326)
    plot_gdf = gdf
    if 緩衝區半徑公尺長 is not None and 緩衝區半徑公尺長 > 0:
        buffered_gdf = gdf.to_crs(epsg=3826).copy()
        buffered_gdf['geometry'] = buffered_gdf.geometry.buffer(緩衝區半徑公尺長)
        plot_gdf = buffered_gdf.to_crs(epsg=4326)

    # 3. 核心繪圖邏輯與樣式設定 (透明度深淺控制上限為 50% / 0.5)
    color_col = 分類欄位 if 分類欄位 else 數值欄位
    style_kwds = {'weight': 2, 'opacity': 0.8} 
    
    if 分類欄位 and 分類欄位 in gdf.columns:
        categories = gdf[分類欄位].unique()
        cmap_obj = plt.get_cmap('Set1') 
        num_cats = len(categories)
        color_list = [mcolors.to_hex(cmap_obj(i / max(1, num_cats - 1))) for i in range(num_cats)]
        color_map = dict(zip(categories, color_list))
        
        def style_fn(feature):
            cat = feature['properties'].get(分類欄位, None)
            base_color = color_map.get(cat, "#3388ff")
            style_dict = {"color": base_color, "weight": 2, "opacity": 0.8, "fillColor": base_color}
            if 數值欄位 and 數值欄位 in gdf.columns:
                val = feature['properties'].get(數值欄位, 0)
                if val is not None and not np.isnan(val):
                    norm_val = (val - vmin) / (vmax - vmin) if (vmax - vmin) != 0 else 0.5
                    # 透明度 (fillOpacity) 控制在 0.1 到 0.5 (最大 50%) 之間
                    alpha = float(np.clip(norm_val * 0.4 + 0.1, 0.1, 0.5))
                    style_dict["fillOpacity"] = alpha
                else:
                    style_dict["fillOpacity"] = 0.3
            else:
                style_dict["fillOpacity"] = 0.3
            return style_dict
        style_kwds["style_function"] = style_fn
    elif 數值欄位 and 數值欄位 in gdf.columns:
        def style_fn(feature):
            val = feature['properties'].get(數值欄位, 0)
            style_dict = {"weight": 2, "opacity": 0.8}
            if val is not None and not np.isnan(val):
                norm_val = (val - vmin) / (vmax - vmin) if (vmax - vmin) != 0 else 0.5
                # 透明度 (fillOpacity) 控制在 0.1 到 0.5 (最大 50%) 之間
                alpha = float(np.clip(norm_val * 0.4 + 0.1, 0.1, 0.5))
                style_dict["fillOpacity"] = alpha
            else:
                style_dict["fillOpacity"] = 0.3
            return style_dict
        style_kwds["style_function"] = style_fn

    #4. 呼叫 explore
    m = plot_gdf.explore(
        column=color_col,
        cmap="turbo" if 數值欄位 and not 分類欄位 else None,
        vmin=vmin, vmax=vmax,
        # tiles="OpenStreetMap", 
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community",
        legend=顯示圖例,
        tooltip=True, popup=True,
        style_kwds=style_kwds
    )

    # 使用 Esri 的免費淡色底圖 (Esri World Gray Canvas)
    # m = plot_gdf.explore(
    #     column=color_col,
    #     cmap="turbo" if 數值欄位 and not 分類欄位 else None,
    #     vmin=vmin, vmax=vmax,
    #     tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
    #     attr="Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ",
    #     legend=顯示圖例,
    #     tooltip=True, popup=True,
    #     style_kwds=style_kwds
    # )

    # 5. 增加「具偏移功能」的文字標記層 (使用原圖 gdf 的質心)
    if 標記欄位 and 標記欄位 in gdf.columns:
        temp_gdf = gdf.to_crs(epsg=4326)
        jitter = 0.00005 

        for _, row in temp_gdf.iterrows():
            text = str(row[標記欄位])
            if text and text.lower() not in ['none', 'nan', '無']:
                centroid = row.geometry.centroid
                lat_offset = (random.random() - 0.5) * jitter
                lon_offset = (random.random() - 0.5) * jitter
                
                folium.Marker(
                    location=[centroid.y + lat_offset, centroid.x + lon_offset],
                    icon=folium.DivIcon(
                        html=f"""<div style="font-family: 'Microsoft JhengHei', sans-serif; 
                                color: #000; font-weight: 900; font-size: 9pt; 
                                white-space: nowrap; text-shadow: 2px 2px 2px #FFF, -1px -1px 0 #FFF, 1px -1px 0 #FFF, -1px 1px 0 #FFF, 1px 1px 0 #FFF;">
                                {text}</div>"""
                    )
                ).add_to(m)

    # 6. 儲存與開啟 (修改地圖.py 的這一段)
    fd, path = tempfile.mkstemp(suffix='.html')
    try:
        m.save(path)
        
        # 【新增這幾行】：讀取 HTML 並寫入 referrer 政策
        with open(path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 在 <head> 中插入政策，允許本地檔案傳送 Referer
        meta_tag = '<meta name="referrer" content="no-referrer-when-downgrade">'
        html_content = html_content.replace('<head>', f'<head>{meta_tag}')
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        webbrowser.open(f'file://{os.path.realpath(path)}')
    finally:
        os.close(fd)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-x", type=float, help="經度")
    parser.add_argument("-y", type=float, help="緯度")
    args = parser.parse_args()
    if args.x and args.y:
        顯示座標(args.y, args.x)
