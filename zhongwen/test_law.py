import unittest

class Test(unittest.TestCase):
    def test(self):
        from law import 法條查詢

        self.assertEqual(法條查詢('職業安全衛生法第33條').條文內容.iloc[0], 
                '雇主應負責宣導本法及有關安全衛生之規定，使勞工周知。')

        self.assertEqual(法條查詢('職業安全衛生法33').條文內容.iloc[0], 
                '雇主應負責宣導本法及有關安全衛生之規定，使勞工周知。')

        self.assertEqual(法條查詢('職業安全衛生法[合格]').條號.iloc[0], '8')

if __name__ == '__main__':
    unittest.main()
