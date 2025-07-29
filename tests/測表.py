import unittest

class Test(unittest.TestCase):
    def setUp(self):
        from pathlib import Path
        self.甲 = (Path(__file__).parent / '表測例甲.txt').read_text(encoding='utf-8')

    def test顯示(self):
        from zhongwen.表 import 顯示
        from zhongwen.文 import 隨機中文 
        import pandas as pd
        import numpy as np
        df = pd.DataFrame()
        df['整數欄位'] = np.random.randint(-5000, 5000, size=10)
        df['實數欄位'] = np.random.uniform(-100, 100, size=df.shape[0])
        df['百分比欄位'] = np.random.uniform(-3, 3, size=df.shape[0])
        df['期間欄位'] = pd.period_range(start='2024Q3', periods=df.shape[0], freq='Q')
        df['日期欄位'] = pd.date_range(start='2024-11-24', periods=df.shape[0], freq='W')
        df['文字欄位'] = df.日期欄位.map(lambda _: 隨機中文(10))
        df['隱藏欄位'] = df.日期欄位.map(lambda _: 隨機中文(10))
        df['全空欄位'] = np.nan

        nan_ratio = 0.2  # 隨機插入2成的空值

        total_values = df.size
        nan_count = int(total_values * nan_ratio)
        nan_indices = (
            np.random.choice(df.index, nan_count, replace=True),
            np.random.choice(df.columns, nan_count, replace=True)
        )
        # 依欄位型別插入 NaN 或 NaT
        for row, col in zip(*nan_indices):
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df.iat[row, df.columns.get_loc(col)] = pd.NaT  # 日期欄位插入 pd.NaT
            else:
                df.iat[row, df.columns.get_loc(col)] = np.nan  # 其他欄位插入 np.nan
        df = df.rename(columns={"日期欄位":"日期\A欄位"})
        顯示(df, 整數欄位=['整數欄位'], 百分比欄位=['百分比欄位'], 隱藏欄位=['隱藏欄位'])
    
    def test_char_width(self):
        from zhongwen.表 import 字寬
        self.assertEqual(字寬('-'), 1)
        self.assertEqual(字寬('字'), 2)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Test('test顯示'))
    unittest.TextTestRunner().run(suite)
