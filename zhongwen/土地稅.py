from zhongwen.庫 import 通知執行時間
from pathlib import Path
from diskcache import Cache

cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

@通知執行時間
@cache.memoize('稅地種類檔')
def 稅地種類檔(LNDT203):
    '地價稅係以所有權人於該縣所有土地歸戶成一個稅號，房屋稅係以門牌號'
    import pandas as pd
    from pathlib import Path
    df = pd.read_excel(LNDT203)
    定義表目錄 = Path(__file__).parent / '定義表' 
    col_desc = pd.read_excel(定義表目錄 / '稅地種類檔(LNDT203).xls').set_index('COLUMN_NAME')
    col_desc = col_desc.COMMENTS.to_dict()
    df = df.rename(columns=col_desc)
    return df

def 所有權人檔(wdir):
    '地價稅係以所有權人於該縣所有土地歸戶成一個稅號，房屋稅係以門牌號'
    '下次要檔要公私有別及身分代號'
    import pandas as pd
    from pathlib import Path
    df = pd.read_csv(wdir / '所有權人檔(LNDT202).txt', sep='\t', 
                     dtype={'LND_MARK':object})
    定義表目錄 = Path(__file__).parent / '定義表' 
    col_desc = pd.read_excel(定義表目錄 / '所有權人檔(LNDT202).xls').set_index('COLUMN_NAME')
    col_desc = col_desc.COMMENTS.to_dict()
    df = df.rename(columns=col_desc)
    return df

@通知執行時間
@cache.memoize('田賦地')
def 田賦地(LNDT203, 審計部公有土地清冊檔=None, 地籍圖檔=None
          ,都市計畫圖檔目錄=None):
    '''核課田賦之土地，如有給定地籍圖，則篩選課徵或免徵田賦面積達八成者，再給定都計圖，則進一步篩選未於都市計畫農保區及公設保留地範圍內之土地。'''
    from zhongwen.公有土地 import 讀取審計部公有土地清冊
    from zhongwen.地籍圖 import 讀取地籍圖
    from zhongwen.都市計畫圖 import 載入都市計畫圖
    import geopandas as gpd
    LNDT203 = str(LNDT203)
    df = 稅地種類檔(LNDT203).query('稅地種類.str.contains("6|7|8|9", na=False)')
    df = df.groupby('土地標示').agg({'稅籍編號':lambda vs: '、'.join(map(str, vs)), '課稅面積':sum}).reset_index()
    df["12碼地段號"] = df.土地標示.astype(str).str[-12:]

    if 審計部公有土地清冊檔:
        publand_df = 讀取審計部公有土地清冊(str(審計部公有土地清冊檔)) 
        df = df.merge(publand_df, on="12碼地段號", how='left')

    if 地籍圖檔:
        gdf1 = 讀取地籍圖(地籍圖檔)
        def 取土地標示(row): 
            return int(f'{row.鄉鎮市區}{row.地段代碼}{row.地號}')
        gdf1['土地標示'] = gdf1.apply(取土地標示, axis=1)
        del df['ID'] 
        del df['地號'] 
        del df['使用分區'] 
        del df['公告現值'] 
        del df['公告地價'] 
        del df['縣市'] 
        del df['鄉鎮市區'] 
        df = gdf1.merge(df, on='土地標示') 
        df['徵免田賦面積比率'] = df.課稅面積 / df.面積
        df = df.query('徵免田賦面積比率>0.8')
        if 都市計畫圖檔目錄: # 前提須指定地籍圖檔
            gdf1 = 載入都市計畫圖(str(都市計畫圖檔目錄))
            df = gpd.overlay(df, gdf1, how='intersection')
            df = df.query('not 分區類別.str.contains("農業區|保護區|河川區|綠地|用地|步道")')
    return df

@通知執行時間
@cache.memoize('田賦地籍圖')
def 田賦地籍圖(LNDT203, 地籍圖檔):
    '徵免田賦面積達八成者'
    from zhongwen.地籍圖 import 讀取地籍圖
    shp = 地籍圖檔
    gdf1 = 讀取地籍圖(shp)

    # 公有地 = 公有土地()
    # df = df.query('段號 not in @公有地.ID')

    def 稅籍地號(row): 
        return int(f'{row.鄉鎮市區}{row.地段代碼}{row.地號}')

    gdf1['稅籍地號'] = gdf1.apply(稅籍地號, axis=1)
    
    gdf = gdf1.merge(田賦地(LNDT203), left_on='稅籍地號', right_on= '土地標示') 
    gdf = gdf.rename(columns=lambda cn: cn.replace('_x', ''))
    gdf['徵免田賦面積比率'] = gdf.課稅面積 / gdf.面積
    gdf = gdf.query('徵免田賦面積比率>0.8')
    return gdf

def 非農林利用土地(國土利用調查成果圖檔):
    from zhongwen.國土利用調查成果圖 import 國土利用調查成果圖, 國土利用類別
    u = 國土利用調查成果圖(國土利用調查成果圖檔).query('not 第1級土地利用分類.str.contains("01|02")')
    u['利用類別'] = u['第2級土地利用分類'].map(lambda c: 國土利用類別(2).get(c, c))
    pat = '海面|學|校|道路|鐵路|河川|草生|溝渠|未使用地|崩塌地|省道|公園綠地廣場|湖泊|礁岩'
    pat += '|堰壩|氣象|機場|專用港|地下水取水井|其他港口設施|堤防|法定文化資產|電力|灘地|其他文化設施'
    pat += '|政府機關|社會福利設施|人工改變中土地|水道沙洲灘地|海面|水閘門|抽水站|其他|興建中'
    pat += '|宗教|自來水及自來水設施|幼兒園|醫療保健|一般文化設施|蓄水池|濕地|裸露地|港口|蓄水設施'
    pat += '|公用設備|空置地|國道|水道|水利構造物|文化設施|水庫'
    u = u.query('not 利用類別.str.contains(@pat, na=False)')
    return u 
    
@通知執行時間
@cache.memoize('非農林用徵免田賦土地')
def 非農林用徵免田賦土地(國土利用調查成果圖檔, LNDT203, 地籍圖檔):
    import geopandas as gpd
    u = 非農林利用土地(國土利用調查成果圖檔) 
    df = gpd.overlay(u, 田賦地籍圖(LNDT203, 地籍圖檔),  how='intersection')
    df['異常使用面積'] = df.geometry.area
    df['設算課稅地價'] = df.異常使用面積 * df.公告地價
    df = df.rename(columns={'課稅面積':'徵免田賦面積'})
    return df

def 開啟國土規劃地理資訊平台():
    import os
    url = 'https://nsp.tcd.gov.tw/ngis/'
    os.system(f'start {url}')
