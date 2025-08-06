from diskcache import Cache
from pathlib import Path
import functools
cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

@cache.memoize('國土利用調查成果圖')
def 國土利用調查成果圖(shps):
    from collections.abc import Iterable 
    import geopandas as gpd
    import pandas as pd
    
    if isinstance(shps, str) or not isinstance(shps, Iterable):
        shps = [shps]
    df = pd.concat(gpd.read_file(shp, encoding='cp950').to_crs(epsg=3826) for shp in shps) 
    df = df.rename(columns=國土利用屬性欄位表())
    return df

def 國土利用屬性欄位表():
    from pathlib import Path
    import pandas as pd
    定義表目錄 = Path(__file__).parent / '定義表' 
    f = 定義表目錄 / "國土利用屬性欄位表.xlsx"
    df = pd.read_excel(f, header=1)
    return df[['欄位名稱', '中文名稱']].set_index('欄位名稱').中文名稱.to_dict()

def fbuse():
    '''國土利用調查為工商使用，篩選2級代碼如次：
1. 0501(商業)
2. 0504(製造業)
'''
    u = use()
    return u.query('LCODE_C2.str.contains("0501|0504")')


def factory_use():
    '''國土利用調查為工廠（0504）、倉儲（0505）、礦鹽利用土地08（砂石廠）、
營建剩餘土石收容處理相關設施（0904）等，例如：
LAND.factory_use()
'''
    u = use()
    return u[(u.LCODE_C1.str.contains('08'))
             |u.LCODE_C2.str.contains('0504|0505|0904')
            ]


@functools.cache
def 國土利用類別(等級=2):
    from pathlib import Path
    import pandas as pd
    定義表目錄 = Path(__file__).parent / '定義表' 
    t = pd.read_excel(定義表目錄 / '土地利用代碼.xlsx', sheet_name=f"{等級}級")
    if 等級==1:
        t['代碼'] = t.代碼.map(lambda i: f'{i:02}')
    elif 等級==2:
        t['代碼'] = t.代碼.map(lambda i: f'{i:04}')
    elif 等級==3:
        t['代碼'] = t.代碼.map(lambda i: f'{i:06}')
    t = t.set_index('代碼').類別.to_dict() 
    return t

def 國土利用類別備份(c):
    '''依代碼查詢國土利用分類，例如：
LAND.get_usekind('0504')'''
    try:
        n =  {'03':'交通利用土地'
             ,'0301':'機場'
             ,'0302':'一般鐵路及相關設施'
             ,'0305':'道路及相關設施'
             ,'0306':'港口'
             ,'04':'水利利用土地'
             ,'0401':'河道'
             ,'0402':'蓄水設施'
             ,'0403':'水道沙洲灘地'
             ,'0404':'水道構造物'
             ,'0405':'防汛道路'
             ,'0406':'海面'
             ,'05':'建築利用土地'
             ,'0501':'商業'
             ,'050101':'零售批發'
             ,'050102':'服務業'
             ,'0502':'純住宅'
             ,'0503':'混合使用住宅'
             ,'0504':'製造業'
             ,'0505':'倉儲' 
             ,'0506':'宗教'
             ,'0507':'殯葬設施'
             ,'0508':'其他建築用地' 
             ,'06':'公共利用土地' 
             ,'0601':'政府機關' 
             ,'0602':'學校' 
             ,'0603':'醫療保健' 
             ,'0604':'社會福利設施' 
             ,'0605':'公用設備' 
             ,'0606':'環保設施' 
             ,'060502':'電力' 
             ,'060503':'瓦斯' 
             ,'060505':'加油站' 
             ,'0606':'環保設施' 
             ,'07':'遊憩利用土地'
             ,'0701':'文化設施'
             ,'070102':'一般文化設施'
             ,'070301':'遊樂場所'
             ,'0702':'公園綠地廣場'
             ,'0703':'休閒設施'
             ,'08':'礦鹽利用土地'
             ,'0801':'礦業及相關設施'           
             ,'0802':'土石及相關設施'
             ,'0803':'鹽業及相關設施'
             ,'09':'其他利用土地'
             ,'0901':'溼地'
             ,'0902':'草生地'
             ,'0903':'裸露地'
             ,'0904':'營建剩餘土石收容處理相關設施' 
             ,'0905':'空置地'
             }[c]
        return n
    except:
        return c
