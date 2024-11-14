import unittest

class Test(unittest.TestCase):
    def test_to_landmark(self):
        from zhongwen.地號 import 取土地標示
        self.assertEqual(取土地標示('GA07006400710000'), '07006400710000')

    def test_download_codetable(self):
        from zhongwen.地號 import 下載段碼表, 下載鄉鎮市區代碼表, cache
        from zhongwen.表 import show_html
        from zhongwen.快取 import 刪除指定名稱快取
        df = 下載段碼表() 
        # 刪除指定名稱快取(cache, '下載鄉鎮市區代碼表')
        # df = 下載鄉鎮市區代碼表() 
        # df = df.query('縣市代碼=="G"')
        show_html(df, 顯示筆數=2000)

    def test_get_landnos(self):
        from zhongwen.地號 import 取地號
        地號清單 = 取地號(
"鳳林鎮長橋段404-3地號、中心埔段1180地號、綜開段16地號等及及周遭廠址共89筆"
        )
        self.assertEqual(地號清單, 
                [
                '鳳林鎮長橋段404-3', 
                '鳳林鎮中心埔段1180', 
                '鳳林鎮綜開段16' 
                ])
        地號清單 = 取地號('花蓮市美港段5-2、2及5-10')
        self.assertEqual(地號清單, 
                [
                '花蓮市美港段5-2', '花蓮市美港段2', '花蓮市美港段5-10' 
                ])
        地號清單 = 取地號(
            "鳳林鎮兆豐段224地號等780筆土地與榮開段304地號等14筆"
            )
        self.assertEqual(地號清單, 
                [
                '鳳林鎮兆豐段224', '鳳林鎮榮開段304'
                ])
        地號清單 = 取地號("玉里鎮三義段4、55及三義一小段81、158地號等共34筆土地")
        self.assertEqual(地號清單, 
                [
                '玉里鎮三義段4', '玉里鎮三義段55', '玉里鎮三義一小段81', 
                '玉里鎮三義一小段158'
                ])

    def test_get_landcode(self):
        from zhongwen.地號 import 下載段碼表, 段碼, 地碼, 段名
        s = 下載段碼表('U').query('段.str.contains("萬壽")')
        sn = 段碼('萬壽段二小段', 'U') 
        self.assertEqual(sn, 'UA060086' )
        no = 地碼('下台地段410', 'U')
        self.assertEqual(no, 'UA11049604100000')
        sn = 段碼('下台地段', 'U') 
        assert sn == 'UA110496'
        no = 地碼('玉里鎮三義一小段158', 'U')
        assert no == 'UC03034601580000'
        sn = 段碼('水車段', 'U') 
        assert sn == 'UB070247'
        no = 地碼('鳳林鎮水車段1460', 'U') 
        assert no == 'UB07024714600000'
        assert 段碼('三義一小段', 'U') == 'UC030346'
        assert 地碼('鳳林鎮水車段1460地號', 'U') == 'UB07024714600000'

    def test_get_landno(self):
        from zhongwen.地號 import 取地號
        self.assertEqual(取地號('UB024714600000'), '鳳林鎮水車段1460地號')
        self.assertEqual(取地號('024714600000', 'U'), '鳳林鎮水車段1460地號')

    def test_land_secno(self):
        from zhongwen.地號 import 地籍圖段號
        self.assertEqual(
                地籍圖段號('UB07024714600000'), 
                'UB024714600000') 

    def test_secname(self):
        from zhongwen.地號 import 段名
        self.assertEqual(段名('0142', 'U'), '吉安鄉初音段' )

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    # unittest.main()
    suite = unittest.TestSuite()
    # suite.addTest(Test('test_get_landcode'))  # 指定測試
    suite.addTest(Test('test_to_landmark'))  # 指定測試
    unittest.TextTestRunner().run(suite)
