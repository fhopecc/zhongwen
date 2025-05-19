import unittest

class Test(unittest.TestCase):
    def test(self):
        from zhongwen.數 import 取數值
        from zhongwen.表 import show_html
        import pandas as pd
        import numpy as np

        self.assertEqual(取數值('-3,689'), -3689)
        self.assertEqual(取數值('(13,826)'), -13826)
        self.assertEqual(取數值('中間一二三數字'), 123)
        self.assertEqual(取數值('中間一二三數字246'), 123)
        self.assertEqual(取數值('中間一二三數字2.46', 全取=True), [123, 2.46])
        self.assertTrue(pd.isna(取數值('--')))
        df = pd.DataFrame(['中間一二三數字', '中間一二三數字246'])
        df = df.map(取數值)


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
