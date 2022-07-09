import unittest

class Test(unittest.TestCase):
    
    def test(self):
        from chinese import 中文數字, 中文数字

        self.assertEqual(中文数字(3.4), '三点四')
        self.assertEqual(中文数字(182.1), '一百八十二点一')
        self.assertEqual(中文數字(16), '十六')
        self.assertEqual(中文數字(1600), '一千六')
        self.assertEqual(中文數字(110), '一百一')
        self.assertEqual(中文数字(10600), '一万零六百')
        self.assertEqual(中文数字(1821010), '一百八十二万一千零一十')
        self.assertEqual(中文数字(111180000), '一亿一千一百一十八万')
        self.assertEqual(中文數字(23232.00518, 大寫=True)
                        ,'貳萬參仟貳佰參拾貳點零零伍壹捌')
        self.assertEqual(中文數字(23232.00518, 兩=True)
                        ,'兩萬三千兩百三十兩點零零五一八')
       
if __name__ == '__main__':
    unittest.main()
