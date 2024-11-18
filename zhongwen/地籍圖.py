'''土地資料之取得、匯入及清理
地號例：花蓮縣鳳林鎮水車段1460
地碼例：UB07024714600000
'''
from functools import cache
from pathlib import Path
from diskcache import Cache
import fhopecc.env as env

dcache = Cache(Path.home() / 'cache' / Path(__file__).stem)

r = env.datadir / '土地基本資料'
d = env.workdrive / 'gd' / '110縣府單決' / '沿海保護' / '都計容許使用'

def sname(no):
    '指定 no 地號碼表示的地號簡名，無鄉鎮市區名。'
    return name(no)[3:]

def number(s):
    '轉成半型數字'
    return (s
            .translate(str.maketrans('０１２３４５６７８９之','0123456789-'))
            .translate(str.maketrans('零一二三四五六七八九', '0123456789'))
           )

def 地段號地籍圖(地段號清單):
    段號清單 = [地籍圖段號(地段號) for 地段號 in 地段號清單]
    return 地籍圖().query('段號.isin(@段號清單)')
    
def landkml(kml, 地號清單):
    '産出指定地號清單之 kml 檔'
    ls = 段號地籍圖(地號清單)
    tokml(ls, kml, 'landid')

def landtokml(kml, *landids):
    '産出指定地段ID之 kml 檔'
    landids = map(to_landid, landids)
    s = shape()
    ls = s.query('landid.isin(@landids)')
    tokml(ls, kml, 'landid')

def unit_code(county):
    '地所代碼'
    if county in ['花蓮', '新城', '吉安', '壽豐', '秀林']:
        return 'A'
    elif county in ['光復', '萬榮', '豐濱', '鳳林']:
        return 'B'
    else:
        return 'C'

def shape():
    return 地籍圖()

@cache
def 地籍圖屬性表():
    import pandas as pd
    df = pd.read_csv(env.定義表目錄 / '地籍圖屬性資料說明表.txt')
    df = df.set_index('欄位名稱')
    return df.資料說明.to_dict()

@dcache.memoize('讀取地籍圖')
def 讀取地籍圖(地籍圖檔路徑):
    '座標系為EPSG3826'
    from zhongwen.file import 最新檔
    import geopandas as gpd
    shp = 地籍圖檔路徑
    gdf = gpd.read_file(shp, encoding='utf8').to_crs(epsg=3826)
    gdf = gdf.rename(columns=地籍圖屬性表())
    return gdf

def 使用分區使用地類別代碼對照():
    return pd.read_csv(r / '使用分區使用地類別代碼檔(結構化).csv').set_index('Code').iloc[:, 0]

def get_usetype(landid):
    '''依地號查詢土地使用分區，例如：
land.get_usetype('壽豐鄉山嶺段458地號')
'''
    lid = to_landid(landid)
    s = shape()
    s = s.query('landid == @lid')[['landid', 'AA11', 'AA12']]
    s['使用分區'] = s.AA11.map(usetype())
    s['使用地類別'] = s.AA12.map(usetype())
    return s


def download_land_usetype_dict():
    '''下載土地使用分區對照檔。
TODO:如 make 的 file 指令之裝飾子，提供使用前要下載檔案'''
    url = 'http://117.56.7.113/od/data/api/3C0DF3A1-42F4-44A3-B5E3-5E3444F4CB8E?$format=json'
    f = r / 'land_usetype_dict.json'
    from urllib import request
    with request.urlopen(url) as c:
        with f.open('w') as f:
            f.write(c.read())

def owner(unit, time):
    '''傳回指定地政單位及資料調閱日期之土地所有權部資料，例如：
LAND.owner('花蓮地政', '1091215')
'''
    try:
        with next((r / f'{time}{unit}').glob(f'*所有權部*txt')).open('r', encoding='big5', errors='replace') as f:
            o = pd.read_fwf(f,widths=[4,4,4,4,3,2,2,2,3,2,2,10,1,10,10,3,1,6,8,60,60]
                              ,header=None
                              ,names=["段號","地號母號","地號子號","登記次序","登記日期（年）","登記日期（月）","登記日期（日）","登記原因","登記原因發生日期（年）","登記原因發生日期（月）","登記原因發生日期（日）","所有權人統一編號","權利範圍類別","權利範圍應有部分分母","權利範圍應有部分分子","權狀年期","權狀字","權狀號","申報地價","所有權人姓名","所有權人住址"]                              
                           )[:-1]        
            o['landid'] = o.apply(lambda r: f"U{unit_code(unit[:2])}{r['段號']}{r['地號母號']}{r['地號子號']}", axis=1)
            return o                              
    except StopIteration:
        return None
    
def 管理者(unit, time):
    '''傳回指定地政單位及資料調閱日期之管理者資料，例如：
land.管理者('花蓮地政', '1091215')
'''
    return {"玉里地政":manager_fwf
           ,"花蓮地政":manager_csv
           ,"鳳林地政":tagfwf 
           }[unit](unit, time)

#管理者(土地)
def manager_csv(unit, time):
    return pd.read_csv(next((r / f'{time}{unit}').glob(f'*管理者(土地)utf8*'))
                      ,header=None
                      ,dtype=str
                      )[:-2]
#管理者(土地)
def manager_fwf(unit, time):
    return pd.read_fwf(next((r / f'{time}{unit}').glob(f'*管理者*utf8*'))
                      ,widths=[1,4,4,4,4,10,10,60,60]
                      ,header=None
                      ,names=["部別","段（小段）號","地號母號"
                             ,"地號子號","登記次序"
                             ,"所有權人統一編號","管理者統一編號","管理者姓名","管理者住址"]                            
                      ,encoding='utf8'
                      )[:-1]

def 地政單位代碼(unit):
    return {"玉里地政":'C' ,
            "花蓮地政":'A' ,
            "鳳林地政":'B'
           }[unit]


def 標示部(unit, time):
    '''傳回指定地政單位及資料調閱日期之標示部資料，例如：
land.標示部('花蓮地政', '1091215')
'''
    tags = {"玉里地政":tagfwf ,
            "花蓮地政":tagcsv ,
            "鳳林地政":tagfwf     
           }[unit](unit, time)
    def get_no(tag):
        return (f'{tag.縣市[:1]}{地政單位代碼(unit)}{tag.鄉鎮市區[:2]}'
                f'{tag["段（小段）號"][:4]}{tag.地號}'
               )
    tags['no'] = tags.apply(get_no, axis='columns')
    return tags
            
#標示部格式為固定寬度
def tagcsv(unit, time):
    return pd.read_csv(next((r / f'{time}{unit}').glob(f'*標示部*'))
                      ,header=None
                      ,dtype=str
                      ,encoding='cp950'
                      ,names=["縣市","鄉鎮市區","段（小段）號","地號",
                              "登記日期", "登記原因", "地目","等則","面積" ,"使用分區","使用地類別",
                              "公告土地現值","公告地價","視中心縱坐標",
                              "視中心橫坐標","圖幅號"]                              
                      )[:-1]
def tagfwf(unit, time):
    '標示部格式為固定寬度'
    try:
        o = pd.read_fwf(next((r / f'{time}{unit}').glob(f'*標示部*utf8*')),widths=[1,2,4,4,4,3,2,2,2,1,2,9,2,2,7,7,10,10,3]
                  ,header=None
                  ,names=["縣市","鄉鎮市區","段（小段）號","地號母號","地號子號"
                         ,"登記日期（年）","登記日期（月）","登記日期（日）","登記原因","地目","等則","面積"
                         ,"使用分區","使用地類別","公告土地現值","公告地價","視中心縱坐標"
                         ,"視中心橫坐標","圖幅號"]                              
                  ,encoding='utf8'
                   )[:-1]
        return o                              
    except StopIteration:
        return None

def reason():
    '''傳回登記原因代碼表'''
    return pd.read_csv(r  / '登記原因代碼1090604.csv')

def reason_contains(str):
    '''查詢登記原因代碼。例：LAND.reason_contain('徵收')，列出所有含「徵收」之登記原因代碼。'''
    rr = reason()
    return rr[rr.ReasonsForRegistratioin.str.contains(str)]
def get_reason(str):
    '''查詢指定代碼之登記原因。例：列出所有含「ZZ」之登記原因程式碼如下：
LAND.get_reason('ZZ')'''
    rr = reason()
    return rr[rr.Code.str.contains(str)]
def print_land_data_size(unit, time):
    '''印出調閱地所資料筆數，供填轉錄（銷毀）各機關電腦資料檔案通報單使用。
例：LAND.print_land_data_size("鳳林地政", "1091221")'''
    o = owner(unit, time)
    t = tag(unit, time)
    m = manager(unit, time)
    print(f'''標示部計{t.index.size:,}筆
所有權部計{o.index.size:,}筆
管理者資料計{m.index.size:,}筆
''')


def to_gdf(df, 地址欄位=None):
    if 地址欄位:
        return gpd.GeoDataFrame(df, crs="EPSG:4326", 
                                geometry=df[地址欄位].map(地址座標)
                               )   
    return df
