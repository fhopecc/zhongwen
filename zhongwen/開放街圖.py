from pathlib import Path
from diskcache import Cache
cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

def 取地點座標(地點):
    '地點格式如次：宜蘭縣審計室, 宜蘭縣, 台灣，座標系是4326。'
    import osmnx as ox
    return ox.geocode(地點)

def 取地點最近車程網節點(地點):
    '地點格式如次：宜蘭縣審計室, 宜蘭縣, 台灣。'
    import osmnx as ox
    import networkx as nx

    loc = 取地點座標(地點)

    # 下載該地區的路網（例如駕車路網）
    G = ox.graph_from_point(loc, dist=1000, network_type="drive")

    # 找到最近的節點
    return ox.distance.nearest_nodes(G, loc[1], loc[0])

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

@cache.memoize(tag='路網')
def 取路網(區域名稱="Hualien County, Taiwan", 類型='drive'):
    """
    :param 類型: 路網類型，例如 'drive'（開車）、'walk'（步行）、'bike'（自行車）等
    :return: OSMnx 圖形物件
    """
    import osmnx as ox
    ox.utils.config(log_console=True, use_cache=True)
    place_name = 區域名稱
    network_type = 類型
    G = ox.graph_from_place(place_name, network_type=network_type)
    return G

def 取節點最短路程(起點, 終點, 路網=None):
    '回傳公尺距離及節點路徑'
    import networkx as nx
    import pandas as pd
    G = 路網
    if not G:
        G = 取路網()
    origin_node = 起點
    destination_node = 終點
    
    try:
        shortest_route = nx.shortest_path(G, origin_node, destination_node, weight='length')
        route_length = nx.shortest_path_length(G, origin_node, destination_node, weight='length')
        if pd.isnull(route_length):
            msg = f"沒有找到從節點 {origin_node} 到節點 {destination_node} 的路徑。"
            raise nx.NetworkXNoPath(msg)
        return route_length, shortest_route
    except nx.NetworkXNoPath:
        msg = f"沒有找到從節點 {origin_node} 到節點 {destination_node} 的路徑。"
        raise nx.NetworkXNoPath(msg)

class 轉換多邊形錯誤(Exception): pass
def 取開放街圖網路圖徵(識別碼):
    from shapely.geometry import Polygon
    import overpy

    api = overpy.Overpass()
    specific_way_id = 識別碼
    query = f"""
    [out:json][timeout:25];
    way({specific_way_id});
    out body;
    >;
    out skel qt;
    """
    result = api.query(query)
    if result.ways:
        way = result.ways[0]
        
        # 創建節點坐標字典
        nodes = {node.id: (float(node.lon), float(node.lat)) for node in result.nodes}
        
        # 獲取多邊形的座標
        coords = [nodes[node.id] for node in way.nodes]
        
        # 確保該 way 是閉合的
        if coords[0] == coords[-1]:
            polygon = Polygon(coords)  # 創建 Shapely Polygon
            return polygon
        else:
            raise 轉換多邊形錯誤("非閉合網路無法轉換成多邊形。")

@cache.memoize('取路口')
def 取路口(地區="花蓮縣, 臺灣"):
    '''
    一、取開放街圖路口，即連接逾 3 條道路之交叉點。
    二、欄位：osmid、x、y, street_count, name
    三、座標系 WGS84, EPSG:4326
    四、street_count：1.死巷；2.道路屬性、速限或路名變化，非真正路口；
                      3.三叉路口，典型的 T 字或 Y 字路口；4.四條道路交會通常為十字路口；
                      5或以上.多叉路口或圓環。
    '''
    from zhongwen.文 import 臚列
    import geopandas as gpd
    import osmnx as ox

    # 從 OpenStreetMap 下載花蓮市的道路網絡數據
    G = ox.graph_from_place(地區, network_type='drive')

    # 提取路口 (交叉點) 的資料
    nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)

    # 篩選出具有多個連接道路的路口 (即交叉點)
    intersections = nodes[nodes['street_count'] > 2]

    def get_intersection_name(node, G):
        "根據路口連接的道路名稱推測路口名稱"
        street_names = []
        for u, v, key, data in G.edges(node, keys=True, data=True):
            if 'name' in data:
                street_names.append(data['name'])

        def flatten_generator(nested_list):
            for item in nested_list:
                if isinstance(item, list):
                    yield from flatten_generator(item)
                else:
                    yield item
        return 臚列(sorted(list(flatten_generator(street_names))))

    # 對每個路口推測名稱
    intersections['name'] = intersections.index.map(lambda node: get_intersection_name(node, G))
    return intersections

def 繪路程(起點, 終點, 地圖, 路網=None, 色彩='blue'):
    import folium
    import osmnx as ox
    s, e, m, G = 起點, 終點, 地圖, 路網
    folium.Marker((s.y, s.x)
                 ,icon=folium.DivIcon(
                     html=f'<div style="font-size: 10pt; color: white; background:black">{s.名稱}</div>')
                 ).add_to(m)
    folium.Marker((e.y, e.x)
                 ,icon=folium.DivIcon(
                     html=f'<div style="font-size: 10pt; color: white; background:black">{e.名稱}</div>')
                 ).add_to(m)
    if not G:
        G = 取路網()
    snode = ox.distance.nearest_nodes(G, s.geometry.x, s.geometry.y)
    enode = ox.distance.nearest_nodes(G, e.geometry.x, e.geometry.y)
    d, route = 取節點最短路程(snode, enode, G)
    km = d / 1000  # 將距離轉換為公里

    # 路徑中心節點
    route_center_index = len(route) // 2
    route_center = route[route_center_index]

    # 繪製路徑節點
    route_points = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]
    folium.PolyLine(route_points, color=色彩, weight=5, opacity=0.7).add_to(m)

    folium.Marker(
        location=(G.nodes[route_center]['y'], G.nodes[route_center]['x']),
        icon=folium.DivIcon(html=f'<div style="text-align:center;width:48pt; font-size: 8pt; color: white; background:black">{km:.2f}公里</div>')
    ).add_to(m)

@cache.memoize(tag='下載宜蘭縣寺廟圖徵')
def 下載宜蘭縣寺廟圖徵():
    '座標系為EPSG4326'
    import osmnx as ox
    place_name = "Yilan County, Taiwan"
    tags = {'amenity': 'place_of_worship', "religion": "buddhist"}
    temples = ox.geometries_from_place(place_name, tags)
    return temples

@cache.memoize('下載道路網')
def 下載道路網(縣市="Yilan County, Taiwan"):
    '座標系EPSG 4826'
    import osmnx as ox
    import geopandas as gpd
    place_name = 縣市
    G = ox.graph_from_place(place_name, network_type='drive')
    nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)
    return edges

def 查詢最近路程節點(地點, 路網=None):
    '地點如次：宜蘭縣審計室, 宜蘭縣, 台灣'
    import osmnx as ox
    
    # 使用 geocode 查詢地理位置
    location = ox.geocode(地點)
    print("位置座標：", location)
