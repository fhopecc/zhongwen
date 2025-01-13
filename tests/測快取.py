import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'

    # @patch('股票分析.營收分析.營收分析結果快取檔', \
            # Index(tempfile.TemporaryFile(delete=True).name))
    def test(self):
        from diskcache import Index
        from zhongwen.快取 import 增加快取最近時序分析結果
        import tempfile

        快取 = Index(tempfile.TemporaryFile(delete=True).name)

        @增加快取最近時序分析結果(快取, '公司代號', '營收月份')
        def 分析函式測例():
            return pd.DataFrame({"公司代號":["1101", "1102"]
                                 
                                 })



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
