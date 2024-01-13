import unittest

class Test(unittest.TestCase):
    def test(self):
        from zhongwen.date import 今日, 民國日期, 民國年月, 上月, 月末
        from zhongwen.batch_data import 解析更新期限
        時期, 期限, 資訊 = 解析更新期限()
        today = 今日()
        self.assertEqual(期限, today.replace(day=10))
        self.assertEqual(資訊, f'{民國日期()}應公布{民國年月(上月())}資訊。')

        時期, 期限, 資訊 = 解析更新期限('次月底前')
        self.assertEqual(期限, today.replace(day=31))
        self.assertEqual(資訊, f'{民國日期()}應公布{民國年月(上月())}資訊。')

if __name__ == '__main__':
    unittest.main()
