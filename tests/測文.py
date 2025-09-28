from unittest.mock import patch
import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'
    def test轉樣式表字串(self):
        from zhongwen.text import 轉樣式表字串
        t = "1abcd\n2abcd"
        tb = 轉樣式表字串(t)
        self.assertEqual(tb.replace('\\n', '&#10;'), 'ab')

    def test(self):
        from zhongwen.文 import 臚列標題
        text = '''### 標題甲
### 標題乙

內容乙

### 標題丙
'''
        self.assertEqual(臚列標題(text, 級別='3'), '(一)標題甲；(二)標題乙；(三)標題丙')

    def test取倉頡候選字(self):
        from zhongwen.文 import 倉頡檢字, 取臺灣字頻序號
        from zhongwen.文 import cache
        from marisa_trie import Trie
        cache.clear()
        f = 取臺灣字頻序號() 
        self.assertEqual(f['的'], 1)
        self.assertEqual(取臺灣字頻序號('的'), 1)
        self.assertEqual(取臺灣字頻序號('3'), 5732)
        t : Trie = 倉頡檢字()
        candidates = sorted([c[-1] + c[:-1] for c in t.keys('女戈木')]
                           ,key = lambda s:(len(s), s))
        print(candidates)
        candidates = sorted([c[-1] + c[:-1] for c in t.keys('女戈木')]
                           ,key = lambda s:(len(s),取臺灣字頻序號(s[0]),s))
        print(candidates)
        candidates = 倉頡檢字('女戈木')
        print(candidates)
        candidates = 倉頡檢字('vid')
        print(candidates)

        self.assertNotEqual(倉頡檢字('jj')[0], '十十')


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Test('test取倉頡候選字'))
    # suite.addTest(Test('test轉樣式表字串'))
    unittest.TextTestRunner().run(suite)
