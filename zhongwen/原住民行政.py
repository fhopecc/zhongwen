from diskcache import Cache
from pathlib import Path
import logging

logger = logging.getLogger(Path(__file__).stem)

cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

@cache.memoize('載入原住民部落')
def 載入原住民部落(檔, 縣市='花蓮縣'):
    '''
    一、下載自原住族委員會。
    二、欄位：編號、縣市、鄉鎮市區、村/里、鄰、原住民戶數、原住民人口數、
              核定年度、部落傳統名制、部落名稱、族別
    '''
    import pandas as pd
    tribe = pd.read_excel(檔, sheet_name=縣市, header=1)
    tribe = tribe.iloc[1:]
    tribe.columns = ['編號', '縣市', '鄉鎮市區', '村/里', '鄰'
                 ,'原住民戶數', '原住民人口數', '核定年度'
                 ,'部落傳統名制', '部落名稱', '族別']
    return tribe

@cache.memoize('取營業地點位於原住民部落範圍者')
def 取營業地點位於原住民部落範圍者(營業登記檔, 部落檔): 
    from zhongwen.營業稅 import 載入營業登記檔, cache
    from zhongwen.快取 import 刪除指定名稱快取
    from zhongwen.表 import 顯示
    from pathlib import Path
    import pandas as pd
    import re
    bgm = 載入營業登記檔(營業登記檔).query('營業地址.str.contains("花蓮縣")')
    logger.info(f"營業登記檔規模：{bgm.shape}")
    tribes = 載入原住民部落(部落檔) 
    logger.info(f"原住民部落檔規模：{tribes.shape}")
    tribes['村里'] = tribes['村/里'].str.replace('、', '|')
    bgm_in_tribes = bgm.merge(tribes, how='cross')
    def 營業地址是否包含村里(row):
        address = row['營業地址']
        pattern = row['村里']
        if pd.isna(address) or pd.isna(pattern):
            return False
        return bool(re.search(str(pattern), str(address), re.IGNORECASE))
    conditions = bgm_in_tribes.apply(營業地址是否包含村里, axis=1)
    bgm_in_tribes = bgm_in_tribes[conditions]
    return bgm_in_tribes 

