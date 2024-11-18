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

