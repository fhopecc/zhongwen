import unittest
from pathlib import Path
wdir = Path(__file__).parent
class Test(unittest.TestCase):
    def test_number(self):
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
        from zhongwen.number import 中文數字轉數值, 轉數值, 約數, 百分比
        self.assertEqual(中文數字轉數值('一'), 1)
        self.assertEqual(中文數字轉數值('二十五'), 25)
        self.assertEqual(中文數字轉數值('一萬三千二百五十九'), 13259)
        self.assertEqual(中文數字轉數值('十一'), 11)
        self.assertEqual(中文數字轉數值('拾柒'), 17)
        self.assertEqual(中文數字轉數值('十萬'), 100000)
        self.assertEqual(中文數字轉數值('十一萬'), 110000)
        self.assertEqual(轉數值('十一萬'), 110000)
        self.assertEqual(轉數值('一五０'), 150)
        self.assertEqual(轉數值('一五0'), 150)
        self.assertEqual(轉數值('二五'), 25)
        self.assertEqual(轉數值('一００'), 100)
        self.assertEqual(轉數值('- 6.35'), -6.35)
        self.assertEqual(轉數值('一萬三千二百五十九'), 13259)
        self.assertEqual(約數('55,302'), '5萬餘')
        self.assertEqual(百分比('0.8911'), '89.11％')

        from zhongwen.number import 標號, 轉標號
        self.assertEqual(str(標號(1, 1)), '壹、' )
        self.assertEqual(str(標號(1, 4)), '(一)')
        self.assertEqual(str(標號(1, 5)), '1.')
        self.assertEqual(轉標號('壹、'), 標號(1, 1))
        self.assertEqual(轉標號('貳拾、'), 標號(20, 1))
        self.assertEqual(轉標號('一、'), 標號(1, 3))
        self.assertEqual(轉標號('3.'), 標號(3, 5))
        self.assertEqual(轉標號('1.'), 標號(1, 5))

    def test_text(self):
        from zhongwen.text import 轉全型, 轉半型
        self.assertEqual(轉全型('%'), '％')
        self.assertEqual(轉半型('％'), '%')

        from zhongwen.text import 是否為中文字元, 字元切換
        self.assertTrue(是否為中文字元('簡'))
        self.assertTrue(是否為中文字元('简'))
        self.assertFalse(是否為中文字元('a'))
        self.assertFalse(是否為中文字元('μ'))
        self.assertEqual(字元切換('a'), 'A')
        self.assertEqual(字元切換('A'), 'a')
        self.assertEqual(字元切換('B'), 'b')
        self.assertEqual(字元切換('b'), 'B')
        self.assertEqual(字元切換('簡'), '简')
        self.assertEqual(字元切換('简'), '簡')
        self.assertEqual(字元切換('か'), 'カ')
        self.assertEqual(字元切換('カ'), 'か')

        from zhongwen.text import 臚列
        self.assertEqual(臚列(['甲方', '乙方', '丙方']), '甲方、乙方及丙方')
        self.assertEqual(臚列(['單方']), '單方')
        self.assertEqual(臚列('片面'), '片面')

        from zhongwen.text import 倉頡對照表, 倉頡首碼, 首碼搜尋表示式
        m = 倉頡對照表()
        self.assertEqual(m['稜'], 'hdgce')
        # self.assertEqual(m['函'], 'hdgce')
        self.assertEqual(倉頡首碼('稜'), 'h')
        self.assertEqual(倉頡首碼('a'), 'a')
        # self.assertEqual(倉頡首碼('函'), 'u')
        text = '''fa 命令原係向前搜尋字母a，
擴充為向前搜尋字母a及中文倉頡碼首碼為a的中文字，
如【是】倉頡碼為【amyo】。函u
'''
        self.assertTrue('是' in 首碼搜尋表示式('a', text))
        self.assertTrue('倉' in 首碼搜尋表示式('o', text))
        self.assertTrue('令' in 首碼搜尋表示式('o', text))
        self.assertTrue('係' in 首碼搜尋表示式('o', text))

        from zhongwen.text import 翻譯
        self.assertEqual(翻譯('test'), '測試')
        self.assertEqual(翻譯('取り'), '拿')

        # from zhongwen.text import 中文詞界
        # line = '化學法第9條規定'
        # self.assertEqual(中文詞界(10, line), (9,10))

    def test_date(self):
        from zhongwen.date import 取日期
        from datetime import datetime
        self.assertEqual(取日期('2022/6/3 上午 12:00:00'), datetime(2022,6,3,0,0) )
        self.assertEqual(取日期('2020.01.05'), datetime(2020,1,5,0,0))
        self.assertEqual(取日期('110/12/27'), datetime(2021,12,27,0,0))

    def test_law(self):
        from zhongwen.law import 法規名稱字首樹, 法規自動完成建議
        self.assertEqual(法規名稱字首樹().keys('漁港法')[0], '漁港法')
        line = '依據證'
        self.assertEqual(法規自動完成建議(line)[0], '證') # 第一個結果是找出的字首
        self.assertEqual(法規自動完成建議(line)[1], '證券交易法') # 名稱越短的法規越重要

    def test_hllaw(self):
        # from zhongwen.hllaw import 爬取法規
        # self.assertTrue(爬取法規())
        pass

    def test_file(self):
        from zhongwen.file import 抓取
        url = 'https://glrs.hl.gov.tw/glrsout/index.aspx'
        page = 抓取(url)
        # print(page)
        self.assertEqual(page[:5], "<html")

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
