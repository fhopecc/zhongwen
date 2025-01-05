from pathlib import Path
import logging
logger = logging.getLogger(Path(__file__).stem)

def 刪除指定名稱快取(快取, 名稱):
    c, n = 快取, 名稱
    keys_to_delete = [key for key in c if isinstance(key, tuple) and key[0] == n]
    for key in keys_to_delete:
        c.delete(key)

def 增加快取最近時序分析結果(快取, 分析項目名稱欄位, 分析項目時戳欄位, 分析時序名稱=''):
    from zhongwen.時 import 取正式民國日期
    from functools import wraps

    def 取可快取最新結果分析時序函數(分析時序函數):
        @wraps(分析時序函數)
        def 可快取最新結果分析時序函數(時間序列, 重新分析=False):
            最久時間序列 = 時間序列.iloc[0]
            最久分析項目時戳 = 最久時間序列[分析項目時戳欄位]
            最近時間序列 = 時間序列.iloc[-1]
            分析項目名稱 = 最近時間序列[分析項目名稱欄位]
            分析項目時戳 = 最近時間序列[分析項目時戳欄位]
            msg  = f'分析{分析項目名稱}自{取正式民國日期(最久分析項目時戳)}'
            msg += f'至{取正式民國日期(分析項目時戳)}期間{分析時序名稱}數據……'
            logger.info(msg)
            if not 重新分析:
                try:
                    快取分析結果 = 快取[分析項目名稱]
                    快取分析項目時戳 = 快取分析結果[分析項目時戳欄位]
                    if 分析項目時戳 <= 快取分析項目時戳:
                        msg  = f'因{分析項目名稱}{分析時序名稱}'
                        msg += f'尚無較{取正式民國日期(快取分析項目時戳)}更新之資料'
                        msg += '，本次無須更新。'
                        logger.info(msg)
                        return 快取分析結果
                except (KeyError, AttributeError):
                    logger.info(f'未曾分析{分析項目名稱}{分析時序名稱}！')
            分析時序結果 = 分析時序函數(時間序列)
            快取[分析時序結果[分析項目名稱欄位]] = 分析時序結果
            return 分析時序結果 
        return 可快取最新結果分析時序函數
    return 取可快取最新結果分析時序函數
