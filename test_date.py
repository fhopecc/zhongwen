import unittest
from datetime import datetime
from zhongwen.date import 取日期

class Test(unittest.TestCase):
    def test_parse_date(self):
        self.assertEqual(取日期('2022/6/3 上午 12:00:00'), datetime(2022,6,3,0,0) )
        self.assertEqual(取日期('2020.01.05'), datetime(2020,1,5,0,0))
        self.assertEqual(取日期('20200105'), datetime(2020,1,5,0,0))
        self.assertEqual(取日期('111/07/01 02:22:34'), datetime(2022,7,1,0,0))
        self.assertEqual(取日期('110/12/27'), datetime(2021,12,27,0,0))
        self.assertEqual(取日期('110.11.10'), datetime(2021,11,10,0,0))
        self.assertEqual(取日期('111.9.23'), datetime(2022,9,23,0,0))

        self.assertEqual(取日期('111.4.29+150'), datetime(2022,9,26,0,0))

        now = datetime.now()
        if datetime(now.year,12,24) > now:
            self.assertEqual(取日期('12.24'), datetime(now.year-1,12,24))
        else:
            self.assertEqual(取日期('12.24'), datetime(now.year,12,24))
        if datetime(now.year,1,3) > now:
            self.assertEqual(取日期('1.3'), datetime(now.year-1,1,3))
        else:
            self.assertEqual(取日期('1.3'), datetime(now.year,1,3))

        self.assertEqual(取日期(datetime(2022,2,1,23,11)), datetime(2022,2,1))
        self.assertEqual(取日期(None).date(), datetime.now().date())

        self.assertEqual(取日期('1110527'), datetime(2022,5,27))

    def test_date_repr(self):
        from zhongwen.date import 民國日期
        self.assertEqual(民國日期(取日期('110/12/27')), '1101227')
        self.assertEqual(民國日期(取日期('110/1/27'), '%Y年%M月%d日'), '110年1月27日')

        from zhongwen.date import 經過日數
        self.assertEqual(經過日數('108.5.13', '109.12.3'), 570)

        from zhongwen.date import 今日
        self.assertEqual(今日(), 取日期(datetime.now()))

if __name__ == '__main__':
    unittest.main()
