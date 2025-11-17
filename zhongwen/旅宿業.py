'旅宿業資訊研析'
from diskcache import Cache
from pathlib import Path
import functools

cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

def 載入合法民宿(datadir):
    '縣府提供合法民宿基本資料，含客房面積、員工人數、客房數'
    f = 最新檔(datadir, '**/*民宿基本資料*.xlsx')
    df = pd.read_excel(f)
    df = df.rename(columns={'客房總樓地板面積(m²)':'客房總樓地板面積'
        ,'合計總房間數':'總房間數'})
    df = df.query('not 地址.isna()')
    df['標準地址'] = df.地址.map(標準地址)
    df = df.explode('標準地址')
    return df 

def 逾免稅經營規模之合法民宿(hoteldir):
    '財政部90年12月27日台財稅字第0900071529號函'
    df = 合法民宿(hoteldir, recache=True)
    df = df.query('客房總樓地板面積>150 or 總房間數>5 or 總經營人數>2')
    return df

@cache.memoize('載入旅宿')
def 載入旅宿(j):
    '''
    一、交通部觀光資訊資料庫-旅館民宿資料下載 json 格式資料。
    二、載入 j 指定的 json 格式旅宿資料。
    三、HotelClass代碼：1.國際觀光旅館、2.一般觀光旅館、3.一般旅館、4.民宿、
        5.露營區、9.其他
    '''
    from zhongwen.表 import 顯示
    from pathlib import Path
    from io import StringIO
    import pandas as pd
    import json
    df = pd.read_json(StringIO(j.read_text(encoding='utf-8-sig')))
    df = pd.json_normalize(df["Hotels"])
    df['HotelClasses'] = df.HotelClasses.astype(str)
    return df

def 好客民宿統計():
    from zhongwen.表 import 顯示
    df = 載入旅宿()
    df = df.query('HotelClasses.str.contains("4")') # 僅民宿
    df = df.groupby(['PostalAddress.City'], as_index=False).agg(
            民宿數=('HotelID', 'count'), 好客民宿數=('TaiwanHost', 'sum'))
    df['好客民宿比例'] = df.好客民宿數 / df.民宿數 * 100  
    df = df.rename(columns={'PostalAddress.City':'市縣'})
    df = df.sort_values('好客民宿比例', ascending=False)
    df.reset_index(drop=True, inplace=True)
    df.columns.name = '編號'
    df.index = df.index+1
    顯示(df) 

def 星級旅館統計():
    from zhongwen.表 import 顯示
    df = 載入旅宿()
    print(df.describe())
    df = df.query('HotelClasses.str.contains("1|2|3")') # 僅旅館
    df = df.groupby(['PostalAddress.City'], as_index=False).agg(
            旅館數=('HotelID', 'count'), 星級旅館數=('TaiwanHost', 'sum'))
    df['星級旅館占比'] = df.星級旅館數 / df.旅館數 * 100  
    df = df.rename(columns={'PostalAddress.City':'市縣'})
    df = df.sort_values('星級旅館占比', ascending=False)
    df.reset_index(drop=True, inplace=True)
    df.columns.name = '編號'
    df.index = df.index+1
    顯示(df)

@functools.cache
@cache.memoize('取環保標章旅館明細')
def 取環保標章旅館明細(csv, 市縣=None):
    '''
    一、環境部環境資料開放平臺-環保標章旅館資料
        (https://data.moenv.gov.tw/dataset/detail/GP_P_42)
    '''
    from zhongwen.表 import 顯示
    from zhongwen.時 import 取日期
    import pandas as pd
    if 市縣:
        return 取環保標章旅館明細(csv).query('corpaddress.str.contains(@市縣)')
    df = pd.read_csv(csv)
    df['signdate'] = df.signdate.map(取日期)
    df['expiredate'] = df.expiredate.map(取日期)
    print(df.describe())
    return df

def 統計環保標章旅館(csv):
    from zhongwen.表 import 顯示
    cache.clear()
    csv = Path(__file__).parent / '環保標章旅館資料.csv'
    df = 取環保標章旅館明細(csv, '花蓮')
    df = df.groupby('note').namezh.count()
    顯示(df) 

def 統計各類旅宿比重():
    from zhongwen.表 import 顯示
    df = 載入旅宿()
    df = df[df["PostalAddress.City"].str.contains("花蓮")] 
    df = df.groupby('HotelClasses').HotelName.count()
    顯示(df, 無格式=True)

@functools.cache
@cache.memoize('載入旅宿檢查明細表')
def 載入旅宿檢查明細表():
    from zhongwen.表 import 顯示
    from pathlib import Path
    import pandas as pd
    f = Path(__file__).parent / '02.旅宿業管理情形調查表(彙整).xlsx'
    df = pd.concat(pd.read_excel(f, name, header=2) for name in ['表4-1旅館檢查', '表4-2民宿檢查'])
    df = df.dropna(subset=['鄉鎮別'])
    df['名稱'] = df.民宿名稱.fillna(df.旅館名稱)
    def 取違規態樣(違規情形):
        if '非法經營' in 違規情形:
            return '非法經營'
        if '保險逾期' in 違規情形:
            return '保險逾期'
        if '擴大' in 違規情形:
            return '非法擴大經營'
        if '其他' in 違規情形:
            return '其他'
        return 違規情形
    df['違規態樣'] = df['違法(規)情形內容說明及細項'].map(取違規態樣)
    return df
 
def 旅宿違規統計():
    from zhongwen.表 import 顯示
    from pathlib import Path
    import pandas as pd
    f = Path(__file__).parent / '02.旅宿業管理情形調查表(彙整).xlsx'
    df = pd.read_excel(f, '表4-2民宿檢查', header=2) 
    df = df.dropna(subset=['鄉鎮別'])
    dfa = df
    df = pd.read_excel(f, '表4-1旅館檢查', header=2) 
    df = df.dropna(subset=['鄉鎮別'])
    dfa = pd.concat([dfa, df])
    dfa['名稱'] = dfa.民宿名稱.fillna(dfa.旅館名稱)
    def 取違規類型(違規情形):
        if '非法經營' in 違規情形:
            return '非法經營'
        if '保險逾期' in 違規情形:
            return '保險逾期'
        if '擴大' in 違規情形:
            return '非法擴大經營'
        if '其他' in 違規情形:
            return '其他'
        return 違規情形
    dfa['違規類型'] = dfa['違法(規)情形內容說明及細項'].map(取違規類型)
    # print(dfa.describe())
    dfa = dfa.groupby('違規類型')['名稱'].count()
    顯示(dfa, 顯示索引=True, 顯示筆數=2000)

def 旅宿經連續查獲違規統計():
    from zhongwen.表 import 顯示
    df = 載入旅宿檢查明細表()
    df = df.groupby(['名稱', '違規態樣'], as_index=False)['檢查日期'].agg(
            ['count', 'min', 'max'])
    df = df.query('count>1 and 違規態樣=="非法刊登廣告"')
    顯示(df, 顯示筆數=2000)

def 載入非法旅宿(xlsx, sheet_names=['表3-1非法旅館', '表3-2非法民宿']):
    from zhongwen.智 import 取搜尋連結
    from zhongwen.表 import 顯示
    from pathlib import Path
    import pandas as pd
    df = pd.concat(pd.read_excel(xlsx, name, header=2) for name in sheet_names)
    df = df.dropna(subset='營業現況')
    df['查詢Google'] = df.中文名稱.map(取搜尋連結)
    df.reset_index(drop=True, inplace=True)
    df.index = df.index+1
    df['編號'] = df.index
    return df 

def 產製檢視旅宿網非法旅宿廣告結果(xlsx, sheet_names=['表3-1非法旅館', '表3-2非法民宿']):
    from zhongwen.表 import 顯示, 取名稱帶同名圖片超文件碼
    import os
    df = 載入非法旅宿(xlsx, sheet_names)
    df['中文名稱'] = df.apply(
            lambda r: 取名稱帶同名圖片超文件碼(r.中文名稱
                                              ,'01.訂房網檢視結果'
                                              ,'100%'
                                              ,顯示名稱=f'{r.編號}.{r.中文名稱}')
            ,axis=1
            )
    html = Path(__file__).parent / '114年10月23日產製檢視旅宿網非法旅宿廣告結果.html'
    s = df[['中文名稱']].style
    s = s.set_caption(html.stem)
    s.hide(axis='index')
    s.to_html(html
             ,escape=False)
    os.system(f'start {html}')
