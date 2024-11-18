from diskcache import Cache
from pathlib import Path

cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

@cache.memoize('載入都市計畫圖')
def 載入都市計畫圖(圖檔目錄):
    'epsg:3826'
    from pathlib import Path
    import geopandas as gpd
    import pandas as pd
    shpdir = Path(圖檔目錄)
    shps = [shp for shp in shpdir.glob('*.shp')]
    gdf = pd.concat([gpd.read_file(shp, encoding='cp950') for shp in shps])
    gdf = gdf.set_crs('epsg:3826')
    return gdf

def 農保區():
    return 都市計畫分區圖().query('分區.str.contains("保護|農業")')

def 都市計畫分區圖():
    return gpd.read_file(land.r / '1100424花蓮縣都市計畫分區.gdb', layer=1) 

def 都市土地(ldir):
    u = 都市計畫分區圖()
    ul = gpd.overlay(u, 地籍圖(ldir),  how='intersection')
    ul['土地都市計畫範圍率'] = ul.area / ul.面積
    #ul = ul[['稅籍地號', '土地都市計畫範圍率']].drop_duplicates()
    #l = land.地籍圖()
    #ul = l.merge(ul, on='稅籍地號')
    return ul

def urbanplan():
    return 都市計畫分區圖()


def pfarm_district():
    '保護區農業區'
    return 農保區()

def penalty():
    '都計違規裁罰紀錄，地理資訊相當完整'
    p = gpd.read_file(land.r / '1100421都計容許使用' /'都計業務.gdb', layer=1) 
    p['地號'] = p.SecLandID.map(utils.nvl(land.name, ''))
    p['P_DATE']=p.P_DATE.map(pd.to_datetime).dt.tz_localize(None)
    d = datetime(1999, 9, 15)
    p.loc[p['P_DATE']==d, 'P_DATE']=datetime(2010, 9, 15)
    p['違規案件種類']=p.ViolationNum.str[:1].map(
            {'A':'情節重大案件', 'B':'特定行業案件', 'C':'一般行業或行為案件'})
    p['裁罰次數']=p.ViolationNum.str[-3:].astype(int)
    p['裁罰次數']=p.groupby('地號').裁罰次數.transform(max)
    p['最近裁處日期'] = p.groupby('地號').P_DATE.transform(max)
    p['最近限改期限']=p.P_DATE + pd.to_timedelta(30, unit='D')
    p['逾限日數']= (audit_date - p.最近限改期限).map(utils.getdays)
    p['逾限日數']= p.groupby('地號').逾限日數.transform(max)
    p['逾限年數']= round(p.逾限日數/365, 2)
    p['距上次裁處經過日數']= p.逾限日數+30
    p = p.rename(columns={
        'UPZone':'分區', 
        'VIOLATION':'違規情形'
        })
    p = p.query("not (地號.str.contains('吳全段256地號') and 違規情形.str.contains('加蓋鐵皮屋2棟及車棚農地未農用'))")
    p = p.query("not (地號.str.contains('吳全段256地號') and 違規情形.str.contains('於該地號土地加蓋鐵皮屋2棟及車棚，農地為農用'))")
    p = p.query("not (地號=='花蓮市福德段9018地號' and 違規情形=='經營餐廳')")
    return p


def approval():
    '容許使用案件'
    return gpd.read_file(land.r / '1100421都計容許使用' /'都計業務.gdb', layer=2) 
    

def 海岸():
    '海岸地區範圍'
    return gpd.read_file(land.r / '1070808海岸地區範圍' / '1070808海岸地區範圍.shp')


def penalty2(audit_date):
    '都計違規裁罰情形一覽表'
    import pandas as pd
    d = env.workdrive / 'gd' / '110縣府單決' / '沿海保護' / '海岸違反都計管制情形'
    f = d / '1100406_105年起違反都市計畫法各年度裁罰情形一覽表(截至110年4月6日).xlsx' 
    p = pd.read_excel(f, 1, header=1)
    p = (p[1:-2]     
            .rename({
                'No':'案號',
                '違反地點':'鄉鎮市',
                'Unnamed: 10':'段號代碼',
                'Unnamed: 11':'地段',
                'Unnamed: 12':'地號',
                'Unnamed: 13':'面積',
                '處分人(或營業場所)名稱':'處分人名稱'
                }, axis=1)
            .fillna(method='ffill')     
            )
    pcode = p.違法編碼.str.split('-', expand=True)
    p = p.assign(
            違規案件種類情形=pcode[0].map(
                {'A':'情節重大案件', 'B':'特定行業案件', 'C':'一般行業或行為案件'}),
            使用分區=pcode[1],
            裁罰次數=pcode[2].astype(int)
            )
    p['處分書日期']=p.處分書日期.map(utils.rocdate)
    #p['繳款期限']=p.繳款期限.map(utils.rocdate)
    p['最近一次處分經過日數']=(audit_date - p.處分書日期).map(utils.getdays)
    p['最近一次處分經過年數']=round(p.最近一次處分經過日數/365, 2)
    p['土地標示'] = (p.鄉鎮市 + p.地段 + p.地號.map(str)).map(land.to_landid)
    #修正異常值
    p.loc[p.處分人名稱=='吳麗珍(即集福行)', '裁罰次數'] = 1
    return p


def pfarm_useasbf():
    '''都市計畫農業區保護區土地，利用為商業及工廠建築使用情形
住宅區營業使用
農業區或保護區-+-工廠使用-+-地籍-+-容許使用-+-海岸範圍
'''
    p = pfarm_district()
    fb = land.fbuse()
    pfb = gpd.overlay(p, fb, how='intersection')
    pfb['土地利用類別'] = pfb.LCODE_C2.map(land.useclass)
    pfb['違規使用面積'] = pfb.area
    return pfb


def 保護區():
    return urbanplan().query('分區.str.contains("保護")')


def 海岸保護區():
    p = 保護區()
    r = 海岸()
    pr = gpd.overlay(p, r, how='intersection')
    return pr


def 保護區工商用():
    p = 保護區()
    fb = land.fbuse()
    pfb = gpd.overlay(p, fb, how='intersection')
    pfb['土地利用類別'] = pfb.LCODE_C2.map(land.useclass)
    pfb['違規使用面積'] = pfb.area
    return pfb 


def 海岸保護區工商用():
    '海岸保護區工商用帶地號'
    p = 保護區工商用()
    r = 海岸()
    pr = gpd.overlay(p, r, how='intersection')
    prl = gpd.overlay(pr, land.shape(),  how='intersection')
    prl['地號'] = prl.段號.map(utils.nvl(land.sname, ''))
    return prl


def 未列管海岸保護區工商用(fulllandno=False):
    pr = 海岸保護區工商用()
    pp = penalty(audit_date=datetime(2021,4,6))
    pa = approval()
    prp = gpd.overlay(pr, pp, how='intersection', keep_geom_type=False)
    prp = prp[['ID', '最近裁處日期']].drop_duplicates()
    pra = gpd.overlay(pr, pa, how='intersection', keep_geom_type=False)#['ID', 'TYPE']
    pra = pra[['ID', 'TYPE']].drop_duplicates()
    pr = pr.merge(prp, how='left', on= 'ID')
    pr = pr.merge(pra, how='left', on= 'ID')
    pr = pr.query('TYPE.isna() and 最近裁處日期.isna()')
    prg = pr.groupby(
                ['都市計畫', '分區', 
                 'ID', '土地利用類別', '違規使用面積' 
                ]
            ).agg({'地號':lambda lnos:'、'.join(lnos)})
    prg = (prg.sort_values(['都市計畫', '分區', '違規使用面積'], ascending=False)
              .reset_index()
          )
    prg.index = prg.index+1
    prg.index.name = '項次'
    def reduce_landno(nos):
        '地號只取前三個'
        nos = nos.split('、')
        return '、'.join(nos[0:3]) + f"等{len(nos)}宗土地。"
    if not fulllandno:
        prg['地號'] = prg.地號.map(reduce_landno)
    return prg.rename(columns={'ID':'國土利用調查編號'}) 


def 農保比例地籍():
    p = 農保區()
    ps = gpd.overlay(p, land.shape(),  how='intersection')
    ps['農保比例'] = ps.area / ps.AA10
    ps = ps[['landid', '農保比例']].drop_duplicates()
    s = land.shape()
    s = s.merge(ps, on='landid')
    return s


def pfarm_useasbf_land():
    '''都市計畫農業區保護區土地，利用為商業及工廠建築使用情形，帶地號'''
    pfb = pfarm_useasbf()
    pfbg = gpd.overlay(pfb, 農保比例地籍(),  how='intersection')
    pfbg['地號'] = pfbg.段號.map(utils.nvl(land.sname, ''))
    pfbg['地籍面積'] = pfbg.area
    pfbg['地籍面積比'] = pfbg.地籍面積/pfbg.AA10
    return pfbg


def 未列管農保區作工商用(fulllandno=False):
    '''都市計畫農業區保護區土地，利用為商業及工廠建築使用情形，
卻無容許使用及裁處紀錄案件。
地號欄位係指示位置使用，並非該地號整片違規使用。
fulllandno係指定是否顯示完整地號。
'''
    pf = pfarm_useasbf_land()
    pp = penalty(audit_date=datetime(2021,4,6))
    pa = approval()
    pfp = gpd.overlay(pf, pp, how='intersection', keep_geom_type=False)
    pfp = pfp[['ID', '最近裁處日期']].drop_duplicates()
    pfa = gpd.overlay(pf, pa, how='intersection', keep_geom_type=False)#['ID', 'TYPE']
    pfa = pfa[['ID', 'TYPE']].drop_duplicates()
    pf = pf.merge(pfp, how='left', on= 'ID')
    pf = pf.merge(pfa, how='left', on= 'ID')
    pf = pf.query('TYPE.isna() and 最近裁處日期.isna() and 農保比例 > 0.1')
    pfg = pf.groupby(
                ['都市計畫', '分區', 
                 'ID', '土地利用類別', '違規使用面積' 
                ]
            ).agg({'地號':lambda lnos:'、'.join(lnos)})
    pfg = (pfg.rename(columns={'ID':'國土利用調查編號'}) 
              .sort_values(['都市計畫', '分區', '違規使用面積'], ascending=False)
              .reset_index()
          )
    pfg.index = pfg.index+1
    pfg.index.name = '項次'
    def reduce_landno(nos):
        '地號只取前三個'
        nos = nos.split('、')
        return '、'.join(nos[0:3]) + f"等{len(nos)}宗土地。"
    if not fulllandno:
        pfg['地號'] = pfg.地號.map(reduce_landno)
    return pfg
