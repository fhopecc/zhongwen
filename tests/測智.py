from unittest.mock import patch
import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'
    def test取年報摘要(self):
        from zhongwen.智 import 取年報摘要
        from zhongwen.pdf import 取文字
        from pathlib import Path
        pdf = Path(__file__).parent.parent / r'tests\數字2024年報.pdf'
        內容 = 取文字(str(pdf))
        r = 取年報摘要(內容)

    def test取詢問(self):
        from zhongwen.智 import 詢問
        r = 詢問('匯率的繁體中文表達方式')
        print(r)
 
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Test('test取詢問'))
    unittest.TextTestRunner().run(suite)
