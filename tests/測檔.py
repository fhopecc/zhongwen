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

    def test取文檔位置(self):
        from zhongwen.檔 import 取文檔位置
        s = fr'File "D:\github\vimchinese\plugin\python.vim", line 74'
        d = 取文檔位置(s) 
        self.assertEqual(d['列'], 74)

    def test取檔名補全選項(self):
        from zhongwen.檔 import 取檔名補全選項
        from pathlib import Path
        # d:\github\zhongwen\zhongwen\
        # te
        cs = 取檔名補全選項(Path(__file__).read_text(encoding='utf8'), 27, 38)
        # print([c['abbr'] for c in cs])
        cs = 取檔名補全選項(Path(__file__).read_text(encoding='utf8'), 28
                           ,11, 工作目錄=Path(__file__).parent.parent)
        print(cs)
 
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Test('test取檔名補全選項'))
    unittest.TextTestRunner().run(suite)
