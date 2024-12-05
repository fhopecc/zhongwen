from zhongwen.number import 轉數值
from zhongwen.file import 下載
import pandas as pd
import re

def 機關地址(全國=False):
    from pathlib import Path
    import os
    wdir = Path(__file__).parent

    url = 'https://svrorg.dgpa.gov.tw/file/orglist.csv'
    f = 下載(url)
    df = pd.read_csv(f, encoding='cp950')
    df = df.query('裁撤註記!="是"')
    if not 全國:
        df = df.query('機關地址.str.contains("花蓮", na=False)')
    df['標準地址'] = df.機關地址.map(標準地址)
    df = df.explode('標準地址')
    return df

def 標準地址含基地(addr):
    return 標準地址(addr, True)

def 修正誤植名稱(addr):
    誤植表 = {'美崙區':''}
    for k in 誤植表:
        addr = addr.replace(k, 誤植表[k])
    return addr

def 清理冗餘或非屬地址字元(addr):
    # 消除前置郵遞區號
    pat = r'\d+(.+)'
    if m:=re.match(pat, addr):
        addr = m[1]
    
    from zhongwen.text import 轉半型
    addr = 轉半型(addr)

    # 清理最末括號
    pat = r'(.+)\(.+\)'
    if m:=re.match(pat, addr):
        addr = m[1]

    return addr

def 刪除鄰(addr):
    import re
    pat = r'[\d一二三四五六七八九]+鄰'
    return re.sub(pat, '', addr)

def 標準地址(addr, 含基地=False):
    '''
    花蓮縣道路命名暨門牌編釘自治條例
    地址的識別鍵為（鄉鎮市區名）+（道路名）+（門牌號）+[(樓層)]
    標準化：
    1.去除（縣市名）、（村里名）。
    2.將(附號)之"之"用"-"取代。
      公園路1之7號->公園路1-7號
    '''
    # 非字串不轉換
    if not isinstance(addr, str):
        return addr

    addr = 清理冗餘或非屬地址字元(addr)

    addr = 修正誤植名稱(addr)

    # 去除（縣市名）、（村里名）、（鄰號）
    pat = r'^(.+縣)?(.+[鄉鎮市])(.+[村里])?(.+鄰)?(.+[路街](.+段)?(.+巷)?)?(.+號([之]\d+)?)(.*[樓F](之\d+)?)?$'
    if m:=re.match(pat, addr):
        鄉鎮市 = 標準鄉鎮市區名(m[2])
        路名 = 標準路名(m[5])
        村里名 = m[3]
        門牌號 = m[8].strip()
        if not m[5]: # 沒有路名，門牌號前加村名
            if m[3]:
                門牌號 = 村里名 + 門牌號
        號 = 標準門牌號(門牌號)
        樓 = m[10]
        try:
            樓 = 標準樓(m[10])
        except Exception as e:
            樓 = m[10]

        if isinstance(號, list):
            基地門牌 = [''.join(filter(None, (鄉鎮市, 路名, _號))) for _號 in 號] 
        else: 
            基地門牌 = ''.join(filter(None, (鄉鎮市, 路名, 號)))

        if isinstance(基地門牌, list): 
            if isinstance(樓, list):
                adrs = [''.join(filter(None, (基地門牌[-1], _樓))) 
                       for _樓 in 樓]
                return [*基地門牌, *adrs] if 含基地 else [*(基地門牌[:-1]), *adrs]
            if 樓:
                a = ''.join(filter(None, (基地門牌[-1], 樓)))
                return [*基地門牌, a] if 含基地 else [*基地門牌[:-1], a]

        if isinstance(樓, list):
                adrs = [''.join(filter(None, (基地門牌, _樓))) 
                         for _樓 in 樓]
                return [基地門牌, *adrs] if 含基地 else adrs
        if 樓:
            a = ''.join(filter(None, (基地門牌, 樓)))
            return [基地門牌, a] if 含基地 else a

        if 基地門牌:
            return 基地門牌
    return addr

def 標準鄉鎮市區名(n):
    # 去除重覆
    pat = '(.+?[鄉鎮市])+'
    if m:=re.match(pat, n):
        return m[1]
    return n

def 標準樓(l):
    if not l: return ''
    pat = r'([^樓]樓)及([^樓]樓)'
    if m:=re.match(pat, l):
        return [標準樓(m[1]), 標準樓(m[2])]

    pat = r'.*[棟](.*)樓'
    if m:=re.match(pat, l):
        return 標準樓(m[1]+'樓')

    pat = '([^樓F]+)[樓F](之(.+))?'
    if m:=re.match(pat, l):
        l = 樓數(m[1]) 
        if isinstance(l, range) or isinstance(l, list):
            return [樓名(n) for n in l if n!=0]
        樓號 = 樓名(l)
        if (m[3]):
            樓號+= '之' + m[3] 
        return 樓號 
    return l

def 樓數(l):
    if not l:return l
    pat = r'([^~至\-]+)[~至\-](.+)'
    if m:=re.match(pat, l):
        s = 樓數(m[1])
        e = 樓數(m[2])
        return range(s, e+1)

    pat = r'[^.]+\..*'
    if re.match(pat, l):
        ls = l.split('.')
        return [樓數(l) for l in ls]

    pat = r'(B)?([^F]+)[F]?'
    if m:=re.match(pat, l):
        if m[1]:
            return -1*轉數值(m[2])
        return 轉數值(m[2])
    return l

def 樓名(n):
    l = str(abs(n))
    if n < 0: l = '地下' + l 
    return l + '樓'

def 標準門牌號(no):
    pat = r'([^號]+(([，、,])[^號]+))號'
    if m:=re.match(pat, no):return [標準門牌號(no+'號') for no in m[1].split(m[3])]

    pat = r'(\D+[村里])(([^0-9一二三四五六七八九十]+).+號.*)'
    if m:=re.match(pat, no):return 標準門牌號(m[2])

    pat = r'(\D+)[村里]([0-9一二三四五六七八九十]+.*號.*)'
    if m:=re.match(pat, no):return f'{m[1]}{標準門牌號(m[2])}'

    pat = r'(\D*)(\d+)-(\d+)號'
    if re.match(pat, no):return no

    pat = r'([^號]+)號(之([^號]+))?'
    if m:=re.match(pat, no):
        no = 號碼(m[1])
        if isinstance(no, list):
            return [f'{n}號' for n in no]
        if m[3]:
           no = no + '-' + 號碼(m[3])
        return f'{no}號'
    return no 

def 號碼(no):
    # 號碼清單 
    pat = r'([^之]+)之([^之]+)'
    if m:=re.match(pat, no):
        主號 = 號碼(m[1])
        附號 = 號碼(m[2])
        return f'{主號}-{附號}'

    pat = r'([^、.]+)(([、.])([^、.]+))+'
    if m:=re.match(pat, no):
        分隔符 = m[3]
        nos = no.split(分隔符)
        return [號碼(n) for n in nos]

    pat = r'([^\d一二三四五六七八九十百]+)(.+)'
    if m:=re.match(pat, no):
        號名 = m[1]
        號數 = 轉數值(m[2])
        return f'{號名}{號數 }'
    n = 轉數值(no)
    if n > 0: return str(n)
    return no

def 標準路名(road):
    '''
    華城五街->華城5街
    大學路二段->大學路2段
    誤植：
    民德民權四街->民權四街
    '''
    if not road: return ''
    誤植表 = {'民德民權四街':'民權四街'
             ,'ㄧ':'一'
             }
    road = road.replace('ㄧ', '一')
    for k in 誤植表: 
        road = road.replace(k, 誤植表[k])
    pat = r'(.+[路街])((.+)段)?((.+)巷)?'
    if m:=re.match(pat, road):
        r = m[1]
        pat = r'(\D+)(\d+)([路街])' 
        if mr:=re.match(pat, r):
            from zhongwen.number import 中文數字
            r = f'{mr[1]}{中文數字(mr[2])}{mr[3]}'
        if n1:=m[3]:
            r += str(轉數值(n1))+'段'
        if n2:=m[5]:
            r += str(轉數值(n2))+'巷'
        return r
    return road

def 地址合併(df1, df2, addr1, addr2, 含基地=True):
    '將2個資料指定的地址欄位先轉成標準地址再進行左合併'
    df1columns = df1.columns
    df1['標準地址'] = df1[addr1].map(lambda a:標準地址(a, 含基地))
    df1 = df1.explode('標準地址')
    df2['標準地址'] = df2[addr2].map(lambda a:標準地址(a, 含基地))
    df2 = df2.explode('標準地址')
    df1 = df1.merge(df2, how='left', on='標準地址')
    # breakpoint()
    if addr1==addr2:
        addr1=addr1+"_x"
        addr2=addr1+"_y"
    df2start_column_name = df1.columns[df1.shape[1]-df2.shape[1]+1]
    df1['合併有效筆數'] = df1.groupby(addr1)[df2start_column_name].transform('count')
    df1 = pd.concat([df1.query('合併有效筆數==0')
                    ,df1.query('合併有效筆數>0')[df1[df2start_column_name].notna()]
                    ]
                    )
    del df1['標準地址']
    df1.drop_duplicates(inplace=True)
    df1.sort_values(df1.columns[0], inplace=True)
    df1.reset_index(drop=True, inplace=True)
    df1.index = df1.index+1
    return df1

def 地址座標(addr):
    '''取得指定地址之點座標，用法：
LAND.addr_geocoding('花蓮市中美路295之59號')'''
    #addr = address(addr)
    url = f'https://api.tomtom.com/search/2/geocode/{addr}.json?&key=22qLzwADkhNjl5lduwql5eN6qS9ARwoK&countrySet=TWN&language=zh-TW&limit=1'
    import requests
    response = requests.get(url)
    data = response.text
    print(data)
    import json
    js = json.loads(str(data))
    from shapely.geometry import Point
    #可能所有人都至少一次踩过这个坑：地理坐标点用字符串形式表示时是纬度在前，经度在后（ "latitude,longitude" ），而数组形式表示时是经度在前，纬度在后（ [longitude,latitude] ）—顺序刚好相反。 其实，在 Elasticesearch 内部，不管字符串形式还是数组形式，都是经度在前，纬度在后。不过早期为了适配 GeoJSON 的格式规范，调整了数组形式的表示方式。 因此，在使用地理位置的路上就出现了这么一个“捕熊器”，专坑那些不了解这个陷阱的使用者。
    [y, x]=list(js['results'][0]['position'].values())
    return Point(x, y)
