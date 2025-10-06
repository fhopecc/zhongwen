import unittest

class Test(unittest.TestCase):
    
    
    @unittest.skip('')
    def test_law_completion(self):
        from zhongwen.法規 import 法規名稱字首樹, 法規自動完成建議
        self.assertEqual(法規名稱字首樹().keys('漁港法')[0], '漁港法')
        line = '依據證'
        self.assertEqual(法規自動完成建議(line)[0], '證') # 第一個結果是找出的字首
        self.assertEqual(法規自動完成建議(line)[1], '證券交易法') # 名稱越短的法規越重要

    def test測取法規補全選項(self):
        from zhongwen.法規 import 取法規補全選項
        from pathlib import Path
        f = Path(r"g:\我的雲端硬碟\00.114-2花縣府原民處0901-16-1017提出\原民處查核工作紀錄.md")
        cs = 取法規補全選項(f.read_text(encoding='utf-8'), 58, 2)
        print(cs)

if __name__ == '__main__':
    unittest.main()
