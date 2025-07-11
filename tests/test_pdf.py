from unittest.mock import patch
import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'

    def test(self):
        from 股票分析.財報爬蟲 import 爬取財報電子書
        from zhongwen.pdf import 取文字
        from pathlib import Path
        # pdf = Path(__file__).parent / '數字2024年報.pdf' 
        pdf = 爬取財報電子書('中再保', 2025, 1) 
        text = 取文字(str(pdf))
        print(text)
        self.assertEqual(text, '')
 
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Test('test'))  # 指定測試
    unittest.TextTestRunner().run(suite)
