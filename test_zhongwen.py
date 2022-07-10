import unittest

class Test(unittest.TestCase):
    def test_number(self):
        from zhongwen.number import 中文數字, 中文数字, 大寫中文數字
        self.assertEqual(中文數字(16), '十六')
        self.assertEqual(中文數字(1600), '一千六')
        self.assertEqual(中文數字(110), '一百一')
        self.assertEqual(中文数字(3.4), '三点四')
        self.assertEqual(中文数字(182.1), '一百八十二点一')
        self.assertEqual(中文数字(10600), '一万零六百')
        self.assertEqual(中文数字(1821010), '一百八十二万一千零一十')
        self.assertEqual(中文数字(111180000), '一亿一千一百一十八万')
        self.assertEqual(大寫中文數字(21), '貳拾壹')
        self.assertEqual(大寫中文數字(23232.00518)
                        ,'貳萬參仟貳佰參拾貳點零零伍壹捌')
        self.assertEqual(中文數字(23232.00518, 兩=True)
                        ,'兩萬三千兩百三十兩點零零五一八')
        from zhongwen.number import 中文數字轉數值, 轉數值, 約數
        self.assertEqual(中文數字轉數值('一'), 1)
        self.assertEqual(中文數字轉數值('二十五'), 25)
        self.assertEqual(中文數字轉數值('一萬三千二百五十九'), 13259)
        self.assertEqual(中文數字轉數值('十一'), 11)
        self.assertEqual(中文數字轉數值('拾柒'), 17)
        self.assertEqual(中文數字轉數值('十萬'), 100000)
        self.assertEqual(中文數字轉數值('十一萬'), 110000)
        self.assertEqual(轉數值('一五０'), 150)
        self.assertEqual(轉數值('一五0'), 150)
        self.assertEqual(轉數值('二五'), 25)
        self.assertEqual(轉數值('一００'), 100)
        self.assertEqual(轉數值('- 6.35'), -6.35)
        self.assertEqual(轉數值('一萬三千二百五十九'), 13259)
        self.assertEqual(約數('55,302'), '5萬餘')
        from zhongwen.number import 標號, 轉標號
        self.assertEqual(str(標號(1, 1)), '壹、' )
        self.assertEqual(str(標號(1, 4)), '(一)')
        self.assertEqual(轉標號('壹、'), 標號(1, 1))
        self.assertEqual(轉標號('一、'), 標號(1, 3))
        self.assertEqual(轉標號('3.'), 標號(3, 5))

      
if __name__ == '__main__':
    unittest.main()
