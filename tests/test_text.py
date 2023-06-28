import unittest
from pathlib import Path

class Test(unittest.TestCase):
    def test_moedict(self):
        from zhongwen.text import 查萌典, 萌典尚無定義之字詞
        
        # import logging
        # logging.getLogger().setLevel(logging.DEBUG)

        self.assertEqual(查萌典('查'), ['ㄔㄚˊ：考察、檢查。翻閱、檢尋。大筏，水中的浮木。', 
                                        'ㄓㄚ：姓。如五代時南唐有查文徽。我。同「咱」(一)。'])

        with self.assertRaises(萌典尚無定義之字詞):
            查萌典('word')

    # @unittest.skip('隔離測試')
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
        self.assertEqual(字元切換('['), '「')
        self.assertEqual(字元切換(']'), '」')

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

        # diskcache
        # functools.cache 0.025, 0.025, 0.025
        # 模組變數 0.023, 0.036, 0.023, 0.023
        # 顯然使用模組變數緩存對照表效率更高
        # import cProfile
        # with cProfile.Profile() as pr:
            # 首碼搜尋表示式('a', text*1000)
        # from sys import stdout
        # pr.print_stats()
        # breakpoint()

        from zhongwen.text import 翻譯
        self.assertEqual(翻譯('test'), '測試')
        self.assertEqual(翻譯('取り'), '拿')
        from zhongwen.text import 中文詞界

        line = '''該局為處理廚餘並轉化土壤改良劑再利用，建置花蓮縣環保科技園區廚餘高效能處理廠，分別於花蓮縣環保科技園區研究廠房10(下稱A廠)及研究廠房20(下稱B廠)各設置一套廚餘高效能處理系統，每套處理系統均設置二組醱酵槽，並辦理「花蓮縣環保科技園區廚餘高效能處理廠代操作管理廠商專業服務計畫」勞務採購，將該廠委外操作管理。該計畫110年採購預算金額為282萬元，於110年9月9日以公開評選方式決標予循創有限公司(下稱循創)，決標金額為275萬元，履約期間為110年11月1日至110年12月31日止；111年採購預算金額為1,691萬5,000元，亦決標予循創，決標金額同預算金額，履約期間為111年1月1日至111年12月31日止。嗣該局為避免機具設備零件損壞故障及後續定期及不定期歲修等問題，影響廚餘處理去化，於111年6月27日變更本案契約，於招標規範(四)其他應配合事項新增設備維護及維修作業，規定廠區發現設備有故障、異常或其他問題應於五日內派技術人員處理並完成維修，如無法短時間修復完成，請公司函報該局修復期程，並提替代因應措施，修復完成請公司函報該局備查。次查循創於同年8月2日函報該局111年4月B廠一槽軸心斷裂，估計同年8月31日前維修完成。嗣該局因該公司至同年7月19日始於Line群組告知上開故障情形，，(111年6月28日至111年7月18日)，未依約立即函報上述故障情形，日數為21日。'''

        # self.assertEqual(中文詞界(10, line), (9,10))

      
if __name__ == '__main__':
    unittest.main()
