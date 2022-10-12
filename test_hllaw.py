import unittest

class Test(unittest.TestCase):

    def test_law_query(self):
        from zhongwen.law import LawQuery
        q = LawQuery('職業安全衛生法第33條')
        self.assertEqual(q.法規名稱, '職業安全衛生法')
        self.assertEqual(q.條號, "33") 
        self.assertEqual(q.關鍵字, None) 

        q = LawQuery('職業安全衛生法[合格]')
        self.assertEqual(q.法規名稱, '職業安全衛生法')
        self.assertEqual(q.條號, None) 
        self.assertEqual(q.關鍵字, '合格') 

    def test(self):
        from zhongwen.law import 法條查詢, 法條展開, 法條說明

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

if __name__ == '__main__':
    unittest.main()
