from unittest.mock import patch
import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'
    def test取年報摘要(self):
        from zhongwen.智 import 取年報摘要
        from 股票分析.財報爬蟲 import 爬取財報電子書
        from zhongwen.pdf import 取文字
        from zhongwen.文 import 刪除中文字間空白, 刪除空行
        from pathlib import Path
        c = 內容 = 刪除中文字間空白(取文字(爬取財報電子書('中再保', 2025, 1)))
        c = [l for l in c.split() if '地址' not in l]
        c = [l for l in c if '電話' not in l]
        c = [l for l in c if 'Direct' not in l]
        c = '\n'.join(c)
        c = 刪除空行(c)
        # 內容 = 內容[300:500])
        # print(內容)
        print(c)
        r = 取年報摘要(c)[:200]
        print(r)

    def test詢問(self):
        from zhongwen.智 import 詢問
        詢問('富林-KY市占率、主要營收組成、主要客戶占比、外銷占比、主要競爭對手及最近財報分析')
        
    def test諮詢谷歌雙子星(self):
        from zhongwen.智 import 諮詢谷歌雙子星
        from clipboard import copy 
        諮詢谷歌雙子星('富林-KY市占率、主要營收組成、主要客戶占比、外銷占比、主要競爭對手及最近財報分析')
 
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    # unittest.main()
    suite = unittest.TestSuite()
    # suite.addTest(Test('test取年報摘要'))
    suite.addTest(Test('test詢問'))
    unittest.TextTestRunner().run(suite)
