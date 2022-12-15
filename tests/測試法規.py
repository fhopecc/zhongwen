import unittest

class Test(unittest.TestCase):

    def test_query_by_content(self):
        from zhongwen.中央法規 import 法規條文, cache
        # cache.clear()
        # pass
        # df = 法規條文()
        # df = df.query('法規名稱.str.contains("各類場所消防安全設備設置標準")')
        # df = df.query('條文內容.str.contains("，及")')
        # df = df.query('法規名稱=="消防勤務實施要點"')
        # from fhopecc.pandas_tools import show_html
        # show_html(df)

    def test_law_query(self):
        from zhongwen.法規 import LawQuery
        q = LawQuery('職業安全衛生法第33條')
        self.assertEqual(q.法規名稱, '職業安全衛生法')
        self.assertEqual(q.條號, "33") 
        self.assertEqual(q.關鍵字, None) 

        q = LawQuery('職業安全衛生法[合格]')
        self.assertEqual(q.法規名稱, '職業安全衛生法')
        self.assertEqual(q.條號, None) 
        self.assertEqual(q.關鍵字, '合格') 

    def test(self):
        from zhongwen.法規 import 法條查詢, 法條展開, 法條說明

        self.assertEqual(法條查詢('職業安全衛生法第33條').條文內容.iloc[0], 
                '雇主應負責宣導本法及有關安全衛生之規定，使勞工周知。')

        self.assertEqual(法條查詢('職業安全衛生法33').條文內容.iloc[0], 
                '雇主應負責宣導本法及有關安全衛生之規定，使勞工周知。')

        self.assertEqual(法條查詢('職業安全衛生法[合格]').條號.iloc[0], '8')

        self.assertEqual(法條展開('職業安全衛生法33'), 
                '職業安全衛生法第33條規定：「雇主應負責宣導本法及有關安全衛生之規定，使勞工周知。」'
                )
        self.assertEqual(法條說明('職業安全衛生法[合格]')[:10], '職業安全衛生法第8條')

        self.assertEqual(法條展開('危險性機械及設備安全檢查規則3')[:27], 
                '危險性機械及設備安全檢查規則第3條規定：「本規則適用於'
                )
        self.assertEqual(法條展開('直轄市縣市消防機關救護車輛裝備人力配置標準5')[:27], 
                '直轄市縣市消防機關救護車輛裝備人力配置標準第5條規定：'
                )
        
    def test_law_completion(self):
        from zhongwen.法規 import 法規名稱字首樹, 法規自動完成建議
        self.assertEqual(法規名稱字首樹().keys('漁港法')[0], '漁港法')
        line = '依據證'
        self.assertEqual(法規自動完成建議(line)[0], '證') # 第一個結果是找出的字首
        self.assertEqual(法規自動完成建議(line)[1], '證券交易法') # 名稱越短的法規越重要

if __name__ == '__main__':
    unittest.main()
