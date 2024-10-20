import unittest

class Test(unittest.TestCase):

    def test_markdown(self):
        from zhongwen.office_document import 標題階層編號轉中文編號 
        from subprocess import check_output
        t = '6	擬議處理意見'
        o = '陸、擬議處理意見'
        self.assertEqual(標題階層編號轉中文編號(t), o)

        t = '1.2.1 三級管控核有缺失'
        o = '一、三級管控核有缺失'
        self.assertEqual(標題階層編號轉中文編號(t), o)

        out = check_output('py -m zhongwen.office_document --level_number_to_chinese_number "1.2.1 三級管控核有缺失"', shell=True)
        self.assertEqual(out.decode('cp950').rstrip(), '一、三級管控核有缺失')

    def test(self):
        from zhongwen.office_document import parse
        doc = '''工作底稿
花蓮漁港觀光漁市公共設施新建工程大事記

105.4.21.該規劃於外泊地南側腹地作為上架場用地，惟土地上既有鐵皮屋搭建而成之假日魚市，規劃於106年底拆遷至新設觀光魚市，公告花蓮漁港區域及漁港計畫。

106.5.9.行政院花東地區發展推動小組第14次委員會議決議，花東第二期(105-108 年)綜合發展實施方案滾動檢討案，核列花蓮縣漁港機能改善與多元化利用建置計畫為C類計畫，總經費6,011萬元。

花蓮漁港漁業公共設施新建工程大事記
107.3.27.決標予富太營造股份有限公司。
108.5.13.該府辦理本案驗收結算結果，逾期18天，逾期違約金19萬餘元，結算金額1,071萬餘元。
'''
        t = parse(doc)
        print(t)
        print(t.pretty())
        self.assertEqual(t.children[1].children[0].children[0], '花蓮漁港觀光漁市公共設施新建工程大事記')
        # self.assertEqual(t.children[1].children[1].children[0], '花蓮漁港漁業公共設施新建工程大事記')

        doc = '''肆、調查重點：
一、花蓮縣政府辦理漁港機能改善與多元化利用建置計畫之規劃設計與經費核定及修正情形。

二、預算編列與執行檢核情形。

三、中央補助計畫機關核定之後續規劃及工程執行情形。

四、漁港設施竣工後之管理使用效益。
'''
        # t = parse(doc)
        # print(t.pretty())
        # print(t.children[0])
        # self.assertEqual(t.children[0].children[0].data.value, 'h1')
        # self.assertEqual(t.children[1].children[0].data.value, 'h3')

if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Test('test_markdown'))  # 指定要執行的測試方法
    unittest.TextTestRunner().run(suite)
