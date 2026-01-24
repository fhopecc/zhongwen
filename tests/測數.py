import unittest

class Test(unittest.TestCase):
    def test(self):
        from zhongwen.數 import 取數值, 求值
        import pandas as pd

        self.assertEqual(取數值('-3,689'), -3689)
        self.assertEqual(取數值('(13,826)'), -13826)
        self.assertEqual(取數值('中間一二三數字'), 123)
        self.assertEqual(取數值('中間一二三數字246'), 123)
        self.assertEqual(取數值('中間一二三數字2.46', 全取=True), [123, 2.46])
        self.assertTrue(pd.isna(取數值('--')))
        self.assertAlmostEqual(求值('15/0.7%'), 2142.85, places=1)
        self.assertAlmostEqual(求值('15/0.7％'), 2142.85, places=1)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    unittest.main()
