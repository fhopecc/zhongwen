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
        from zhongwen.文 import 倉頡檢字, 取臺灣字頻序號, 首碼搜尋表示式
        from zhongwen.文 import cache
        from marisa_trie import Trie
        # cache.clear()
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

        text = '''fa 命令原係向前搜尋字母a，
擴充為向前搜尋字母a及中文倉頡碼首碼為a的中文字，
如【是】倉頡碼為【amyo】。函u
'''
        self.assertTrue('是' in 首碼搜尋表示式('a', text))
        self.assertTrue('倉' in 首碼搜尋表示式('o', text))
        self.assertTrue('令' in 首碼搜尋表示式('o', text))
        self.assertTrue('係' in 首碼搜尋表示式('o', text))

    def test查萌典(self):
        from zhongwen.文 import 查萌典, 萌典尚無定義之字詞
        import logging

        self.assertEqual(查萌典('查'), ['ㄔㄚˊ：考察、檢查。翻閱、檢尋。大筏，水中的浮木。', 
                                        'ㄓㄚ：姓。如五代時南唐有查文徽。我。同「咱」(一)。'])

        with self.assertRaises(萌典尚無定義之字詞):
            查萌典('word')
        logging.getLogger().setLevel(logging.DEBUG)
        self.assertEqual(查萌典('彊')[0], '「強」的異體字。')

    def test取文內簡稱字首樹(self):
        from zhongwen.文 import 取文內簡稱字首樹, 取簡稱補全選項
        from pathlib import Path
        f = Path(r"g:\我的雲端硬碟\00.114-2花縣府原民處0901-16-1017提出\原民處查核工作紀錄.md")
        abbrs = 取文內簡稱字首樹(f.read_text(encoding='utf-8'))
        print(abbrs.keys('2'))
        opts = 取簡稱補全選項(f.read_text(encoding='utf-8'), 315, 7)
        print(opts)

    def test取英文單字補全選項(self):
        from zhongwen.文 import 取英文單字補全選項, 取英文單字首樹
        from pathlib import Path
        f = Path(__file__)
        words = 取英文單字首樹(f.read_text(encoding='utf-8'))
        print(words.keys('test'))
        # pr
        # 
        # vim9
        opts = 取英文單字補全選項(f.read_text(encoding='utf-8'), 82, 12)
        print(opts)
        opts = 取英文單字補全選項(f.read_text(encoding='utf-8'), 83, 10)
        print(opts)
        opts = 取英文單字補全選項(f.read_text(encoding='utf-8'), 84, 14)
        print(opts)

    def test取最近詞首(self):
        from zhongwen.文 import 取最近詞首
        print('abcd')
        w = 取最近詞首('set compe', 8)
        print(w)
        self.assertEqual(w, comp)

    def test取名詞字首樹(self):
        from zhongwen.文 import 取名詞字首樹
        from pathlib import Path
        f = r'g:\我的雲端硬碟\00.114-2花縣府原民處0901-16-1017(20)提出\慢食產業計畫查核工作紀錄.md'
        f = Path(f)
        nouns = 取名詞字首樹(f.read_text(encoding='utf-8'))
        nouns = [n.encode('cp950', errors='replace').decode('cp950') for n in nouns]
        print(nouns)

    def test取停用詞(self):
        from zhongwen.文 import 取停用詞
        import re
        df = 取停用詞()
        pat = df.iloc[:, 0].values
        pat = '|'.join(pat)
        pat = rf"(?:[\uff00-\uffef\u3000-\u303f\s,.?;:/\\\"'|~!@#$%^&*()\[\]{{}}\_=\+\-]|{pat})+"
        print(pat)
        s = '''#### 徵選原住民部落範圍內商家給予獎勵金補助提升慢食產業，惟食農相關商家參與徵選比例偏低，且僅於慢食組織說明徵件方式，允宜協調相關機關組織協助加強宣導，以提升商家參與比補助成效
        '''
        s1 = re.findall(pat, s)
        print(s1)
        s2 = [w for w in re.split(pat, s) if len(w)>0]
        print(s2)

    def test取英文單字補全選項(self):
        from zhongwen.文 import 取英文單字補全選項, 取英文單字首樹
        from pathlib import Path
        f = Path(__file__)
        words = 取英文單字首樹(f.read_text(encoding='utf-8'))
        print(words.keys('test'))
        # pr
        # 
        # vim9
        opts = 取英文單字補全選項(f.read_text(encoding='utf-8'), 82, 12)
        print(opts)
        opts = 取英文單字補全選項(f.read_text(encoding='utf-8'), 83, 10)
        print(opts)
        opts = 取英文單字補全選項(f.read_text(encoding='utf-8'), 84, 14)
        print(opts)

    def test取詞補全選項(self):
        from zhongwen.文 import 取詞字首樹, 取詞補全選項
        from pathlib import Path
        f = Path(__file__)
        words = 取詞字首樹(f.read_text(encoding='utf-8'))
        print(words.keys('test'))
        print(words.keys('取詞'))
        print(words.keys("'"))
        opts = 取詞補全選項(f.read_text(encoding='utf-8'), 147, 12)
        print(opts)
        opts = 取詞補全選項(f.read_text(encoding='utf-8'), 146, 14)
        print(opts)

    def test取強調詞補全選項(self):
        from zhongwen.文 import 取強調詞字首樹, 取強調詞補全選項
        from pathlib import Path
        # 「強調甲」
        # 【強調乙】
        # [強調丙]
        # 強
        f = Path(__file__)
        words = 取強調詞字首樹(f.read_text(encoding='utf-8'))
        print(words.keys('強調甲'))
        opts = 取強調詞補全選項(f.read_text(encoding='utf-8'), 157, 11)
        print(opts)

    def test_re_pattern_convesion(self):
        from zhongwen.文 import python_re_to_vim_magic
        from zhongwen.文 import 取分隔詞模式
        print(取分隔詞模式())
        print(python_re_to_vim_magic(取分隔詞模式()))
        self.assertEqual(取分隔詞模式('vim'), python_re_to_vim_magic(取分隔詞模式()))

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Test('test取詞補全選項'))
    unittest.TextTestRunner().run(suite)
