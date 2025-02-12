import unittest

class Test(unittest.TestCase):

    def test_get_date(self):
        from zhongwen.時 import 取日期, 今日
        from pandas import Timestamp, Timedelta
        from datetime import datetime, date
        import pandas as pd
        self.assertEqual(取日期('1121231'), Timestamp('2023-12-31'))
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
        self.assertEqual(取日期('1110527'), Timestamp(2022,5,27))

        self.assertEqual(取日期('1110213.000000'), Timestamp(2022,2,13))
        self.assertEqual(取日期(940101), Timestamp(2005,1,1))
        self.assertEqual(取日期(1110213), Timestamp(2022,2,13))
        self.assertEqual(取日期(1110213.0), Timestamp(2022,2,13))
        self.assertEqual(取日期('昨日'), Timestamp.today().normalize() - Timedelta(days=1))
        self.assertEqual(取日期(date(2022,7,29)), Timestamp(2022,7,29))

        self.assertEqual(今日, Timestamp.today().normalize())

    def test取期間(self):
        from zhongwen.時 import 取期間, 取民國期間
        from zhongwen.時 import 上月, 上年度
        from pandas import Period, Timestamp
        self.assertEqual(取期間('112'), Period('2023', 'Y-DEC'))
        self.assertEqual(取期間('2024'), Period('2024', 'Y-DEC'))
        self.assertEqual(取期間('11310'), Period('202410', 'M'))
        self.assertEqual(取期間('113/10'), Period('202410', 'M'))
        self.assertEqual(取期間('113/1'), Period('202401', 'M'))
        self.assertEqual(取期間('2024-10'), Period('202410', 'M'))
        self.assertEqual(取期間('202411'), Period('202411', 'M'))
        self.assertEqual(取期間('2020-01'), Period('202001', 'M'))
        self.assertEqual(取期間('2024Q2'), Period('2024Q2', 'Q-DEC'))
        self.assertEqual(取期間('2024Q2'), Period('2024Q2', 'Q-DEC'))
        self.assertEqual(取期間('99年年度'), Period('2010', 'Y-DEC'))
        self.assertEqual(取期間('112年'), Period('2023', 'Y-DEC'))
        self.assertEqual(取期間('112年年度'), Period('2023', 'Y-DEC'))
        self.assertEqual(取期間('112年第3季'), Period('2023Q3', 'Q-DEC'))
        self.assertEqual(取期間('112年上半年'), Period('2023-1', '6M'))
        self.assertEqual(取期間('112年前半年度'), Period('2023-1', '6M'))
        self.assertEqual(取期間('112年後半年度'), Period('2023-7', '6M'))

        self.assertEqual(取民國期間('112年'), '112年度')
        self.assertEqual(取民國期間('2024Q3'), '113年第3季')
        self.assertEqual(取民國期間('112年上半年'), '112年前半年度')

        self.assertIsInstance(上月, Period)
        self.assertIsInstance(上年度, Period)

    def test_cut_period(self):
        from zhongwen.時 import 全年期別分割, 取期間
        from pandas import period_range
        import pandas as pd
        ps, rps = 全年期別分割(pd.Period('2024-06', freq='6M'))
        print(ps)
        print(rps)
        # print(period_range('2024Q1', periods=3, freq='Q'))

    def test_YOY(self):
        from zhongwen.時 import 去年同期, 取期間
        import pandas as pd
        p = 取期間('2024Q3')
        self.assertEqual(去年同期(p), 取期間('2023Q3'))
        p = pd.Period('2024-06', freq='6M')
        self.assertEqual(去年同期(p), pd.Period('2023-06', freq='6M'))

    def test_iter_yearly(self):
        from zhongwen.時 import 自起始年底按年列舉至本年底
        from zhongwen.時 import 取日期
        import pandas as pd
        ds = 自起始年底按年列舉至本年底(111)
        ys = pd.date_range(取日期('1111231'), 取日期('1131231'), freq='YE')
        # self.assertEqual(ds
                        # ,list(pd.date_range(取日期('1111231'), 取日期('1131231'), freq='YE')))

    def test_roc_date(self):
        from zhongwen.時 import 取民國年月
        self.assertEqual(取民國年月('11311'), '11311')

    def test_workaround(self):
        import pandas as pd
        p = pd.Period('2024Q4', '2Q-DEC')
        # print(p.start_time)
        # print(p.end_time)


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    unittest.main()
    suite = unittest.TestSuite()
    unittest.TextTestRunner().run(suite)
