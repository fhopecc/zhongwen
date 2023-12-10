import unittest

class Test(unittest.TestCase):
    def test(self):
        from zhongwen.時序分析 import 最近連續非零正數次數
        import pandas as pd
        s = [0, 1, 2, 0]
        self.assertEqual(最近連續非零正數次數(s), 0)
        s = [1, 1, 2, 0, 1]
        self.assertEqual(最近連續非零正數次數(s), 1)
        s = [1, 1, 2, 0, 1, 1, 2]
        self.assertEqual(最近連續非零正數次數(s), 3)
        s = pd.Series([1, 1, 2, 0, 1, 1, 2])
        self.assertEqual(最近連續非零正數次數(s), 3)

if __name__ == '__main__':
    unittest.main()
