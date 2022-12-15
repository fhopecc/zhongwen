import unittest
from datetime import datetime, date
from zhongwen.date import 取日期
import pandas as pd

class Test(unittest.TestCase):
    def test_parse_date(self):
        self.assertEqual(取日期('2022/6/3 上午 12:00:00'), date(2022,6,3) )
        self.assertEqual(取日期('2020.01.05'), date(2020,1,5))
        self.assertEqual(取日期('20200105'), date(2020,1,5))
        self.assertEqual(取日期('111/07/01 02:22:34'), date(2022,7,1))
        self.assertEqual(取日期('110/12/27'), date(2021,12,27))
        self.assertEqual(取日期('88/02/01'), date(1999,2,1))
        self.assertEqual(取日期('110.11.10'), date(2021,11,10))
        self.assertEqual(取日期('111.9.23'), date(2022,9,23))
        self.assertEqual(取日期('111.4.29+150'), date(2022,9,26))
        self.assertEqual(取日期('民國 99 年 09 月 10 日'), date(2010,9,10))
        self.assertTrue(pd.isnull(取日期('民國 0 年 00 月 00 日')))

        now = datetime.now()
        if datetime(now.year,12,24) > now:
            self.assertEqual(取日期('12.24'), date(now.year-1,12,24))
        else:
            self.assertEqual(取日期('12.24'), date(now.year,12,24))
        if datetime(now.year,1,3) > now:
            self.assertEqual(取日期('1.3'), date(now.year-1,1,3))
        else:
            self.assertEqual(取日期('1.3'), date(now.year,1,3))

        self.assertEqual(取日期(datetime(2022,2,1,23,11)), date(2022,2,1))
        self.assertEqual(取日期(None).date(), datetime.now().date())
        self.assertEqual(取日期('1110527'), date(2022,5,27))

        self.assertEqual(取日期('1110213.000000'), date(2022,2,13))
        self.assertEqual(取日期(940101), date(2005,1,1))
        self.assertEqual(取日期(1110213), date(2022,2,13))
        self.assertEqual(取日期(1110213.0), date(2022,2,13))
  

    def test_date_repr(self):
        from zhongwen.date import 民國日期
        self.assertEqual(民國日期(取日期('110/12/27')), '1101227')
        self.assertEqual(民國日期(取日期('110/1/27'), '%Y年%M月%d日'), '110年1月27日')

        from zhongwen.date import 經過日數
        self.assertEqual(經過日數('108.5.13', '109.12.3'), 570)

        from zhongwen.date import 今日
        self.assertEqual(今日(), 取日期(datetime.now()))

    def test_month(self):
        from zhongwen.date import 月末
        from datetime import date
        self.assertEqual(月末(2022, 10), date(2022, 10, 31))

    def test_quarter(self):
        from zhongwen.date import 季末
        from datetime import date
        self.assertEqual(季末(2022, 2), date(2022, 6, 30))

if __name__ == '__main__':
    unittest.main()
