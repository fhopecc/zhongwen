import unittest
from pathlib import Path

class Test(unittest.TestCase):
    # @unittest.skip('skip')
    def test_company_name(self):
        from zhongwen.text import 公司正名
        n0 = '中國信託商業銀行(股)公司(下稱中信銀行)'
        n1 = '中國信託商業銀行股份有限公司'
        self.assertEqual(公司正名(n0), n1)

    # @unittest.skip('skip')
    def test_moedict(self):
        from zhongwen.text import 查萌典, 萌典尚無定義之字詞
        
        # import logging
        # logging.getLogger().setLevel(logging.DEBUG)

        self.assertEqual(查萌典('查'), ['ㄔㄚˊ：考察、檢查。翻閱、檢尋。大筏，水中的浮木。', 
                                        'ㄓㄚ：姓。如五代時南唐有查文徽。我。同「咱」(一)。'])

        with self.assertRaises(萌典尚無定義之字詞):
            查萌典('word')
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
        self.assertEqual(查萌典('彊')[0], '「強」的異體字。')

    # @unittest.skip('隔離測試')
    def test_text(self):
        from zhongwen.text import 轉全型, 轉半型
        self.assertEqual(轉全型('%'), '％')
        self.assertEqual(轉半型('％'), '%')

        from zhongwen.text import 是否為字元
        self.assertTrue(是否為字元('簡'))
        self.assertTrue(是否為字元('a'))
        self.assertTrue(是否為字元('μ'))
        self.assertFalse(是否為字元('.'))
        self.assertFalse(是否為字元('，'))

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
        self.assertEqual(字元切換('行'), '行')

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
        # self.assertEqual(翻譯('取り'), '拿')

    def test_text_segmentation(self):
        from zhongwen.text import 分詞

        字串 = '''美國十年期公債殖利率即你現在買進且持有至到期日每年的年化報酬率，
其係依據債券現價、持有至到期日期間之利息及到期還本現金流所計算之內部報酬率，
由於美國係目前世界上經濟最發達的國家，
其所發行公債倒債風險極低，該公債被大部分投資人視為無風險投資，
是以，美國十年期公債殖利率通常視作無風險利率。
'''
        self.assertTrue('債券' in 分詞(字串))

        # self.assertEqual(中文詞界(10, line), (9,10))

    def test_to_css_string(self):
        from zhongwen.text import 轉樣式表字串
        s = '[長空]：上年度股利估計相對誤差達20.40%；[短多]：毛利率達54.27%，營利率達23.48%'
        r = r'[\009577\007a7a]\00ff1a\004e0a\005e74\005ea6\0080a1\005229\004f30\008a08\0076f8\005c0d\008aa4\005dee\00905420.40%\00ff1b[\0077ed\00591a]\00ff1a\006bdb\005229\007387\00905454.27%\00ff0c\0071df\005229\007387\00905423.48%'
        self.assertEqual(轉樣式表字串(s), r)

    @unittest.skip('尚未完成')
    def test_surround(self):
        from zhongwen.text import 取最近環繞符號, 刪除環繞符號, 插入環繞符號
        from zhongwen.text import 取引用內容, 引用
        s = 'There is a (parentheses) and the nearest (parenthese).'
        self.assertEqual(取引用內容(s), None)
        self.assertEqual(取引用內容(s, 10), None)
        self.assertEqual(取引用內容(s, 11), 引用('(parentheses)', 11, 23))
        self.assertEqual(取引用內容(s, 12), 引用('(parentheses)', 11, 23))
        self.assertEqual(取引用內容(s, 22), 引用('(parentheses)', 11, 23))
        self.assertEqual(取引用內容(s, 23), 引用('(parentheses)', 11, 23))
        self.assertEqual(取引用內容(s, 24), None)
        self.assertEqual(取引用內容(s, 40), None)
        self.assertEqual(取引用內容(s, 41), 引用('(parenthese)', 41, 52))
        self.assertEqual(取引用內容(s, 42), 引用('(parenthese)', 41, 52))
        self.assertEqual(取引用內容(s, 51), 引用('(parenthese)', 41, 52))
        self.assertEqual(取引用內容(s, 52), 引用('(parenthese)', 41, 52))

        s = 'delete (the [neareast surround]).'
        self.assertEqual(取引用內容(s, 31), 引用('(the [neareast surround])', 7, 31))
        self.assertEqual(取引用內容(s, 7), 引用('(the [neareast surround])', 7, 31))
        self.assertEqual(取引用內容(s, 8), 引用('(the [neareast surround])', 7, 31))
        self.assertEqual(取引用內容(s, 11), 引用('(the [neareast surround])', 7, 31))
        self.assertEqual(取引用內容(s, 12), 引用('[neareast surround]', 12, 30))
        self.assertEqual(取引用內容(s, 30), 引用('[neareast surround]', 12, 30))

        s = '這列一個「引號」，再列一個『雙引號』。'
        self.assertEqual(取引用內容(s, 4), 引用('「引號」', 4, 7))
        self.assertEqual(取引用內容(s, 12), None)
        self.assertEqual(取引用內容(s, 13), 引用('『雙引號』', 13, 17))
        self.assertEqual(取引用內容(s, 15), 引用('『雙引號』', 13, 17))
        self.assertEqual(取引用內容(s, 17), 引用('『雙引號』', 13, 17))
        self.assertEqual(取引用內容(s, 18), None)

        s = "刪除「游標處「巢狀引號」的功能」。"
        # self.assertEqual(取引用內容(s, 5), 引用('「游標處「巢狀引號」的功能」', 6, 11))
        # self.assertEqual(取引用內容(s, 6), 引用('「巢狀引號」', 6, 11))
        # self.assertEqual(取引用內容(s, 7), 引用('「巢狀引號」', 6, 11))
        # self.assertEqual(取引用內容(s, 11), 引用('「巢狀引號」', 6, 11))

        # r = "刪除「游標處巢狀引號的功能」。"
        # self.assertEqual(刪除環繞符號(s, "「", 7), r)
        # self.assertEqual(刪除環繞符號(s, "「", 8), r)
        # self.assertEqual(刪除環繞符號(s, "「", 12), r)
        s = "刪除'游標處單引號'的功能"
        r = "刪除游標處單引號的功能"
        # self.assertEqual(刪除環繞符號(s, "'", 3), r)
        # self.assertEqual(刪除環繞符號(s, "'", 4), r)
        # self.assertEqual(刪除環繞符號(s, "'", 9), r)
        # self.assertEqual(刪除環繞符號(s, "'", 10), r)
        s = "'日期欄位'"
        # self.assertEqual(取最近環繞符號(s), "''")
        s = "'日期欄位'"
        # self.assertEqual(刪除環繞符號(s, "'"), "日期欄位")
        t = 'enclose this (cursorword) in parentheses.'
        # self.assertEqual(插入環繞符號('enclose this cursorword in parentheses.', 列=14), t)
      # 測試
    @unittest.skip('尚未完成')
    def test_find_matching_parentheses(self):
        from zhongwen.text import 查找引號對
        expression = "a * (b + c) - {d / [e + f]}"
        matches = 查找引號對(expression)
        print(matches)

if __name__ == '__main__':
    unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Test('test_find_matching_parentheses'))  # 指定要執行的測試方法
    unittest.TextTestRunner().run(suite)
