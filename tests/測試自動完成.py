import unittest

class Test(unittest.TestCase):
    def test(self):
        from zhongwen.自動完成 import 同字首詞
        行 = '是以，依據美國十年'
        字典 = ['公債',  '十年房地產', '美國十年期公債', '美國十年經濟'] 
        結果 = [{'abbr': '美國十年期公債', 'kind': 'K', 'word': '期公債'}
               ,{'abbr': '美國十年經濟', 'kind': 'K', 'word': '經濟'}
               ,{'abbr': '十年房地產', 'kind': 'K', 'word': '房地產'}]
        ['美國十年期公債', '美國十年經濟', '十年房地產'] 
        self.assertEqual(同字首詞(行, 字典), 結果)


if __name__ == '__main__':
    unittest.main()
