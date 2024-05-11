import unittest
from pathlib import Path
wdir = Path(__file__).parent
class Test(unittest.TestCase):

    def test_轉數值(self):
        from zhongwen.number import 中文數字轉數值, 轉數值, 約數, 百分比
        self.assertEqual(轉數值('十一萬'), 110000)
        self.assertEqual(轉數值('一五０'), 150)
        self.assertEqual(轉數值('一五0'), 150)
        self.assertEqual(轉數值('二五'), 25)
        self.assertEqual(轉數值('一００'), 100)
        self.assertEqual(轉數值('- 6.35'), -6.35)
        self.assertEqual(轉數值('35,636.71'), 35636.71)
        self.assertEqual(轉數值('一萬三千二百五十九'), 13259)
        self.assertEqual(轉數值('參佰玖拾柒萬肆仟壹拾伍'), 3974015)
        self.assertEqual(轉數值('5,000'), 5000)
        self.assertEqual(轉數值('8.1%'), 0.081)
        self.assertEqual(轉數值('-8.1%'), -0.081)
        self.assertEqual(轉數值('１２３'), 123)
        self.assertEqual(轉數值('3年'), 3)
        self.assertEqual(約數('55,302'), '5萬餘')
        self.assertEqual(約數('5,302'), '5,302')
        self.assertEqual(百分比('0.8911'), '89.11％')

        self.assertEqual(中文數字轉數值('一'), 1)
        self.assertEqual(中文數字轉數值('二十五'), 25)
        self.assertEqual(中文數字轉數值('一萬三千二百五十九'), 13259)
        self.assertEqual(中文數字轉數值('十一'), 11)
        self.assertEqual(中文數字轉數值('拾柒'), 17)
        self.assertEqual(中文數字轉數值('十萬'), 100000)
        self.assertEqual(中文數字轉數值('十一萬'), 110000)

    def test_中文數字(self):
        from zhongwen.number import 中文數字, 中文数字, 大寫中文數字
        self.assertEqual(中文數字(16), '十六')
        self.assertEqual(中文數字(110), '一百一')
        self.assertEqual(中文數字(1600), '一千六')
        self.assertEqual(中文数字(3.4), '三点四')
        self.assertEqual(中文数字(10600), '一万零六百')
        self.assertEqual(中文数字(1821010), '一百八十二万一千零一十')
        self.assertEqual(中文数字(111180000), '一亿一千一百一十八万')
        self.assertEqual(大寫中文數字(21), '貳拾壹')
        self.assertEqual(大寫中文數字(23232.00518)
                        ,'貳萬參仟貳佰參拾貳點零零伍壹捌')
        self.assertEqual(中文數字(23232.00518, 兩=True)
                        ,'兩萬三千兩百三十兩點零零五一八')

        from zhongwen.number import 標號, 轉標號
        self.assertEqual(str(標號(1, 1)), '壹、' )
        self.assertEqual(str(標號(1, 4)), '(一)')
        self.assertEqual(str(標號(1, 5)), '1.')
        self.assertEqual(轉標號('壹、'), 標號(1, 1))
        self.assertEqual(轉標號('貳拾、'), 標號(20, 1))
        self.assertEqual(轉標號('一、'), 標號(1, 3))
        self.assertEqual(轉標號('3.'), 標號(3, 5))
        self.assertEqual(轉標號('1.'), 標號(1, 5))

        from zhongwen.number import 全型數字
        self.assertEqual(全型數字('123'), '１２３')

    def test_counter_sec_ones(self):
        from zhongwen.number import 連續正負次數
        a = [2, 3, -0.1, 7, 8, 9, -0.3, 2, 3, 4, 5, 5]
        self.assertEqual(連續正負次數(a), 2)
        a = [-2, -3, -0.1, 7, 8, 9, -0.3, 2, 3, 4, 5, 5]
        self.assertEqual(連續正負次數(a), -3)
        a = [-2, -3, -0.1, -7]
        self.assertEqual(連續正負次數(a), -4)
        a = [2, 3, 0.1, 7]
        self.assertEqual(連續正負次數(a), 4)

        from zhongwen.number import 連續正數
        a = [2, 3, -0.1, 7, 8, 9, -0.3, 2, 3, 4, 5, 5]
        self.assertEqual(連續正數(a), 5)
        a = [2]
        self.assertEqual(連續正數(a), 1)
        a = [2, 3, -0.1, 7, 8, 9, -0.3, 3, 4, 5, 5]
        self.assertEqual(連續正數(a), 4)

        # from zhongwen.number import 最近連續正負次數
        # a = [2]
        # self.assertEqual(最近連續正負次數(a), 1)
        # a = [-1]
        # self.assertEqual(最近連續正負次數(a), -1)
        # a = [2, 7]
        # self.assertEqual(最近連續正負次數(a), 2)
        # a = [2, -7]
        # self.assertEqual(最近連續正負次數(a), -1)
        # a = [float('nan'), 3, 0.1, 7]
        # self.assertEqual(最近連續正負次數(a), 3)

    def test_nan_handler(self):
        from zhongwen.number import 除零例外則回覆非數常數
        div_zero_func = lambda r: r/0
        div_zero_return_nan_func = 除零例外則回覆非數常數(div_zero_func)
        import numpy as np
        self.assertTrue(np.isnan(div_zero_return_nan_func(1)))

    def test_文字表達(self):
        from zhongwen.number import 增減百分比, 增減
        self.assertEqual(增減百分比(0.11), '增加11.00%')
        self.assertEqual(增減百分比(-0.01), '減少1.00%')
        self.assertEqual(增減(3), '增加3')
        self.assertEqual(增減(-2), '減少2')

    def test_script(self):
        from subprocess import check_output
        out = check_output("py -m zhongwen.number --increment 貳拾、"
                          ,shell=True)
        self.assertEqual(out.decode('cp950').rstrip(), '貳拾壹、')

        out = check_output("py -m zhongwen.number --increment 1."
                          ,shell=True)
        self.assertEqual(out.decode('cp950').rstrip(), '2.')
      
if __name__ == '__main__':
    unittest.main()
