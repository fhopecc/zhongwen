'旅館管理'
from fhopecc.cache import 資料庫快取
from diskcache import Cache
from pathlib import Path

disk = Path('d:\\')
cache = Cache(disk / 'cache' / Path(__file__).name)

@資料庫快取
def 載入民宿清冊(檔案=Path(__file__).parent / r'test\民宿基本資料1111230.xlsx'
                ,顯示=False):
    '縣府提供列管民宿清冊'
    from zhongwen.pandas_tools import show_html
    df = pd.read_excel(檔案)
    if 顯示: show_html(df, 自動格式=False) 
    return df

@cache.memoize(expire=30*24*60*60, tag='旅宿業清冊')
def 旅宿業清冊():
    '''政府資料開放平台下載旅館民宿資料集，欄位定義參考交通部發布之觀光資訊標準格式旅館民宿。'''
    import pandas as pd
    csv = 'https://gis.taiwan.net.tw/XMLReleaseALL_public/hotel_C_f.csv'
    df = pd.read_csv(csv)
    return df

@cache.memoize(expire=30*24*60*60, tag='花蓮旅宿業清冊')
def 花蓮旅宿業清冊():
    '''
    旅宿業類別代碼：1.國際觀光旅館、2.一般觀光旅館、3.一般旅館、4.民宿
    '''
    df = 旅宿業清冊().query('Region.str.contains("花蓮", na=False)')
    df = df.rename(
            columns={'Name':'名稱'
                    ,'Add':'地址'
                    ,'Class':'類別'
        })
    df['類別'] = df.類別.map({1:'國際觀光旅館'
                             ,2:'一般觀光旅館'
                             ,3:'一般旅館'
                             ,4:'民宿'})
    return df

@cache.memoize()
def 合法民宿(datadir):
    '縣府提供合法民宿基本資料，含客房面積、員工人數、客房數'
    f = 最新檔(datadir, '**/*民宿基本資料*.xlsx')
    df = pd.read_excel(f)
    df = df.rename(columns={'客房總樓地板面積(m²)':'客房總樓地板面積'
        ,'合計總房間數':'總房間數'})
    df = df.query('not 地址.isna()')
    df['標準地址'] = df.地址.map(標準地址)
    df = df.explode('標準地址')
    return df 

def 民宿(datadir):
    '縣府提供清冊'
    f = 最新檔(datadir, '**/*民宿清冊*.xlsx')
    df = pd.read_excel(f, header=3)
    df = df.query('not 營業地址.isna() or 營業地址=="營業地址"')
    df['標準地址'] = df.營業地址.map(標準地址)
    df = df.explode('標準地址')
    return df

@cache.memoize()
def 非法民宿(datadir):
    '縣府提供列管非法民宿'
    return 民宿(datadir).query('現狀.str.contains("非法")')

def 逾免稅經營規模之合法民宿(hoteldir):
    '財政部90年12月27日台財稅字第0900071529號函'
    df = 合法民宿(hoteldir, recache=True)
    df = df.query('客房總樓地板面積>150 or 總房間數>5 or 總經營人數>2')
    return df
