from pathlib import Path
from diskcache import Cache
cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

@cache.memoize('載入交通事故資料')
def 載入交通事故資料(事故資料目錄):
    '''
    一、座標系為經緯度，即EPSG 4326。
    二、要計算距離要先轉成TWD97(EPSG:3826：TM2，中央經線121度)之圖資，單位為公尺。
    三、欄位：發生年度、發生日期、死亡、受傷、geometry
    四、政府資料開放平台即時交通事故資料為年初至前2週之事故資料。
        即時交通事故資料(A1類)(https://data.gov.tw/dataset/12818)
        即時交通事故資料(A2類)(https://data.gov.tw/dataset/13139)
    五、112年傷亡道路交通事故資料(https://data.gov.tw/dataset/167905)
        113年傷亡道路交通事故資料(https://data.gov.tw/dataset/172969)
        114年傷亡道路交通事故資料(https://data.gov.tw/dataset/177136)
    '''
    from zhongwen.表 import 顯示
    from zhongwen.時 import 取日期
    from pathlib import Path
    import geopandas as gpd
    import pandas as pd
    事故資料目錄 = Path(事故資料目錄)
    csvs = 事故資料目錄.glob('*.csv')
    df = pd.concat([pd.read_csv(csv, dtype={'發生時間':str}) for csv in csvs])
    df['發生日期'] = df.發生日期.map(取日期)
    df['發生年度'] = df['發生年度'].astype(str).str.strip()
    df['發生地點'] = df.發生地點.replace({'一段': '1段', '二段': '2段'
                                         ,'三段': '3段'
                                         ,'四段': '4段'
                                         ,'五段': '5段'
                                         ,'六段': '6段'
                                         ,'七段': '7段'
                                         ,'八段': '8段'
                                         ,'九段': '9段'
                                         }, regex=True)
    df['發生地點'] = df.發生地點.str.replace('附近', '', regex=False)
    df['發生地點'] = df.發生地點.str.replace('路口', '路', regex=False)
    df['發生地點'] = df.發生地點.str.replace('段口', '段', regex=False)
    df['發生地點'] = df.發生地點.str.replace('街口', '街', regex=False)
    pattern = r'(^.*?[鄉鎮市區])'
    df['發生區域'] = df.發生地點.str.extract(pattern)
    df['車種'] = df["當事者區分-類別-大類別名稱-車種"]
    df['車種子類'] = df["當事者區分-類別-子類別名稱-車種"]
    df['肇因大類'] = df["肇因研判大類別名稱-主要"]
    df['肇因子類'] = df["肇因研判子類別名稱-主要"]
    df['肇因個別'] = df["肇因研判子類別名稱-個別"]
    df[['死亡', '受傷']] = df['死亡受傷人數'].str.extract(r'死亡(\d+);受傷(\d+)').astype(float)
    df['死亡'] = df.死亡.fillna(0)
    df['受傷'] = df.受傷.fillna(0)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['經度'], df['緯度']), crs='epsg:4326')
    # gdf = gdf.to_crs(epsg=3826)
    return gdf

def 取區域事故統計(發生地點="花蓮縣"):
    from zhongwen.表 import 取數據輪廓
    df = 載入交通事故資料(Path(__file__).parent / '2.事故資料')
    df = df.query('發生地點.str.contains(@發生地點) and 當事者順位==1')
    df = 取數據輪廓(df)
    return df

@cache.memoize('取路口交通事故資料')
def 取路口交通事故資料(地區 = "花蓮縣, 臺灣"):
    '''
    一、取出開放街圖路網路口中心20公尺內之交通事故資料，
        其事故道路型態大類別名稱為交岔路。
    二、欄位：路口x座標、路口y座標、路口名稱、發生年度、發生日期、死亡、受傷、
        肇因子類、geometry
    三、路口唯一識別路口 x, y 座標，主要係整併路口中心20公尺內事故資料。
    三、標準路口名稱：縣+鄉鎮市區+路口集合
    '''
    from zhongwen.開放街圖 import 取路口, cache as dcache
    from zhongwen.地圖 import 顯示地圖
    from zhongwen.文 import 取集合
    from zhongwen.表 import 表示
    from pathlib import Path
    import geopandas as gpd
    import os
    路口 = 取路口(地區)
    target_crs = "EPSG:3826"
    intersections_proj = 路口.to_crs(target_crs)
    事故資料 = 載入交通事故資料(Path(__file__).parent / '2.事故資料').to_crs(target_crs)

    # 2. 為路口建立 20 公尺的緩衝區 (Buffer)
    # 這會把 Point 變成一個個半徑 30m 的圓形 Polygon
    intersections_buffer = intersections_proj.copy()
    intersections_buffer['geometry'] = intersections_proj.buffer(20)
    # 3. 執行空間連接 (Spatial Join)
    # 'inner' 代表只保留有發生過事故的路口，'left' 則保留所有路口
    # op='contains' 或 'intersects' 代表找出落在圓圈內的事故點
    joined = gpd.sjoin(事故資料, intersections_buffer, how='inner'
                      ,predicate='intersects')
    joined = joined.query('道路型態大類別名稱=="交岔路"') 
    joined['標準路口名稱'] = joined.路口名稱.map(取集合).map(lambda s:''.join(sorted(list(s), key=str)))
    joined['標準路口名稱'] = joined.apply(lambda r: f'{r["發生區域"]}{r["標準路口名稱"]}'
                                         ,axis=1)
    return joined

@cache.memoize('取路口歷年事故情形')
def 取路口歷年事故情形(地區 = "花蓮縣, 臺灣"):
    '''
    一、統計區分：路口、年度
    二、路口識別：路口 x, y 座標
    三、科技執法資料：設置地點、取締項目
    四、事故涉多當事者，僅取當事者順位為1之事故紀錄。
    五、統計項：件數、死亡、受傷、各肇因件數。
    六、路口相同者，亦即鄉鎮市區及標準路口名相同者，只取末筆紀錄。
    '''
    from zhongwen.表 import 表示, 多級欄位扁平化
    from zhongwen.文 import 取集合
    from pathlib import Path
    import geopandas as gpd
    import pandas as pd
    事故資料 = 取路口交通事故資料(地區)
    事故資料 = 事故資料.query('當事者順位==1') 
    # 1. 統計各路口事故件數、死亡人數及受傷人數，路口以 x, y 座標區分。
    路口事故統計 = 事故資料.groupby(['路口x座標', '路口y座標'
                                    ,'發生區域', '路口名稱', '發生年度']).agg(
        {'geometry': 'count'
        ,'死亡':'sum'
        ,'受傷':'sum'
        })

    def 取肇因統計(group):
        # 對該群組內的肇因進行件數加總
        cause_counts = group.groupby('肇因子類')['geometry'].count()
        # 按件數由大到小排序
        sorted_causes = cause_counts.sort_values(ascending=False)
        # 格式化為 "肇因(件數)" 形式
        formatted_list = [f"{cause}({count})" for cause, count in sorted_causes.items()]
        # 用逗號連結
        return "、".join(formatted_list)

    df_str = 事故資料.groupby(['路口x座標', '路口y座標', '發生區域', '路口名稱', '發生年度']
                             ).apply(取肇因統計).to_frame(name='各肇因件數')

    路口事故統計 = pd.concat([路口事故統計, df_str], axis=1)
    路口事故統計 = 路口事故統計.rename(columns={'geometry':'件數'})
    路口事故統計 = 路口事故統計.unstack(level='發生年度')
    路口事故統計 = 路口事故統計.reset_index()
    路口事故統計 = 多級欄位扁平化(路口事故統計)
    路口事故統計['標準路口名'] = 路口事故統計.路口名稱.map(取集合).map(lambda s:''.join(sorted(list(s), key=str)))
    路口事故統計['鄉鎮市區'] = 路口事故統計.發生區域
    df1 = 路口事故統計
    df2 = 載入設置科技執法路口()
    df = df1.merge(df2, how='left', on=['鄉鎮市區', '標準路口名'])
    dfdebug = df2.merge(df1, how='left', on=['鄉鎮市區', '標準路口名'])
    dfdebug = dfdebug.query('路口名稱.isna()')
    # 表示(dfdebug)
    df = df.drop_duplicates(subset=['鄉鎮市區', '標準路口名'], keep='last')
    df['科技執法'] = df.取締項目.notna().replace({True:'科技執法', False:'無科技執法'})
    # df1 = 路口事故統計
    # df2 = 載入交通事故資料(Path(__file__).parent / '2.事故資料')
    # df2['鄉鎮市區'] = df2.發生區域
    # df = df1.merge(df2, how='left', on=['鄉鎮市區', '標準路口名'])
    # dfdebug = df2.merge(df1, how='left', on=['鄉鎮市區', '標準路口名'])
    # dfdebug = dfdebug.query('路口名稱.isna()')
    # 表示(dfdebug)
    # df = df.drop_duplicates(subset=['鄉鎮市區', '標準路口名'], keep='last')
    return df

def 載入設置科技執法路口():
    '''
    一、主鍵：鄉鎮市區、標準路口名、設置地點、取締項目
    '''
    from zhongwen.文 import 取集合
    import pandas as pd
    xlsx = r'g:\我的雲端硬碟\00.115-1警察局114年度決算抽查114.12.22-115.1.6\04.道安專調底稿115年4月15日查復\警附表.xlsx'
    df = pd.read_excel(xlsx, '設置科技執法路口')
    df['標準路口名'] = df.標準路口名.map(取集合).map(
            lambda s:''.join((sorted(list(s), key=str))))
    return df

def 交通事故死亡資料():
    df = 載入交通事故案件檔()
    df['當事者死亡'] = df['22.受傷程度'].str.contains("死亡")
    df['發生年度'] = df.發生年度-1911
    df['當事者事故發生時年齡'] = pd.to_numeric(df.當事者事故發生時年齡, errors='coerce')
    df = df.query('當事者死亡')
    年齡分類 = [0, 13, 18, 25, 30, 45, 65, float('inf')]
    年齡標籤 = ["兒童", "少年", "年輕人", "成年期", "壯年期", "中年期","高齡者"]
    df["年齡層"] = pd.cut(df.當事者事故發生時年齡, bins=年齡分類, labels=年齡標籤, right=False)
    return df

def 交通事故高齡者死亡使用運具統計():
    df = 交通事故死亡資料()
    df = df.rename(columns={"26.當事者區分(類別)":"車種"})
    df = df.query('年齡層=="高齡者"')
    df = df.groupby(["發生年度", '車種'])[["總編號(案件編號)"]].count()
    df = df.unstack(level=-1).fillna(0).astype(int)
    return df

def 交通事故各年度各年齡層死亡人數統計():
    import pandas as pd
    df = 交通事故死亡資料()
    df = df.groupby(['發生年度', '年齡層'])[["總編號(案件編號)"]].count()
    df = df.unstack(level=-1)
    return df

def 交通事故高齡者死亡人數():
    df = 載入交通事故案件檔()
    df['發生年度'] = df.發生年度-1911
    df['死亡人數'] = pd.to_numeric(df['3-1.24小時內死亡人數'], errors='coerce').fillna(0) + pd.to_numeric(df['3-2.2-30日內死亡人數'], errors='coerce').fillna(0)
    df['當事者事故發生時年齡'] = pd.to_numeric(df.當事者事故發生時年齡, errors='coerce')
    df['高齡者'] = df.當事者事故發生時年齡>=65
    df['當事者死亡'] = df['22.受傷程度'].str.contains("死亡")
    # print(df.columns.tolist())
    df = df.query('高齡者 and 當事者死亡')
    df = df.rename(columns={"2-1.發生市區鄉鎮":"發生市區鄉鎮"})
    
    df = df.groupby(['發生市區鄉鎮', '發生年度'])[['當事者順位']].count()
    df = df.rename(columns={"當事者順位":"高齡者死亡人數"})
    df = df.unstack(level=-1).fillna(0).astype(int)
    df = df.sort_values([('高齡者死亡人數', 112)], ascending=False)
    return df

def 高齡者事故防制安全推廣情形():
    df = 載入交通事故案件檔()
    df['當事者事故發生時年齡'] = pd.to_numeric(df.當事者事故發生時年齡, errors='coerce')
    df['高齡者'] = df.當事者事故發生時年齡>=65
    # print(df.columns.tolist())
    df = df.query('高齡者==True')
    df = df.groupby(['2-1.發生市區鄉鎮', '發生年度', '事故類別'])['總編號(案件編號)'].count()
    df = df.unstack(level=-1).unstack(level=-1).fillna(0)
    df = df.sort_values([('A1', 2023), ('A2', 2023)], ascending=[False, False])

    f = Path(__file__).parent.parent / '高齡者交通事故防制措施' / '高齡者宣導情形.xlsx'
    df2 = pd.read_excel(f)
    df2['宣導'] = '宣導次數'
    df2 = df2.groupby(['鄉鎮市', '年度', '宣導']).序號.count().unstack(level=-1).unstack(level=-1)
    df2 = df2.fillna(0)
    df = pd.concat([df, df2], axis=1)
    df = df.fillna(0)
    return df

def 交通事故類別分析():
    df = 載入交通事故案件檔()
    df = df[['總編號(案件編號)', '發生年度', '事故類別']].drop_duplicates()
    df = df.groupby(['發生年度', '事故類別'])[['總編號(案件編號)']].count()
    df = df.rename(columns={'總編號(案件編號)':'件數'})
    df = df.unstack()
    return df

def 交通事故死亡人數統計():
    df = 載入交通事故案件檔()
    df['死亡人數'] = pd.to_numeric(df['3-1.24小時內死亡人數'], errors='coerce').fillna(0) + pd.to_numeric(df['3-2.2-30日內死亡人數'], errors='coerce').fillna(0)
    df = df[['總編號(案件編號)', '發生年度', '死亡人數']].drop_duplicates()
    df = df.groupby('發生年度').死亡人數.sum().astype(int)
    return df

def 交通事故各年度各年齡層使用運具死亡人數統計():
    import pandas as pd
    df = 交通事故死亡資料().query('發生年度==112')
    df = df.rename(columns={"26.當事者區分(類別)":"車種"})
    df = df.groupby(['年齡層', '車種'])[["總編號(案件編號)"]].count()
    df = df.unstack(level=-1)
    return df

def 統計各車種事故數(事故資料目錄):
    df = 載入交通事故資料(事故資料目錄)
    df = df.query('處理單位名稱警局層.str.contains("花蓮", na=False)')
    df = df.groupby(["當事者區分-類別-大類別名稱-車種", "當事者區分-類別-子類別名稱-車種"]).count()	
    return df

def 統計車種事故數(事故資料目錄):
    df = 載入交通事故資料(事故資料目錄)
    df = df.query('處理單位名稱警局層.str.contains("花蓮", na=False)')
    df = df.groupby(["當事者區分-類別-大類別名稱-車種", "當事者區分-類別-子類別名稱-車種"]).count()	
    return df

def 闖紅燈直行事故統計():
    from zhongwen.表 import 顯示
    from zhongwen.地圖 import 顯示地圖
    from pathlib import Path
    import os
    df = 取多事故路口事故明細()
    df = df.query('處理單位名稱警局層.str.contains("花蓮", na=False)')
    df = df.query('當事者順位==1')
    # df = df.query('肇因子類.str.contains("闖紅燈直行", na=False)')
    maxyear = df.發生年度.max()
    df = df.groupby(['發生地點', '發生年度']).agg({'發生日期':'count'
                                                  ,'死亡':sum
                                                  ,'受傷':sum})
    df = df.rename(columns={'發生日期':'件數'})
    df = df.unstack().sort_index(axis=1)
    df.columns = ['_'.join(map(str, col)) for col in df.columns]
    df = df.fillna(0)
    df = df.sort_values(by=[f'件數_{maxyear}'
                           ,f'死亡_{maxyear}'
                           ,f'受傷_{maxyear}'], ascending=False)
    return df

def 取科技執法路口歷年事故情形():
    from zhongwen.表 import 表示
    from zhongwen.文 import 取集合, 臚列
    import pandas as pd
    import os
    df = 取路口歷年事故情形()
    df = df.query('取締項目.notna()')
    return df

def 取傷亡交通事故件數前百大路口():
    '''
    一、欄位：路口x座標、路口y座標、路口名稱、件數_2023、件數_2024、件數_2025……、
        死亡_2023、死亡_2024、死亡_2025……、受傷_2023、受傷_2024、受傷_2025……、
        各肇因件數_2023、各肇因件數_2024、各肇因件數_2025……、geometry
    二、路口資料：鄉鎮市區、標準路口名
    '''
    from zhongwen.表 import 表示
    import geopandas as gpd
    df = 取路口歷年事故情形()
    gdf = gpd.GeoDataFrame(
        df, 
        geometry=gpd.points_from_xy(df['路口x座標']
                                   ,df['路口y座標'])
                                   ,crs="EPSG:4326"
    )
    gdf.sort_values('件數_2025', ascending=False, inplace=True)
    gdf = gdf.head(100)
    gdf['主要肇因'] = gdf.各肇因件數_2025.str.split('、').str[0].str.replace(r'\(\d+\)', '', regex=True)
    gdf['次要肇因'] = gdf.各肇因件數_2025.str.split('、').str[1].str.replace(r'\(\d+\)', '', regex=True)
    gdf['較上年度增加'] = (gdf['件數_2025'] > gdf['件數_2024']).replace(
            {True:'是', False:'否'})
    gdf['科技執法'] = df.取締項目.notna().replace({True:'科技執法', False:'無科技執法'})
    gdf['無號誌路口'] = ((df.各肇因件數_2024.str.contains('無號誌', na=False) | 
                          df.各肇因件數_2025.str.contains('無號誌', na=False) ) & 
                        ~(df.各肇因件數_2024.str.contains('有號誌', na=False) |  
                          df.各肇因件數_2025.str.contains('有號誌', na=False)  
                         )).replace({True:'是', False:'否'})
    gdf.reset_index(drop=True, inplace=True)
    gdf.index = gdf.index+1
    return gdf

@cache.memoize('取大型貨車事故')
def 取大型貨車事故():
    '''
    一、砂石(大型貨)車係車種為大貨車、曳引車、半聯結車及全聯結車之事故。
    '''
    from zhongwen.開放街圖 import 取路段
    from zhongwen.表 import 表示
    from pathlib import Path
    import geopandas as gpd
    # cache.clear()
    r = 取路段().to_crs(epsg=3826)
    a = 載入交通事故資料(Path(__file__).parent / '2.事故資料').to_crs(epsg=3826)
    # 轉為 GeoDataFrame (WGS84 -> TWD97)
    a = a.query('處理單位名稱警局層.str.contains("花蓮", na=False)')
    # a = a.query('事故位置大類別名稱.str.contains("路段", na=False)')
    a = a.query('車種.str.contains("大貨車|曳引車|半聯結車|全聯結車", na=False)')
    a = a.query('當事者順位==1')
    # B. 準備事故點資料 (假設你已有一個包含經緯度的 df)
    # 這裡建立範例數據
    # C. 空間匹配：找尋每筆事故最近的路段
    # max_distance 設為 20 公尺，避免匹配到太遠的路
    a = gpd.sjoin_nearest(a, r, max_distance=20, distance_col="與路段中心距離")
    # 排除事故重覆者
    a = a.drop_duplicates(subset=['發生年度', '發生月份', '發生日期'
                                 ,'發生時間', '事故類別名稱'
                                 ,'處理單位名稱警局層', '發生地點', '天候名稱'
                                 ,'光線名稱', '道路類別-第1當事者-名稱'], keep='last')
    return a

@cache.memoize('取特定肇因傷亡交通事故件數路口')
def 取特定肇因傷亡交通事故件數路口(肇因="闖紅燈直行"):
    '''
    一、統計區分：路口、年度
    二、路口資料：鄉鎮市區、標準路口名
    三、科技執法資料：設置地點、取締項目
    四、事故涉多當事者，僅取當事者順位為1之事故紀錄。
    五、統計項：件數(肇因)、死亡(肇因)、受傷(肇因)。
    六、路口相同者，亦即鄉鎮市區及標準路口名相同者，只取末筆紀錄。
    '''
    from zhongwen.表 import 表示, 多級欄位扁平化
    from zhongwen.文 import 取集合
    from pathlib import Path
    import geopandas as gpd
    import pandas as pd
    import osmnx as ox
    import sys
    事故資料 = 取路口交通事故資料()
    事故資料 = 事故資料.query('當事者順位==1 and 肇因子類.str.contains("闖紅燈直行")') 
    # 1. 統計各路口事故件數、死亡人數及受傷人數，路口以 x, y 座標區分。
    路口事故統計 = 事故資料.groupby(['路口x座標', '路口y座標'
                                    ,'發生區域', '路口名稱', '發生年度']).agg(
        {'geometry': 'count'
        ,'死亡':'sum'
        ,'受傷':'sum'
        })
    路口事故統計 = 路口事故統計.rename(columns={'geometry':'件數'})
    路口事故統計 = 路口事故統計.unstack(level='發生年度')
    路口事故統計 = 路口事故統計.reset_index()
    路口事故統計 = 多級欄位扁平化(路口事故統計)
    路口事故統計['標準路口名'] = 路口事故統計.路口名稱.map(取集合).map(lambda s:''.join(sorted(list(s), key=str)))
    路口事故統計['鄉鎮市區'] = 路口事故統計.發生區域
    df1 = 路口事故統計
    df2 = 載入設置科技執法路口()
    df = df1.merge(df2, how='left', on=['鄉鎮市區', '標準路口名'])
    df = df.drop_duplicates(subset=['鄉鎮市區', '標準路口名'], keep='last')
    df['科技執法'] = df.取締項目.notna().replace({True:'科技執法', False:'無科技執法'})
    df['較上年度增加'] = (df.件數_2025 > df.件數_2024).replace({True:'是', False:'否'})
    df['座標'] = df.apply(lambda r: f"{r['路口x座標']}\n{r['路口y座標']}", axis=1)
    df['路口名稱'] = df.鄉鎮市區.str.replace('花蓮縣', '') + df.路口名稱
    df.columns = df.columns.str.replace('_', f'({肇因})_')
    return df

@cache.memoize('取傷亡交通事故件數前百大路口事故明細')
def 取傷亡交通事故件數前百大路口事故明細():
    '''
    一、僅取當事者順位為1之紀錄。
    '''
    df = 取路口交通事故資料()
    df = df.query('當事者順位==1')
    df1 = 取傷亡交通事故件數前百大路口()[["路口x座標", "路口y座標", "件數_2025", "取締項目"]]
    df = df.merge(df1, on=["路口x座標", "路口y座標"]) 
    return df

def 取指定肇因前百大路口事故明細(肇因='闖紅燈直行'):
    df = 取傷亡交通事故件數前百大路口事故明細()
    df = df.query(f'當事者順位==1 and 肇因子類.str.contains("{肇因}")') 
    df['取締項目'] = df.取締項目.fillna("無")
    df = df.groupby(["路口x座標", "路口y座標", "標準路口名稱", "件數_2025", "發生年度", "取締項目"]).agg(
            {'geometry':'count', '受傷':sum})
    df.columns = [f'{肇因}件數', f'{肇因}肇事受傷人數']
    df = df.reset_index()
    return df

def 統計前百大路口指定肇因事故歷年件數(肇因='闖紅燈直行'):
    from zhongwen.表 import 表示, 取數據輪廓, 多級欄位扁平化
    from zhongwen.快取 import 刪除指定名稱快取
    # 刪除指定名稱快取(cache, '取傷亡交通事故件數前百大路口事故明細')
    df = 取指定肇因前百大路口事故明細(肇因)
    df= df.pivot_table(
        index=['路口x座標', '路口y座標', '標準路口名稱', '件數_2025', '取締項目'],
        columns='發生年度',
        values=[f'{肇因}件數', f'{肇因}肇事受傷人數']
    )
    df = df.reset_index()
    df = 多級欄位扁平化(df)
    df = df.fillna(0)
    df['路口中心座標'] = df.apply(lambda r: f'{r["路口x座標"]}\n{r["路口y座標"]}'
                                 ,axis=1)
    df['路口名稱'] = df.標準路口名稱.str.replace("花蓮縣", "")
    df['占件數比率'] = df[f'{肇因}件數_2025'] / df.件數_2025 * 100
    df['增加件數'] = df[f'{肇因}件數_2025'] - df[f'{肇因}件數_2024']
    df['增加人數'] = df[f'{肇因}肇事受傷人數_2025'] - df[f'{肇因}肇事受傷人數_2024']
    df = df.sort_values([f'{肇因}件數_2025', '件數_2025'], ascending=False)
    df = df[['路口中心座標', '路口名稱', '件數_2025', '取締項目'
            ,'左轉件數_2025', '占件數比率',  '左轉件數_2024', '增加件數'
            ,'左轉肇事受傷人數_2025', '左轉肇事受傷人數_2024', '增加人數']]
    return df

def 統計大型貨車事故肇因件數():
    df = 取大型貨車事故()
    # 表示(取數據輪廓(df))
    df = df.groupby('肇因個別').geometry.count()
    df = df.sort_values(ascending=False)
    df = df.to_frame()
    df.columns = ['件數']
    df = df.reset_index()
    return df

def 統計大型貨車事故歷年肇因件數():
    from zhongwen.表 import 表示, 取數據輪廓
    df = 取大型貨車事故()
    df = df.groupby(['發生年度', '肇因個別']).geometry.count()
    df = df.reset_index()
    df = df.rename(columns={'geometry':'件數'})
    df = df.pivot_table(index = '肇因個別'
                       ,columns = '發生年度'
                       ,values = '件數'
                       )
    df = df.fillna(0)
    df = df.sort_values('2025', ascending=False)
    df = df.reset_index()
    return df

if __name__ == '__main__':
    import os
    from zhongwen.表 import 表示
    df = 取大型貨車事故()
    df = df.query('肇因個別.str.contains("恍神|疲勞")')
    表示(df)
