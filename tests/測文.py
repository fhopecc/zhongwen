from unittest.mock import patch
import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'
    def test_geturl(self):
        from zhongwen.文 import geturl
        orgmode_url = 'https://news.ltn.com.tw/news/Hualien/breakingnews/5256071][abcd]]'
        self.assertEqual('https://news.ltn.com.tw/news/Hualien/breakingnews/5256071', 
                         geturl(orgmode_url))

    def test取路徑(self):
        from zhongwen.文 import 取路徑
        orgmode_path = r'[[g:\我的雲端硬碟\文件\用品說明書\汽車CCrossHV2025手冊.pdf][說明書]'
        self.assertEqual(r'g:\我的雲端硬碟\文件\用品說明書\汽車CCrossHV2025手冊.pdf', 
                         取路徑(orgmode_path)[0].group())
        self.assertEqual(2,取路徑(orgmode_path)[0].start())
        self.assertEqual(41,取路徑(orgmode_path)[0].end())
        pathes = r'c:\abc\def d:\def.txt e:\abcd\d1\c.txt' 
        self.assertEqual(r'e:\abcd\d1\c.txt', 取路徑(pathes, 23))
        self.assertEqual('', 取路徑(pathes, 40))

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
        # 前方段落，取詞
        opts = 取詞補全選項(f.read_text(encoding='utf-8'), 147, 26)
        print(opts)
        # opts = 取詞補全選項(f.read_text(encoding='utf-8'), 146, 14)
        # print(opts)

    def test取強調詞補全選項(self):
        from zhongwen.文 import 取強調詞字首樹, 取強調詞補全選項
        from pathlib import Path
        # 「強調甲」
        # 【強調乙】
        # [強調丙]
        # '強調丁'
        # "強調戊"
        # ['強調己']
        # 強
        f = Path(__file__)
        words = 取強調詞字首樹(f.read_text(encoding='utf-8'))
        print(words.keys('強調'))
        opts = 取強調詞補全選項(f.read_text(encoding='utf-8'), 157, 11)
        print(opts)

    def test_re_pattern_convesion(self):
        from zhongwen.文 import python_re_to_vim_magic
        from zhongwen.文 import 取分隔詞模式
        print(取分隔詞模式())
        print(python_re_to_vim_magic(取分隔詞模式()))
        self.assertEqual(取分隔詞模式('vim'), python_re_to_vim_magic(取分隔詞模式()))

    def test意見轉通知(self):
        from zhongwen.文 import 審核意見轉通知
        o = r'花蓮縣政府函為花蓮縣動植物防疫所擬銷毀103年度會計帳表暨憑證一案，謹擬具處理意見如說明三，簽請核示。'
        i = r'貴府函為花蓮縣動植物防疫所擬銷毀103年度會計帳表暨憑證一案，其中除有關債權債務憑證及因案（如監察、審計、檢察、調查、廉政或稅務等機關調查中、法院審理中，或採購履約爭議處理中）應續予保存者外，其餘本室同意辦理，惟請注意檔案法及相關法令之規定，請查照。'
        self.assertEqual(審核意見轉通知(o), i)


        o = '花蓮縣政府函為所屬花蓮縣環境保護局經管縣有聲頻發生器電子鞭炮機(財產編號：310071004-001801)1個，因114年9月23日馬太鞍溪堰塞湖洪災遺失，擬予報損一案，謹擬具處理意見如說明二，簽請核示。'
        i = '貴府函為所屬花蓮縣環境保護局經管縣有聲頻發生器電子鞭炮機(財產編號：310071004-001801)1個，因114年9月23日馬太鞍溪堰塞湖洪災遺失，擬予報損一案，既經貴府查明符合規定同意辦理，本室已予備查，請查照。'
        self.assertEqual(審核意見轉通知(o), i)

        o = '花蓮縣政府聲復本室抽查該府(原住民行政處)114年度1至8月財務收支審核通知一案，謹擬具處理意見如說明二，簽請鑒核。'
        i = '貴府聲復本室抽查貴府(原住民行政處)114年度1至8月財務收支審核通知一案，核復如說明二，請查照。'
        self.assertEqual(審核意見轉通知(o), i)

        o = '依該府114年11月28日府環空字第1140217596號函辦理。'
        i = '復貴府114年11月28日府環空字第1140217596號函。'
        self.assertEqual(審核意見轉通知(o), i)

        o = '本案原通知計有建議事項2項(5小項)及注意事項1項(4小項)，茲據該府本次聲復擬具處理意見如次：'
        i = '核復事項：'
        self.assertEqual(審核意見轉通知(o), i)

        o = '原通知建議事項一(一)，有關長期缺乏文物維護專業人力，致迭有策展後未能整飭入庫保存，或典藏櫃溫濕度監控警示設定值逾控制範圍等情事，允宜向原發中心提出專業人力需求，以維護原住民族文化資產1項，據復：目前缺乏文物維護與保存專業之人力，致策展作業完成後，文物入庫整飭、編目管理及典藏環境監控等工作無法即時辦理，實有必要檢視並補強相關專業人力等情，擬復請將檢視並補強專業人力結果函復本室。'
        i = '原通知建議事項一(一)，有關長期缺乏文物維護專業人力，致迭有策展後未能整飭入庫保存，或典藏櫃溫濕度監控警示設定值逾控制範圍等情事，允宜向原發中心提出專業人力需求，以維護原住民族文化資產1項，承復：目前缺乏文物維護與保存專業之人力，致策展作業完成後，文物入庫整飭、編目管理及典藏環境監控等工作無法即時辦理，實有必要檢視並補強相關專業人力等情，請將檢視並補強專業人力結果函復本室。'
        self.assertEqual(審核意見轉通知(o), i)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Test('test取路徑'))
    unittest.TextTestRunner().run(suite)
