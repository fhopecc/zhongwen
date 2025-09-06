from pathlib import Path
import logging
logger = logging.getLogger(Path(__file__).stem)

def 快取至記憶體(func):
    '確保原始函數描述資料數據複製至裝飾器'
    import functools
    @functools.wraps(func)
    @functools.cache
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def 刪除指定名稱快取(快取, 名稱):
    c, n = 快取, 名稱
    keys_to_delete = [key for key in c if isinstance(key, tuple) and key[0] == n]
    for key in keys_to_delete:
        c.delete(key)

停止快取=False
def 增加快取時序分析結果(取時序函數, 名稱欄位, 時間欄位, 快取檔案, 分析時序名稱=''):
    '''
    一、依指定取時序函數、名稱欄位、時間欄位、快取檔案增加分析函數快取時序分析結果功能。
    二、取時序函數可傳回指定名稱之時序資料。
    三、名稱即為快取鍵，通常為股票名稱或公司名稱。
    四、時間欄位可為多個，其中一個時戳落後即予更新。
    五、如指定名稱之時序資料為空，則引發數據不足錯誤。
    '''
    from zhongwen.表 import 數據不足
    from zhongwen.時 import 取正式民國日期
    from functools import wraps
    import pandas as pd
    class 使用者指定重新分析(Exception):pass
    class 快取結果已過時(Exception):pass
    class 取時序出現例外(Exception):pass
    def 取可快取最新結果分析時序函數(分析時序函數):
        @wraps(分析時序函數)
        def 可快取最新結果分析時序函數(名稱, 重新分析=False, 重新分析項目=None):
            '''重新分析項目係指定要重分析之項目名稱串列，如指定一組股票名稱必需更新。'''
            from collections.abc import Iterable 
            import pandas as pd
            時序名稱 = 取時序函數.__name__.replace("取", "")
            logger.info(f'分析{名稱}之{時序名稱}數據')
            try:
                時間序列 = 取時序函數(名稱)
                最早時間序列 = 時間序列.iloc[0]
                最早分析項目時戳 = 最早時間序列[時間欄位]
                最近時間序列 = 時間序列.iloc[-1]
                最新資料時間 = 最近時間序列[時間欄位]
                msg  = f'分析自{取正式民國日期(最早分析項目時戳)}'
                msg += f'至{取正式民國日期(最新資料時間)}期間'
                msg += f'{時序名稱}之{名稱}數據'
                logger.info(msg)
                if 重新分析項目:
                    if isinstance(重新分析項目, str) or not isinstance(重新分析項目, Iterable):
                        重新分析項目 = [重新分析項目]
                    if 名稱 in 重新分析項目:
                        重新分析 = True
                if 重新分析:
                    del 快取檔案[名稱]
                    raise 使用者指定重新分析(f'使用者指定重新分析{時序名稱}之{名稱}數據！')
                if 停止快取:
                    del 快取檔案[名稱]
                    raise 使用者指定重新分析(f'使用者指定停止快取{時序名稱}之{名稱}數據！')
                快取分析結果 = 快取檔案[名稱]
                快取資料時間 = 快取分析結果[時間欄位]
                if 快取資料時間 < 最新資料時間:
                    msg = f'快取{時間欄位}為{取正式民國日期(快取資料時間)}'
                    msg += f'較最新資料{時間欄位}{取正式民國日期(最新資料時間)}落後，應予更新'
                    raise 快取結果已過時(msg)
                msg  = f'因{時序名稱}之{名稱}快取{時間欄位}為{取正式民國日期(快取資料時間)}'
                msg += '較新，本次無須更新。'
                logger.info(msg)
                return 快取分析結果
            except (快取結果已過時, 使用者指定重新分析, 數據不足, KeyError, IndexError) as e:
                logger.info(
                    f'取{名稱}之{時序名稱}，發生{str(e).replace("！", "例外")}，爰重新分析！')
            分析時序結果 = 分析時序函數(名稱)
            快取檔案[名稱] = 分析時序結果
            return 分析時序結果 
        return 可快取最新結果分析時序函數
    return 取可快取最新結果分析時序函數
