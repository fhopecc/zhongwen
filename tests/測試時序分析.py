import unittest

class Test(unittest.TestCase):

    def test_series(self):
        from zhongwen.時序分析 import 最近缺失序列, 序列缺項補零
        import pandas as pd
        s = pd.Series([0.9, 0.9, 1.3, 1.8, 1.4], index=[106, 108, 109, 110, 112])
        年數, 前幾年 = 最近缺失序列(s)
        self.assertEqual((年數, 前幾年), (111, 1))
        完整序列 = 序列缺項補零(s)
        self.assertEqual(完整序列.index.to_list(), [106, 107, 108, 109, 110, 111, 112])
        self.assertEqual(完整序列.to_list(), [0.9, 0.0, 0.9, 1.3, 1.8, 0.0, 1.4])
        s = pd.Series([0.9, 0.9, 1.3, 1.8, 1.4], index=[106, 107, 108, 109, 110])
        年數, 前幾年 = 最近缺失序列(s)
        self.assertEqual((年數, 前幾年), (None, 0))

    def test(self):
        from zhongwen.時序分析 import 最近連續非零正數次數, 連續消長次數
        import pandas as pd
        s = pd.Series([0, 1, 2, 0])
        self.assertEqual(最近連續非零正數次數(s), 0)
        s = [1, 1, 2, 0, 1]
        self.assertEqual(最近連續非零正數次數(s), 1)
        s = [1, 1, 2, 0, 1, 1, 2]
        self.assertEqual(最近連續非零正數次數(s), 3)
        s = pd.Series([1, 1, 2, 0, 1, 1, 2])
        self.assertEqual(最近連續非零正數次數(s), 3)

        s = pd.Series([1, 2, 3, 2, 1, 2, 3])
        self.assertEqual(連續消長次數(s), 2)

    def test_autocorr(self):
        # import pandas as pd
        # import matplotlib.pyplot as plt
        # s = pd.Series([1, 2, 3, 5, 7, 1, 2, 3, 5, 7, 1, 2, 3, 5, 7])
        # print(s.autocorr(2))
        # ax = plt.plot(s.autocorr())
        # s.plot()
        # plt.show()

        import pandas as pd
        import matplotlib.pyplot as plt
        import numpy as np

        # 生成一個時間序列
        # df = pd.DataFrame({
            # "t": range(1, 1001),
            # "y": 0.5 * np.sin(2 * np.pi * t / 24) + 0.5
        # })

        # 計算自相關係數
        # acf = df["y"].autocorr(lag=None)

        # 繪製自相關係數圖像
        # plt.plot(acf)
        # plt.show()

if __name__ == '__main__':
    unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Test('test_series'))  # 指定測試
    unittest.TextTestRunner().run(suite)
