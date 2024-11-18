import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'
    def setUp(self):
        from zhongwen.庫 import 批次載入, 批次寫入, 取資料庫
        from zhongwen.時 import 取日期, 取期間
        import pandas as pd
        import tempfile


        data = [['1101', '合併',pd.NA, '110', 'text']
               ,['1101', '合併',pd.NA, '110', 'text']
               ,['1102', '合併','100', '110', 'text']
               ,['1102', '合併','100', '110', 'text']
               ]
        self.損益表測例 = pd.DataFrame(data
                          ,columns=['股票代號', '財報種類', '毛利', '營利', '其他'])

        self.測庫路徑 = tempfile.TemporaryFile(delete=True).name
        
        for 財報日期 in ['113.3.31', '113.6.30', '113.9.30']:
            批次寫入(self.損益表測例
                    ,取日期(財報日期)
                    ,'財報日期'
                    ,'損益表'
                    ,取資料庫(self.測庫路徑)
                    )

    def test_batch_load(self):
        from zhongwen.時 import 取日期, 取期間
        from zhongwen.庫 import 批次載入, 載入上批資料
        df0 = 批次載入(self.測庫路徑, '損益表', '財報日期', '財報日期')
        self.assertEqual(df0.shape[0], self.損益表測例.shape[0]*3)

        df1 = 批次載入(self.測庫路徑, '損益表', '財報日期', '財報日期'
                      ,最小批號=取日期('113.3.31'))
        self.assertEqual(df1.shape[0], self.損益表測例.shape[0]*3)

        df2 = 批次載入(self.測庫路徑, '損益表', '財報日期', '財報日期'
                      ,最小批號=取日期('113.6.30'))
        self.assertEqual(df2.shape[0], self.損益表測例.shape[0]*2)

        df3 = 批次載入(self.測庫路徑, '損益表', '財報日期', '財報日期'
                      ,最小批號=取日期('113.9.30'))
        self.assertEqual(df3.shape[0], self.損益表測例.shape[0])

        df4 = 載入上批資料(self.測庫路徑, '損益表', '財報日期', '財報日期')
        self.assertEqual(df4.shape[0], self.損益表測例.shape[0])

        print(df4)
        
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
