import unittest
from zhongwen.date import 取日期
import pandas as pd

class Test(unittest.TestCase):
    def test_parse_date(self):
        from zhongwen.date import 是日期嗎
        from datetime import datetime, date, timedelta
        self.assertEqual(取日期('2022/6/3 上午 12:00:00'), date(2022,6,3) )
        self.assertEqual(取日期('2020.01.05'), date(2020,1,5))
        self.assertEqual(取日期('20200105'), date(2020,1,5))
        self.assertEqual(取日期('111/07/01 02:22:34'), date(2022,7,1))
        self.assertEqual(取日期('110/12/27'), date(2021,12,27))
        self.assertEqual(取日期('88/02/01'), date(1999,2,1))
        self.assertEqual(取日期('110.11.10'), date(2021,11,10))
        self.assertEqual(取日期('111.9.23'), date(2022,9,23))
        self.assertEqual(取日期('920526'), date(2003,5,26))
        self.assertEqual(取日期(11204), date(2023,4,30))
        self.assertEqual(取日期('民國 99 年 09 月 10 日'), date(2010,9,10))
        self.assertEqual(取日期('109年 1月'), date(2020,1,31))
        self.assertEqual(取日期('111.4.29+150'), date(2022,9,26))

        self.assertTrue(pd.isnull(取日期('民國 0 年 00 月 00 日')))

        now = datetime.now()
        self.assertEqual(取日期('12.24'), date(now.year,12,24))
        self.assertEqual(取日期('0831'), date(now.year, 8, 31))

        self.assertEqual(取日期(datetime(2022,2,1,23,11)), date(2022,2,1))
        # self.assertEqual(取日期(None).date(), datetime.now().date())
        self.assertEqual(取日期('1110527'), date(2022,5,27))

        self.assertEqual(取日期('1110213.000000'), date(2022,2,13))
        self.assertEqual(取日期(940101), date(2005,1,1))
        self.assertEqual(取日期(1110213), date(2022,2,13))
        self.assertEqual(取日期(1110213.0), date(2022,2,13))
        
        self.assertEqual(取日期('昨日'), datetime.now().date() - timedelta(days=1))

        self.assertFalse(是日期嗎(pd.NaT))

    def test_date_repr(self):
        from zhongwen.date import 民國日期
        from datetime import datetime
        import pandas as pd

        self.assertEqual(民國日期(取日期('110/12/27')), '1101227')
        self.assertEqual(民國日期(取日期('110/1/27'), '%Y年%M月%d日'), '110年1月27日')
        self.assertEqual(民國日期(pd.NaT), '')

        from zhongwen.date import 經過日數
        self.assertEqual(經過日數('108.5.13', '109.12.3'), 570)

        from zhongwen.date import 今日
        self.assertEqual(今日(), 取日期(datetime.now()))

    def test_month(self):
        from zhongwen.date import 月末
        from datetime import date
        self.assertEqual(月末(2022, 10), date(2022, 10, 31))

        from zhongwen.date import 月起迄
        self.assertEqual(月起迄(2022, 4), [date(2022, 4, 1), date(2022, 4, 30)])

    def test_quarter(self):
        from zhongwen.date import 季末, 季初, 季別, 與季末相距月數, 迄每季, 取日期
        from datetime import date
        self.assertEqual(季末(2022, 2), date(2022, 6, 30))

        self.assertEqual(季別(date(2023, 1, 2)), (2023, 1))

        self.assertEqual(與季末相距月數(date(2023, 5, 3)), 1)

        self.assertIsNotNone(季初()) 
        qs = 迄每季(取日期('20190101'))
        self.assertEqual(next(qs), 取日期('20190331'))
        self.assertEqual(next(qs), 取日期('20190630'))
        # self.assertEqual(qs[0], 取日期('1120813'))

    def test_year(self):
        from zhongwen.date import 民國年底, 取日期, 自起算年迄逐民國年列舉
        self.assertEqual(民國年底(110), 取日期('1101231'))
        self.assertEqual(list(自起算年迄逐民國年列舉(110)),[110, 111, 112])

if __name__ == '__main__':
    unittest.main()
