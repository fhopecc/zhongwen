import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'

    # @patch('股票分析.營收分析.營收分析結果快取檔', \
            # Index(tempfile.TemporaryFile(delete=True).name))
    def test(self):
        from 股票分析.行情分析 import 預測報酬率
        from 股票分析.自結損益 import 分析月稅前損益
        from zhongwen.表 import 數據不足, 顯示
        分析月稅前損益('遠東銀', 重新分析=True)
 
        self.assertRaises(數據不足, 預測報酬率,'FB台50')
        預測報酬率('崑鼎')
        self.assertRaises(數據不足, 預測報酬率,'二信股票')

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
