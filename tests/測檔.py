from unittest.mock import patch
import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'
    def test(self):
        from 股票分析.股票評價 import 更新財報與自結損益及營收暨股利和行情, cache
        from 股票分析.財報分析 import 取財報彙總表
        from zhongwen.時 import 取日期
        from zhongwen.表 import 顯示
        cache.clear()
        更新財報與自結損益及營收暨股利和行情()
        df = 取財報彙總表()
        df = df.query('財報日期==@取日期("1140630")')
        df = df.query('股票代號=="8271"')
        顯示(df)

 
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Test('test'))  # 指定測試
    unittest.TextTestRunner().run(suite)
