'''地號處理模組'''
from pathlib import Path
from diskcache import Cache
import fhopecc.env as env
import pandas as pd
import re
cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

def 取土地標示(地碼):
    '地價稅檔之土地標示'
    return 地碼[2:]

def 取地號多(s):
    pat = r'([^\d]{2,2}(市|鎮|鄉))?([^\d、與]+段)((\d+(-\d+)?[、及]?)+)'
    ms = re.findall(pat, s)
    r = []
    區 = ''
    for m in ms:
        if(m[0]):
            區 = m[0]
        段 = m[2]
        ns = re.split('[、及]', m[3])
        try:
            ns.remove('')
        except:
            pass
        #print(ns)
        r.extend([f'{區}{段}{n}' for n in ns])
    if r:
        return r
    raise ValueError(f'地號清單{s}格式錯誤')

def 地籍圖段號(地碼):
    '''地籍圖段號無鄉鎮市碼，轉換如次
UB07024714600000 -> UB024714600000 '''
    return 地碼[:2] + 地碼[4:]

def 取地號(地碼, 縣市代碼='G'):
    '''指定地碼表示的地號
16位地碼：縣碼1位所區碼1位鄉鎮市碼2位地段碼4位地號4位地小號4位。
land.name('UB07024714600000') -> '鳳林鎮水車段1460地號'
地號格式無鄉鎮市碼14位：縣碼1位所區碼1位地段碼4位地號4位地小號4位。
地號格式無縣、地所及鄉鎮市碼12位：地段碼4位地號4位地小號4位。
地號格式無縣、地所及鄉鎮市碼11位：地段碼4位地號4位地小號3位。
land.name('UB024714600000') -> '鳳林鎮水車段1460地號'
land.name('024714600000') -> '鳳林鎮水車段1460地號'
land.name('024714600000') -> '鳳林鎮水車段1460地號'
'''
    if len(地碼) == 14:
        縣市代碼=地碼[0]
    n1 = int(地碼[-8:-4])
    n2 = int(地碼[-4:])
    if len(地碼) == 11:
        n2 = int(地碼[-3:])
    n2 = '' if n2==0 else '-'+str(n2)
    if len(地碼) == 11:
        return f"{段名(地碼[:4], 縣市代碼=縣市代碼)}{n1}{n2}地號"
    if len(地碼) == 12:
        return f"{段名(地碼[:4], 縣市代碼=縣市代碼)}{n1}{n2}地號"
    if len(地碼) == 14:
        return f"{段名(地碼[2:6], 縣市代碼=縣市代碼)}{n1}{n2}地號"
    return f"{段名(地碼[4:8], 縣市代碼=縣市代碼)}{n1}{n2}地號"

@cache.memoize(tag='段碼表')
def 段碼表(ldir=None):
    '''段名代碼表
下載網址：[https://lisp.land.moi.gov.tw/MMS/MMSpage.aspx#gobox02]
'''
    if not ldir:
        ldir = r"g:\我的雲端硬碟\0_09月前提創新2案\11210-11數位審計人才\結訓報告\農地太陽光電聚落\1110429地籍圖資"
        ldir = Path(ldir)

    src = ldir / '段名代碼表.csv'
    with src.open('r', encoding='utf-8-sig') as f:
        s = f.read()
        s = re.sub(r'\,(?=(\n|$))', '', s)
        from io import StringIO
        s = StringIO(s)
        data = pd.read_csv(s).query('not 備註.str.contains("註銷", na=False)')
        data['段名'] = data.段 + data.小段
        return data
    raise ValueError(f'檔案{src}不符CSV格式')

def 地碼(s, 縣市代碼='G'):
    return 取地碼(s, 縣市代碼)

def 取地碼(s, 縣市代碼='G', 錯誤傳回原值=True):
    '''指定字串 s 表示的16位地碼：
land.地碼('鳳林鎮水車段1460地號') -> 'UB07024714600000'
land.地碼('鳳林鎮水車段1460') -> 'UB07024714600000'
16位地碼：縣碼1位所區碼1位鄉鎮市碼2位地段碼4位地號4位地小號4位。
'''
    try:
        s = s.replace(' ', '')
        pat = r'([^\d]{2,2}(市|鎮|鄉))?(.+小?段)(\d+(-\d+)?)(地號)?'
        if m := re.match(pat, s): 
            sec = 段碼(m[3], 縣市代碼)
            no = _correct_landno(m[4])
            return f'{sec}{no}'
        if 錯誤傳回原值: return s
        raise ValueError(f'地號{s}格式錯誤')
    except IndexError:
        if 錯誤傳回原值: return s
        raise ValueError(f'地號{s}格式錯誤')
    except AttributeError:
        if 錯誤傳回原值: return s
        raise ValueError(f'地號{s}格式錯誤')

def 段碼(name, 縣市代碼='G'):
    s = 下載段碼表(縣市代碼)
    s['段名'] = s.段+s.小段
    if name == '慈惠一小段':
        return '0435'
    if '小段' in name:
        name = name.replace('小段', '').replace('段', '')
        try:
            r = s.query('小段 == @name').iloc[0, :]
        except IndexError:
            r = s.query('段名 == @name').iloc[0, :]

        return f'{r.所區碼}{r.代碼:04}'
    name = name.replace('段', '')
    r = s.query('段 == @name').iloc[0, :]
    return f'{r.所區碼}{r.代碼:04}'

def _correct_landno(s):
    '地號正規化為8碼，如461-1轉成04610001號，不供外部使用'
    if m:= re.match(r'(\d{1,4})(-(\d{1,4}))?', s): 
        return f'{int(m[1]):04}{int(m[3] if m[3] else 0):04}'
    raise ValueError(f'正規地號{s}格式錯誤')

def 段名(c, 縣市代碼='G'):
    '''傳回指定代碼 c 的鄉鎮市段名，例如：
land.段名('0142') ->'吉安鄉初音段'
land.段名('0917') ->'光復鄉大安一小段'
'''
    try:
        d = 下載段碼表(縣市代碼)
        s = d.query('代碼==@c').iloc[0]
        n = s.小段+'小段' if type(s.小段)==str else s.段+'段'
        ctc = s.所區碼[2:]
        ctn = 下載鄉鎮市區代碼表().query('縣市代碼==@縣市代碼 and 鄉鎮市區代碼==@ctc').iloc[0].鄉鎮市區名稱
        return f'{ctn}{n}'
    except IndexError:
        raise ValueError(f'段代碼[{c}]格式錯誤')

@cache.memoize('下載段碼表')
def 下載段碼表(縣市代碼='G'):
    url = f"https://lisp.land.moi.gov.tw/MMS/Handle/DownloadQuerySection.ashx?DownloadType=csv&CountyCode={縣市代碼}&OfficeCode=&TownCode="
    from zhongwen.檔 import 抓取
    import pandas as pd
    s = 抓取(url, encoding='utf-8-sig', 回傳資料形態='StringIO')
    return pd.read_csv(s, dtype={'代碼':str})

@cache.memoize('下載鄉鎮市區代碼表')
def 下載鄉鎮市區代碼表():
    url = f"https://lisp.land.moi.gov.tw/MMS/Handle/DownloadQueryArea.ashx?DownloadType=csv"
    from zhongwen.檔 import 抓取
    import pandas as pd
    s = 抓取(url, encoding='utf-8-sig', 回傳資料形態='StringIO')
    df = pd.read_csv(s, usecols=['縣市名稱','縣市代碼','事務所名稱','事務所代碼','鄉鎮市區名稱','鄉鎮市區代碼'], dtype={'鄉鎮市區代碼':str})
    return df
    
def countyname(code):
    '''指定 code 代碼表示的鄉鎮市名稱
land.countyname("01") -> "花蓮市"
'''
    code = int(code)
    return countydict().query('鄉鎮市區代碼==@code').iloc[0].鄉鎮市區名稱

def countycode(name):
    '''指定 name 名稱表示的鄉鎮市區代碼
land.countyname("01") -> "花蓮市"
'''
    name = name[0:2]
    c = countydict().query('鄉鎮市區名稱.str.contains(@name)').iloc[0].鄉鎮市區代碼
    return f'{c:02}'
