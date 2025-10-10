from diskcache import Cache
from pathlib import Path
import functools
cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

@functools.cache
@cache.memoize('載入營業登記檔', expire=60*24*60*60)
def 載入營業登記檔(檔=None):
    '''
    一、政府資料開放平台全國營業(稅籍)登記資料集。
    二、主要欄位：營業地址、統一編號、總機構統一編號、營業人名稱、資本額、
                  設立日期、組織別名稱、使用統一發票、
                  行業代號、名稱、行業代號1、名稱1、
                  行業代號2、名稱2、行業代號3、名稱3。
    三、未指定檔即自下載 https://eip.fia.gov.tw/data/BGMOPEN1.csv。
    四、快取60日到期。
    '''
    from zhongwen.檔 import 下載
    import pandas as pd
    if not 檔: 
        檔 = 下載('https://eip.fia.gov.tw/data/BGMOPEN1.csv')
    bgm = pd.read_csv(檔)
    # bgm = bgm[bgm.營業地址.str.contains("花蓮")]
    bgm['統一編號'] = bgm.統一編號.map(lambda d:f'{d:.0f}')
    bgm['設立日期'] = bgm.設立日期.map(lambda d:f'{d:.0f}')
    # bgm['標準地址'] = bgm.營業地址.map(標準地址)
    # bgm = bgm.explode('標準地址')
    return bgm

@cache.memoize(tag='載入停業資料集', expire=15*24*60*60)
def 載入停業資料集():
    '政府資料開放平台-全國營業(稅籍)登記(停業)資料集'
    url = 'https://eip.fia.gov.tw/data/BGMOPEN1X.csv'
    from zhongwen.file import 下載
    f = 下載(url, 覆寫=True)
    import pandas as pd
    dtypes = {'統一編號':str
             ,'設立日期':str
             ,'停業日期':str
             }
    df = pd.read_csv(f, dtype=dtypes)
    df.dropna(subset=['統一編號', '停業日期'], inplace=True)
    df.sort_values('停業日期', inplace=True)
    return df

@cache.memoize(tag='非營業中', expire=30*24*60*60)
def 載入非營業中資料集(
        檔案=r'g:\我的雲端硬碟\111-2建設處及觀光處抽查\公共安全\資訊檔案研析\不需通報資訊檔案\BGMOPEN1Y.csv'
       ,顯示=True):
    '政府資料開放平台-全國營業(稅籍)登記(停業以外之非營業中)資料集'
    df = pd.read_csv(檔案)  
    df.dropna(subset=['統一編號'], inplace=True)
    return df

def 非法民宿尚未辦理營業登記(hoteldir): 
    from fhopecc.bgm import 營業登記
    bgm = 營業登記()
    df = 非法民宿(hoteldir)
    df = df.merge(bgm, how='left', on='標準地址')
    df = df.query('統一編號.isna()')
    df = df.rename(columns=lambda s: s.replace('_x', ''))
    df = df.reset_index(drop=True)
    df.index.name = '序號'
    df.index = df.index+1
    df = df[['民宿名稱', '電話號碼', '營業地址']] 
    return df

def 逾免稅經營規模之合法民宿惟查無營業登記者(hoteldir):
    '財政部90年12月27日台財稅字第0900071529號函'
    bgm = 營業登記()
    from fhopecc.hotel import 逾免稅經營規模之合法民宿
    df = 逾免稅經營規模之合法民宿(hoteldir)
    df = df.merge(bgm, how='left', on='標準地址')
    df = df.query('統一編號.isna()')
    df = df.rename(columns=lambda s: s.replace('_x', ''))
    df = df.reset_index(drop=True)
    df.index.name = '序號'
    df.index = df.index+1
    df = df[['中文名稱', '地址', '總房間數', '客房總樓地板面積',  '總經營人數']]
    return df

def 營業稅稅籍主檔欄位定義(f):
    df = pd.read_excel(f, header=1).query('COMMENTS.notna()')
    return df[['COLUMN_NAME', 'COMMENTS']].set_index('COLUMN_NAME').to_dict()['COMMENTS']

def 營業稅(f, columns=None):
    df = pd.read_excel(f)
    if isinstance(columns, dict):
        df = df.rename(columns=columns)
    df['標準地址'] = df.營業人地址鄉鎮區名稱 + df.營業人地址街道門牌
    df['標準地址'] = df.標準地址.map(標準地址)
    df = df.explode('標準地址')
    return df

   
def find(addr):
    '傳回指定名稱或地址營業稅'
    return (data()
           .query('營業人名稱.str.contains(@addr)')
           )

#行業名稱包含關鍵字
def name(s):
    return data()[data().營業人名稱.str.contains(s)]
#資料來源名稱
    

def typeHas(s):
   return bgm[bgm.名稱.str.contains(s)
             |bgm.名稱1.str.contains(s)
             |bgm.名稱2.str.contains(s)
             |bgm.名稱3.str.contains(s)]

def merge_on_addr(x, addr_col):
    x = x[~x[addr_col].isna()]
    x[addr_col] = x[addr_col].apply(fix_addr)
    xb = x.assign(k=1).merge(bgm.assign(k=1), on="k").drop("k", 1)
    xb["eda"] = xb.loc[:, [addr_col, "營業地址"]].apply(lambda x: distance(*x), axis=1)
    return xb

def merge_on_name(x, name):
    name = str(name) + '_x'
    x.columns = x.columns.map(lambda x: str(x) + '_x')
    b = bgm
    b.columns = b.columns.map(lambda x: str(x) + '_b')
    x = x[~x[name].isna()]
    xb = x.assign(k=1).merge(b.assign(k=1), on="k").drop("k", 1)
    xb["edn"] = xb.loc[:, [name, "營業人名稱_b"]].apply(lambda x: edistance(*x), axis=1)
    return xb

if __name__ == '__main__':
    # cache.evict('載入停業資料集')
    載入停業資料集(顯示=True)
