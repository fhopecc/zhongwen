import unittest

class Test(unittest.TestCase):
    def test_take_periods(self):
        from zhongwen.時 import 取期間
        from pandas import Period, Timestamp
        self.assertEqual(取期間('11310'), Period('202410', 'M'))
        self.assertEqual(取期間('113/10'), Period('202410', 'M'))
        self.assertEqual(取期間('113/1'), Period('202401', 'M'))
        self.assertEqual(取期間('2024-10'), Period('202410', 'M'))
        self.assertEqual(取期間('2020-01'), Period('202001', 'M'))

    def test_period(self):
        from zhongwen.時 import 上月
        import pandas as pd
        self.assertIsInstance(上月(), pd.Period)

    def test_iter_month(self):
        from zhongwen.時 import 自指定月份迄上月
        import pandas as pd
        self.assertEqual(list(自指定月份迄上月('11301')), 
                         list(pd.period_range('2024-01', '2024-10', freq='M'))
                        )

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Test('test_take_period'))  # 指定測試
    unittest.TextTestRunner().run(suite)
