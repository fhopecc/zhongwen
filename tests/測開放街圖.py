import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'
    def test_geocode(self):
        from zhongwen.開放街圖 import 取地點座標
        print(取地點座標('宜蘭縣審計室, 宜蘭縣, 台灣')) 

    def test_driving_nx_node(self):
        from zhongwen.開放街圖 import 取最近車程路網節點
        print(取最近車程路網節點('宜蘭縣審計室, 宜蘭縣, 台灣')) 

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
