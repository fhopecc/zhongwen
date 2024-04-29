from unittest.mock import patch
from zhongwen.date import 今日
import unittest


class Test(unittest.TestCase):
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
        self.assertEqual(期限, 取日期('113.5.15'))
        self.assertEqual(資訊, f'113年4月22日應公布113年第1季資訊。')


if __name__ == '__main__':
    unittest.main()
