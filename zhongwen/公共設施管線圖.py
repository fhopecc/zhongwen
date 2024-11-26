from diskcache import Cache
from pathlib import Path
import logging

logger = logging.getLogger(Path(__file__).stem)
cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

@cache.memoize('載入公共設施管線圖')
def 載入公共設施管線圖(公共設施管線圖目錄):
    import geopandas as gpd
    import pandas as pd
    shps = Path(公共設施管線圖目錄).glob('*.shp')
    dfs = []
    for shp in shps:
        try:
            df = gpd.read_file(shp)
            dfs.append(df)
        except ValueError:
            logger.error(f'無法載入圖資檔：{shp}。')
            continue
    gdf = pd.concat(dfs)
    return gdf

@cache.memoize('取無管線資料之手孔蓋')
def 取無管線資料之手孔蓋(公設管線圖目錄, 管線中類="08"):
    '座標系為EPSG3826'
    from zhongwen.公共設施管線圖 import 載入公共設施管線圖 
    from pathlib import Path
    import matplotlib.pyplot as plt
    import geopandas as gpd

    gdf = 載入公共設施管線圖(公設管線圖目錄) 
    gdf['管線中類'] = gdf.CategCode.str[1:3]
    gdf['管線細類'] = gdf.CategCode.str[-2:]
    gdf = gdf.query(f'管線中類.str.contains(@管線中類)') # 僅產製自來水及其他管道
    pipe_gdf = gdf.query('管線細類=="01"') # 管線
    cover_gdf = gdf.query('管線細類=="02"') # 手孔蓋
    pipe_buffer3_gdf = pipe_gdf.buffer(3)
    pipe_gdf_union = pipe_buffer3_gdf.unary_union # 將管線合成一個 geometry 簡化比對程序
    covers_not_intersect_pipes_gdf = cover_gdf[~cover_gdf['geometry'].intersects(pipe_gdf_union)]
    return covers_not_intersect_pipes_gdf 
