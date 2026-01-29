import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'
    def test(self):
        from zhongwen.開放街圖 import 取地點座標
        from zhongwen.開放街圖 import 取地點最近車程網節點
        from zhongwen.開放街圖 import 取鄉鎮市
        
        print(取鄉鎮市(23.9794533, 121.6106910)) 
        # print(取地點座標('宜蘭縣審計室, 宜蘭縣, 台灣')) 
        # print(取地點最近車程網節點('宜蘭縣審計室, 宜蘭縣, 台灣')) 

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    unittest.main()
