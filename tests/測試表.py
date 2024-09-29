import unittest

class Test(unittest.TestCase):
    def setUp(self):
        from pathlib import Path
        self.甲 = (Path(__file__).parent / '表測例甲.txt').read_text(encoding='utf-8')

    def test(self):
        from zhongwen.表 import 取表
        字串 = self.甲
        df = 取表(字串)
        print(df)
        self.assertEqual(df.columns[0], '科目')
        
    def test_parse_block(self):
        from zhongwen.表 import 取字塊
        s = '期間                 (月)                      (季)           (最近四季累計)'
        bs = 取字塊(s)
        self.assertEqual(bs[0], ('期間', 0, 4))
        self.assertEqual(bs[1], ('(月)', 21, 25))
        self.assertEqual(bs[-1], ('(最近四季累計)', 62, 76))
        self.assertEqual(len(bs), 4)

    def test_parse_columns(self):
        from zhongwen.表 import 取欄
        分隔線 = '----------  ----------  ----------  ------------  ----------  --------------' 
        cs = 取欄(分隔線) 
        self.assertEqual(len(cs), 6)
        self.assertEqual(cs[0], ('----------', 0, 10))
        self.assertEqual(cs[1], ('----------', 12, 22))

    def test_char_width(self):
        from zhongwen.表 import 字寬
        self.assertEqual(字寬('-'), 1)
        self.assertEqual(字寬('字'), 2)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Test('test_parse_block'))  # 指定測試
    unittest.TextTestRunner().run(suite)
