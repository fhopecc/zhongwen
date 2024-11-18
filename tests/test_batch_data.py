from unittest.mock import patch
from zhongwen.date import 今日
import unittest

class Test(unittest.TestCase):
    def setUp(self):
        from zhongwen.batch_data import 取資料庫
        from zhongwen.date import 取日期
        from pathlib import Path
        import pandas as pd
        data = [['1101', '合併', pd.NA, '110', 'text']
               ,['1102', '合併', '100', '110', 'text']
               ]
        self.損益表集甲 = pd.DataFrame(data
                          ,columns=['股票代號', '財報種類', '毛利', '營利', '其他'])

        data = [['1101', '合併', '100', '110', 'text']
               ,['1102', '合併', '101', '111', 'text']
               ]
        self.損益表集乙 = pd.DataFrame(data
                          ,columns=['股票代號', '財報種類', '毛利', '營利', '其他'])

        data = [['1101', '合併', '100', '110', 'text']
               ,['1102', '合併', '101', '111', 'text']
               ,['1104', '個別', '101', '111', 'text']
               ]
        self.損益表集丙 = pd.DataFrame(data
                          ,columns=['股票代號', '財報種類', '毛利', '營利', '其他'])


        self.測試資料庫路徑 = Path.home() / 'TEMP' / '測試資料庫'

        self.原始測試資料庫路徑 = Path.home() / 'TEMP' / '原始測試資料庫'

    def tearDown(self):
        from zhongwen.batch_data import 取資料庫
        取資料庫(self.測試資料庫路徑).close()
        self.測試資料庫路徑.unlink()
        取資料庫(self.原始測試資料庫路徑).close()
        self.原始測試資料庫路徑.unlink()

    def test_date_converter(self):
        from zhongwen.date import 取日期
        from zhongwen.batch_data import 轉日期字串
        self.assertEqual(轉日期字串(取日期('1979.7.29')), '1979-07-29')

    def test_sqlite_accessor(self):
        '測試讀寫SQLite功能'
        from zhongwen.batch_data import 取資料庫檔路徑, 批次寫入, 批次讀取
        from zhongwen.batch_data import 取資料表內容, 取資料庫, 取原始資料表內容
        from zhongwen.batch_data import 自原始資料庫重建
        from zhongwen.date import 取日期
        from pathlib import Path 

        self.assertEqual(取資料庫檔路徑(取資料庫(self.測試資料庫路徑)), self.測試資料庫路徑)

        # 測試指定欄位
        批次寫入(self.損益表集甲
                ,取日期('113.9.30')
                ,'財報日期'
                ,'損益表'
                ,取資料庫(self.測試資料庫路徑)
                ,['股票代號', '財報種類', '毛利', '營利'])

        df = 取資料表內容(self.測試資料庫路徑, '損益表')
        self.assertEqual(df.shape, (2, 5))
        self.assertEqual(df.iloc[-1].財報日期, ('2024-09-30'))

        df = 取資料表內容(self.原始測試資料庫路徑, '損益表')
        self.assertEqual(df.shape, (2, 6))
        self.assertEqual(df.iloc[-1].財報日期, ('2024-09-30'))
        self.assertEqual(df.iloc[-1].其他, 'text')

        # 測試增加批次資料
        批次寫入(self.損益表集乙
                ,取日期('113.12.31')
                ,'財報日期'
                ,'損益表'
                ,取資料庫(self.測試資料庫路徑)
                ,['股票代號', '財報種類', '毛利', '營利'])

        df = 取資料表內容(self.測試資料庫路徑, '損益表')
        self.assertEqual(df.shape, (4, 5))
        df = 取資料表內容(self.原始測試資料庫路徑, '損益表')
        self.assertEqual(df.shape, (4, 6))
        
        # 測試覆寫批次功能，須刪除舊批次資料後，寫入新批次資料
        批次寫入(self.損益表集丙 
                ,取日期('113.9.30')
                ,'財報日期'
                ,'損益表'
                ,取資料庫(self.測試資料庫路徑)
                ,['股票代號', '財報種類', '毛利', '營利'])
        批次寫入(self.損益表集丙 
                ,取日期('113.9.30')
                ,'財報日期'
                ,'損益表'
                ,取資料庫(self.測試資料庫路徑)
                ,['股票代號', '財報種類', '毛利', '營利'])
        df = 取資料表內容(self.測試資料庫路徑, '損益表')
        df = df.query('財報日期=="2024-09-30"')
        self.assertEqual(df.shape, (3, 5))

        df = 取原始資料表內容(self.測試資料庫路徑, '損益表')
        self.assertEqual(df.shape, (5, 6))
        df = df.query('財報日期=="2024-09-30"')
        self.assertEqual(df.shape, (3, 6))

        df = 批次讀取(取日期('113.9.30')
                     ,'財報日期'
                     ,'損益表'
                     ,取資料庫(self.測試資料庫路徑)
                     )
        self.assertEqual(df.shape, (3, 6))
        self.assertEqual(df.loc[0, '股票代號'], '1101')
        self.assertEqual(df.loc[0, '毛利'], '100')

        批次寫入(self.損益表集甲
                ,取日期('113.6.30')
                ,'財報日期'
                ,'損益表'
                ,取資料庫(self.測試資料庫路徑)
                ,指定欄位=['股票代號', '財報種類', '毛利', '營利'
                          ,'稅前淨利', '淨利'])

        df = 取原始資料表內容(self.測試資料庫路徑, '損益表')
        self.assertEqual(df.shape, (7, 6))

        df = 批次讀取(取日期('113.6.30')
                     ,'財報日期'
                     ,'損益表'
                     ,取資料庫(self.測試資料庫路徑)
                     )
        self.assertEqual(df.loc[0, '股票代號'], '1101')
        self.assertEqual(df.loc[0, '毛利'], None)

        # 測試自原始資料料表重建
        自原始資料庫重建(self.測試資料庫路徑, '損益表', 
                        ['財報日期', '股票代號', '財報種類'
                        ,'其他'])
        df = 取資料表內容(self.測試資料庫路徑, '損益表')
        self.assertEqual(df.shape, (7, 4))
 
    @patch('zhongwen.date.今日')
    def test(self, 仿今日):
        from zhongwen.batch_data import 解析更新期限
        from zhongwen.date import 取日期, 民國年月
        仿今日.return_value = 取日期('113.3.14')

        時期, 期限, 資訊 = 解析更新期限()
        self.assertEqual(時期, 取日期('113.2.29'))
        self.assertEqual(期限, 取日期('113.3.10'))
        self.assertEqual(資訊, f'113年3月14日應公布113年2月資訊。')

        時期, 期限, 資訊 = 解析更新期限('次月底前')
        self.assertEqual(時期, 取日期('113.2.29'))
        self.assertEqual(期限, 取日期('113.3.31'))
        self.assertEqual(資訊, f'113年3月14日應公布113年2月資訊。')

        時期, 期限, 資訊 = 解析更新期限('次年3個月內')
        self.assertEqual(時期, 取日期('112.12.31'))
        self.assertEqual(期限, 取日期('113.3.31'))
        self.assertEqual(資訊, f'113年3月14日應公布112年資訊。')

        仿今日.return_value = 取日期('113.4.6')
        時期, 期限, 資訊 = 解析更新期限('次季45日內')
        self.assertEqual(時期, 取日期('113.3.31'))
        self.assertEqual(期限, 取日期('113.5.15'))
        self.assertEqual(資訊, f'113年4月6日應公布113年第1季資訊。')

        仿今日.return_value = 取日期('113.7.23')
        時期, 期限, 資訊 = 解析更新期限('次季45日內')
        self.assertEqual(時期, 取日期('113.6.30'))
        self.assertEqual(期限, 取日期('113.8.14'))
        self.assertEqual(資訊, f'113年7月23日應公布113年第2季資訊。')

        仿今日.return_value = 取日期('113.7.23')
        時期, 期限, 資訊 = 解析更新期限('次季2個月內')
        self.assertEqual(時期, 取日期('113.6.30'))
        self.assertEqual(期限, 取日期('113.8.31'))
        self.assertEqual(資訊, f'113年7月23日應公布113年第2季資訊。')

        仿今日.return_value = 取日期('113.10.10')
        時期, 期限, 資訊 = 解析更新期限('次季45日內')
        self.assertEqual(時期, 取日期('113.9.30'))
        self.assertEqual(期限, 取日期('113.11.14'))
        self.assertEqual(資訊, f'113年10月10日應公布113年第3季資訊。')

        仿今日.return_value = 取日期('113.4.22')
        時期, 期限, 資訊 = 解析更新期限('財報')
        self.assertEqual(時期, 取日期('113.3.31'))
        self.assertEqual(期限, 取日期('113.5.30'))
        self.assertEqual(資訊, f'113年4月22日應公布113年第1季資訊。')

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
