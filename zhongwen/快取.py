from pathlib import Path
import logging
logger = logging.getLogger(Path(__file__).stem)

def 刪除指定名稱快取(快取, 名稱):
    c, n = 快取, 名稱
    keys_to_delete = [key for key in c if isinstance(key, tuple) and key[0] == n]
    for key in keys_to_delete:
        c.delete(key)

def 增加快取最近時序分析結果(快取, 分析項目名稱欄位, 分析項目依賴時戳欄位, 分析時序名稱=''):
    '分析項目依賴時戳欄位可為多個'
    from zhongwen.時 import 取正式民國日期
    from collections.abc import Iterable 
    from functools import wraps

    if isinstance(分析項目依賴時戳欄位, str) or not isinstance(分析項目依賴時戳欄位, Iterable):
        分析項目依賴時戳欄位 = [分析項目依賴時戳欄位]

    主要依賴時戳欄位 = 分析項目依賴時戳欄位[0]
    class 快取程序非預期錯誤(Exception):pass
    class 快取結果已過時(Exception):pass
    def 取可快取最新結果分析時序函數(分析時序函數):
        @wraps(分析時序函數)
        def 可快取最新結果分析時序函數(時間序列, 重新分析=False):
            最久時間序列 = 時間序列.iloc[0]
            最久分析項目時戳 = 最久時間序列[主要依賴時戳欄位]
            最近時間序列 = 時間序列.iloc[-1]
            分析項目名稱 = 最近時間序列[分析項目名稱欄位]
            分析項目時戳 = 最近時間序列[主要依賴時戳欄位]
            msg  = f'分析{分析項目名稱}自{取正式民國日期(最久分析項目時戳)}'
            msg += f'至{取正式民國日期(分析項目時戳)}期間{分析時序名稱}數據……'
            logger.info(msg)
            if not 重新分析:
                try:
                    快取分析結果 = 快取[分析項目名稱]

                    for 依賴時戳欄位 in 分析項目依賴時戳欄位:
                        快取分析項目時戳 = 快取分析結果[依賴時戳欄位]
                        分析項目時戳 = 最近時間序列[依賴時戳欄位] 
                        try:
                            if 分析項目時戳 > 快取分析項目時戳:
                                msg = f'快取{依賴時戳欄位}為{取正式民國日期(快取分析項目時戳)}'
                                msg += f'較現行{取正式民國日期(分析項目時戳)}落後，應予更新'
                                logger.info(msg)
                                raise 快取結果已過時(msg)
                        except ValueError:
                            print(分析項目時戳)
                            print(快取分析項目時戳)
                            from zhongwen.表 import 顯示
                            顯示(快取分析結果, 顯示索引=True)
                            breakpoint()

                    msg  = f'因{分析項目名稱}{分析時序名稱}'
                    msg += f'尚無較{取正式民國日期(快取分析項目時戳)}更新之資料'
                    msg += '，本次無須更新。'
                    logger.info(msg)
                    return 快取分析結果
                except KeyError as e:
                    不存在依賴時戳欄位 = e.args[0]
                    if 不存在依賴時戳欄位 in 分析項目依賴時戳欄位:
                        logger.info(f'快取不存在{不存在依賴時戳欄位}時戳，爰重新分析')
                    else:
                        raise 快取程序非預期錯誤(str(e))
                # except (KeyError, AttributeError):
                    # logger.info(f'未曾分析{分析項目名稱}{分析時序名稱}！')
                except 快取結果已過時 as e:
                    logger.info(str(e))
            else:
                logger.info('使用者指定重新分析！')
            分析時序結果 = 分析時序函數(時間序列)
            快取[分析時序結果[分析項目名稱欄位]] = 分析時序結果
            return 分析時序結果 
        return 可快取最新結果分析時序函數
    return 取可快取最新結果分析時序函數
