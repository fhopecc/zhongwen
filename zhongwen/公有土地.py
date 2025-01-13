from diskcache import Cache
from pathlib import Path

cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

@cache.memoize('讀取審計部公有土地清冊')
def 讀取審計部公有土地清冊(公有土地清冊檔, 地籍圖檔=None ):
    '座標系為EPSG3826'
    from zhongwen.地籍圖 import 讀取地籍圖
    import pandas as pd

    publand_file = Path(公有土地清冊檔)
    df = pd.read_csv(publand_file)
    df['12碼地段號'] = df['12碼地段號'].map(lambda n: f"{int(n):012d}")
    if 地籍圖檔:
        gdf = 讀取地籍圖(地籍圖檔)
        for c in df.columns:
            if c in gdf.columns:
                if c != 'ID':
                    del gdf[c]
        df = gdf.merge(df, on='ID')
    return df

def 取占用公有地之宗教建築(公有土地檔, 地籍圖檔):
    from zhongwen.公有土地 import 讀取審計部公有土地清冊, cache
    from zhongwen.快取 import 刪除指定名稱快取
    from zhongwen.地籍圖 import 讀取地籍圖
    from zhongwen.開放街圖 import 下載宜蘭縣寺廟圖徵
    import geopandas as gpd
    import pandas as pd
    # 刪除指定名稱快取(cache, '讀取審計部公有土地清冊')

    gdf = 讀取審計部公有土地清冊(公有土地檔, 地籍圖檔)
    gdf1 = 下載宜蘭縣寺廟圖徵()
    gdf1 = gdf1.to_crs(epsg=3826)
    gdfs = [] 
    for gtype in ["Point", "LineString",  "Polygon"]:
        if not (gdf1_ := gdf1[gdf1.geometry.type == gtype]).empty:
            gdf_ = gpd.overlay(gdf, gdf1_, how='intersection')
            gdfs.append(gdf_)
    gdf = gpd.GeoDataFrame(pd.concat(gdfs)).rename(columns={'name':'宗教建築名稱'})
    gdf = gdf.dropna(subset='宗教建築名稱')
    gdf['占用面積'] = gdf.geometry.area
    columns = ['宗教建築名稱', '鄉鎮市區', '段名', '地號', '公私別', '所有權人', '管理者'
              ,'標示面積', '向量面積', '占用面積'
              ,'使用分區' ,'使用地類別', '國土利用_套疊', '都市計畫_套疊'
              ,'登記日期(年月日)', '登記原因', 'geometry']
    gdf = gdf.query('占用面積>100')
    gdf = gdf[columns]
    gdf.reset_index(drop=True, inplace=True)
    gdf.columns.name = '序號'
    gdf.index = gdf.index+1
    return gdf
