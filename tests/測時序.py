import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'
    def test(self):
        from twse_crawler.營收分析 import 預測次年底營收
        from zhongwen.時序 import 繪各年月份數據週期對比圖
        股票 = '泰銘'
        # 繪各年月份數據週期對比圖(預測次年底營收(股票).預估每月值.預估每月營收)
        from zhongwen.表 import 表示
        df = 預測次年底營收(股票).預估每月值
        表示(df, 顯示索引=True, 顯示筆數=1000)
        
 
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    unittest.main()
