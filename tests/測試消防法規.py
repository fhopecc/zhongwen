import unittest
class Test(unittest.TestCase):
    def test(self):
        from zhongwen.消防法規 import 抓取法規
        url = 'https://law.nfa.gov.tw/mobile/law.aspx?LSID=FL005010'
        law = 抓取法規(url)
        from clipboard import copy
        copy(law)
        print(law)

if __name__ == '__main__':
    unittest.main()
