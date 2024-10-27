from pathlib import Path
from diskcache import Cache
cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

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
def 取路網(區域名稱="Yilan County, Taiwan", 類型='drive'):
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

def 取路口(查詢地點=None):
    '取開放街圖路口'
    import osmnx as ox
    import geopandas as gpd

    # 指定花蓮市的位置名稱
    place_name = "Hualien City, Taiwan"

    # 從 OpenStreetMap 下載花蓮市的道路網絡數據
    G = ox.graph_from_place(place_name, network_type='drive')

    # 提取路口 (交叉點) 的資料
    nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)

    # 篩選出具有多個連接道路的路口 (即交叉點)
    intersections = nodes[nodes['street_count'] > 1]

    def get_intersection_name(node, G):
        "根據路口連接的道路名稱推測路口名稱"
        street_names = set()
        for u, v, key, data in G.edges(node, keys=True, data=True):
            if 'name' in data:
                street_names.add(str(data['name']))
        return "".join(sorted(street_names))

    # 對每個路口推測名稱
    intersections['name'] = intersections.index.map(lambda node: get_intersection_name(node, G))
    return intersections

