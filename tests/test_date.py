from unittest.mock import patch
from zhongwen.date import 今日
import unittest


class Test(unittest.TestCase):
    def test_parse_date(self):
        from zhongwen.date import 是日期嗎, 取日期
        from pandas import Timestamp, Timedelta
        from datetime import datetime
        import pandas as pd
        self.assertEqual(取日期("'24/01/19"), Timestamp(2024,1,19))
        self.assertEqual(取日期('2022/6/3 上午 12:00:00'), Timestamp(2022,6,3) )
        self.assertEqual(取日期('2020.01.05'), Timestamp(2020,1,5))
        self.assertEqual(取日期('20200105'), Timestamp(2020,1,5))
        self.assertEqual(取日期('111/07/01 02:22:34'), Timestamp(2022,7,1))
        self.assertEqual(取日期('110/12/27'), Timestamp(2021,12,27))
        self.assertEqual(取日期('88/02/01'), Timestamp(1999,2,1))
        self.assertEqual(取日期('110.11.10'), Timestamp(2021,11,10))
        self.assertEqual(取日期('111.9.23'), Timestamp(2022,9,23))
        self.assertEqual(取日期('920526'), Timestamp(2003,5,26))
        self.assertEqual(取日期(11204), Timestamp(2023,4,30))
        self.assertEqual(取日期('民國 99 年 09 月 10 日'), Timestamp(2010,9,10))
        self.assertEqual(取日期('109年 1月'), Timestamp(2020,1,31))
        self.assertEqual(取日期('111.4.29+150'), Timestamp(2022,9,26))

        self.assertTrue(pd.isnull(取日期('民國 0 年 00 月 00 日')))

        now = Timestamp.now()
        self.assertEqual(取日期('12.24'), Timestamp(now.year,12,24))
        self.assertEqual(取日期('0831'), Timestamp(now.year, 8, 31))

        self.assertEqual(取日期(datetime(2022,2,1,23,11)), Timestamp(2022,2,1))
        # self.assertEqual(取日期(None).date(), datetime.now().date())
        self.assertEqual(取日期('1110527'), Timestamp(2022,5,27))

        self.assertEqual(取日期('1110213.000000'), Timestamp(2022,2,13))
        self.assertEqual(取日期(940101), Timestamp(2005,1,1))
        self.assertEqual(取日期(1110213), Timestamp(2022,2,13))
        self.assertEqual(取日期(1110213.0), Timestamp(2022,2,13))
        

        self.assertEqual(取日期('昨日'), Timestamp.today().normalize() - Timedelta(days=1))

        self.assertFalse(是日期嗎(pd.NaT))

    @patch('zhongwen.date.今日')
    def test_date_repr(self, 仿今日):
        from zhongwen.date import 民國日期, 取日期, 民國正式日期
        from datetime import datetime
        import pandas as pd

        self.assertEqual(民國日期(取日期('110/12/27')), '1101227')
        self.assertEqual(民國日期(取日期('110/1/27'), '%Y年%M月%d日'), '110年1月27日')
        self.assertEqual(民國日期(pd.NaT), '')

        from zhongwen.date import 經過日數
        self.assertEqual(經過日數('108.5.13', '109.12.3'), 570)

        self.assertEqual(今日(), 取日期(datetime.now()))

        仿今日.return_value = 取日期('113.4.6')
        self.assertEqual(民國日期(取日期('113.4.6'), '%Y年%M月%D日'), '113年4月6日')
        self.assertEqual(民國正式日期(), '113年4月6日')


    @patch('zhongwen.date.今日')
    def testmonth(self, 仿今日):
        from zhongwen.date import 取日期
        from zhongwen.date import 月底, 上月
        from zhongwen.date import 月起迄
        from pandas import Timestamp
        仿今日.return_value = 取日期('113.1.14')
        
        self.assertEqual(月底(2022, 10), Timestamp(2022, 10, 31))

        self.assertEqual(上月(), Timestamp(2023, 12, 31))

        self.assertEqual(月起迄(2022, 4), [Timestamp(2022, 4, 1), Timestamp(2022, 4, 30)])

    def test_quarter(self):
        from zhongwen.date import 季末, 季初, 季別, 與季末相距月數, 迄每季, 取日期
        from pandas import Timestamp
        
        self.assertEqual(季末(2022, 2), Timestamp(2022, 6, 30))

        self.assertEqual(季別(Timestamp(2023, 1, 2)), (2023, 1))
        self.assertEqual(季別(Timestamp(2024, 7, 26)), (2024, 3))
        self.assertEqual(與季末相距月數(Timestamp(2023, 5, 3)), 1)

        self.assertIsNotNone(季初()) 
        qs = 迄每季(取日期('20190101'))
        self.assertEqual(next(qs), 取日期('20190331'))
        self.assertEqual(next(qs), 取日期('20190630'))
        # self.assertEqual(qs[0], 取日期('1120813'))

    def test_year(self):
        from zhongwen.date import 民國年底, 取日期, 自起算民國年逐年列舉迄今年, 取日期
        self.assertEqual(民國年底(110), 取日期('1101231'))
        self.assertEqual(list(自起算民國年逐年列舉迄今年(110))[:2]
                        ,[民國年底(110), 民國年底(111)]
                        )

if __name__ == '__main__':
    unittest.main()
