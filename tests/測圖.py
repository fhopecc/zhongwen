from unittest.mock import patch
import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'
    def test(self):
        from zhongwen.圖 import 取圖內表
        from pathlib import Path
        t = 取圖內表(rf'g:\我的雲端硬碟\02.115-1縣府114年度單決抽查115.4.13-28\02.農業處頻危物種保育專家諮詢楊華美\展演動物許可清冊\202602130519120001.jpg')
        print(t)
        # 安裝依賴套件及程式()
        # 圖檔 = Path(__file__).parent / '賜岳飛敕.jpg'
        # 圖內文 = r = 取圖內文(圖檔)
        # print(圖內文)
        # self.assertEqual(圖內文[:4], "乾隆尚題")
 
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    unittest.main()
    # suite = unittest.TestSuite()
    # suite.addTest(Test('test'))  # 指定測試
    # unittest.TextTestRunner().run(suite)
