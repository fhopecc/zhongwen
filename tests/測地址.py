import unittest
from pathlib import Path
import logging
logger = logging.getLogger(Path(__file__).stem)

class Test(unittest.TestCase):
       
    # @unittest.skip("demonstrating skipping")
    def test2(self):
        from zhongwen.地址 import 標準地址, 刪除鄰
        self.assertEqual(刪除鄰('中山路12鄰3號'), '中山路3號')
        self.assertEqual(刪除鄰('宜蘭縣羅東鎮中山路12鄰3-3號'), '宜蘭縣羅東鎮中山路3-3號')
        self.assertEqual(刪除鄰('宜蘭縣羅東鎮12鄰中山路3-3號'), '宜蘭縣羅東鎮中山路3-3號')
        self.assertEqual(刪除鄰('宜蘭縣羅東鎮九鄰中山路3-3號'), '宜蘭縣羅東鎮中山路3-3號')

    def test_addr(self):
        from zhongwen.地址 import 標準地址, 刪除鄰
        

        self.assertEqual(標準地址(123), 123)

        self.assertEqual(標準地址('978花蓮縣瑞穗鄉瑞祥村溫泉路3段137號'), 
            '瑞穗鄉溫泉路3段137號')

        self.assertEqual(標準地址('花蓮縣花蓮市美崙區永興路2號'), '花蓮市永興路2號')

        self.assertEqual(標準地址('花蓮縣花蓮市主信里忠孝街65號'), '花蓮市忠孝街65號')

        self.assertEqual(標準地址('花蓮市水源街八十號'), '花蓮市水源街80號')


        self.assertEqual(標準地址('花蓮縣吉安鄉吉安村吉安路二段一五０號'), 
            '吉安鄉吉安路2段150號'
            )

        self.assertEqual(標準地址('花蓮縣新城鄉大漢村光復路五七○號'), '新城鄉光復路570號')
        self.assertEqual(標準地址('花蓮縣光復鄉民有街五一巷三號'), '光復鄉民有街51巷3號')
        self.assertEqual(標準地址('花蓮縣秀林鄉文蘭村7鄰米亞丸一號'), '秀林鄉米亞丸1號')
        self.assertEqual(標準地址('花蓮縣花蓮市公園路1之7號'), '花蓮市公園路1-7號')
        self.assertEqual(標準地址('花蓮市國聯一路一００之五號'), '花蓮市國聯一路100-5號')
        self.assertEqual(標準地址('花蓮市國風里5鄰林森路126號'), '花蓮市林森路126號')
        self.assertEqual(標準地址('花蓮縣花蓮市國富里037鄰中央路三段842號')
                                 ,'花蓮市中央路3段842號')
        self.assertEqual(標準地址('花蓮縣吉安鄉北昌村5鄰自立路34巷8號')
                                 ,'吉安鄉自立路34巷8號')
        self.assertEqual(標準地址('花蓮縣新城鄉新城村博愛路 31 號')
                                 ,'新城鄉博愛路31號')


        self.assertEqual(標準地址('花蓮縣吉安鄉中山路二段245、247號'),
                        ['吉安鄉中山路2段245號'
                        ,'吉安鄉中山路2段247號'
                        ])

        self.assertEqual(標準地址('花蓮縣花蓮市民孝里16鄰東興一街79巷18號12樓之3')
                        ,'花蓮市東興一街79巷18號12樓之3')

        self.assertEqual(標準地址('花蓮縣新城鄉順安村6鄰草林10-5號二樓之1')
                        ,'新城鄉草林10-5號2樓之1')

        self.assertEqual(標準地址('花蓮縣花蓮市中山路553號1F樓')
                        ,'花蓮市中山路553號1樓')

        self.assertEqual(標準地址('花蓮縣花蓮市國聯五路１５１號６Ｆ')
                        ,'花蓮市國聯五路151號6樓')

        self.assertEqual(標準地址('花蓮縣花蓮市化道路28號A棟1樓'), '花蓮市化道路28號1樓')

        
        self.assertEqual(標準地址('花蓮縣花蓮市中正路530號6~8樓'), 
                        ['花蓮市中正路530號6樓', '花蓮市中正路530號7樓', '花蓮市中正路530號8樓'])

        self.assertEqual(標準地址('花蓮縣花蓮市國聯五路123號1-2樓')
                        ,['花蓮市國聯五路123號1樓', '花蓮市國聯五路123號2樓'])

        self.assertEqual(標準地址('花縣花蓮市中美路２５６號之１三．四樓')
                        ,['花蓮市中美路256-1號3樓'
                         ,'花蓮市中美路256-1號4樓'])

        self.assertEqual(標準地址('花蓮縣花蓮市國聯二路124號1至2樓')
                        ,['花蓮市國聯二路124號1樓', '花蓮市國聯二路124號2樓'])


        self.assertEqual(標準地址('花蓮縣花蓮市民心里民國路153號B1~9樓')
                        , 
            ['花蓮市民國路153號地下1樓'
            ,'花蓮市民國路153號1樓'
            ,'花蓮市民國路153號2樓'
            ,'花蓮市民國路153號3樓'
            ,'花蓮市民國路153號4樓'
            ,'花蓮市民國路153號5樓'
            ,'花蓮市民國路153號6樓'
            ,'花蓮市民國路153號7樓'
            ,'花蓮市民國路153號8樓'
            ,'花蓮市民國路153號9樓']
            )
        self.assertEqual(標準地址(
            '花蓮縣花蓮市和平路336-1號B2.1.8.9樓'
            ), 
            ['花蓮市和平路336-1號地下2樓'
            ,'花蓮市和平路336-1號1樓'
            ,'花蓮市和平路336-1號8樓'
            ,'花蓮市和平路336-1號9樓'
            ]
            )
        self.assertEqual(標準地址('花蓮縣花蓮市中山路269號1至3樓', True), 
            ['花蓮市中山路269號'
            ,'花蓮市中山路269號1樓'
            ,'花蓮市中山路269號2樓'
            ,'花蓮市中山路269號3樓'
            ])

        self.assertEqual(標準地址('花蓮縣花蓮市中正路581號1樓', True), 
            ['花蓮市中正路581號'
            ,'花蓮市中正路581號1樓'
            ])

        self.assertEqual(標準地址(
            '花蓮縣玉里鎮國武里28鄰中山路二段62.64號1樓'
            ),
            ['玉里鎮中山路2段62號'
            ,'玉里鎮中山路2段64號1樓'
            ])
            
        self.assertEqual(標準地址('花蓮縣新城鄉康樂村加灣39號之16'), '新城鄉加灣39-16號')
        self.assertEqual(標準地址('花蓮縣秀林鄉富世村231-1號'), '秀林鄉富世231-1號')
        self.assertEqual(標準地址('花蓮縣秀林鄉和平村2鄰107號'), '秀林鄉和平107號')
        self.assertEqual(標準地址('花蓮縣秀林鄉銅門村六九號'), '秀林鄉銅門69號')
        self.assertEqual(標準地址('花蓮縣新城鄉七星街58號(花蓮縣)'), '新城鄉七星街58號')
        self.assertEqual(標準地址('花蓮縣花蓮市花蓮市主信里8鄰南京街155號')
                         ,'花蓮市南京街155號')
        '花蓮縣花蓮市主商里16鄰光復街13-3,-4,-5,-6號'
        '花蓮縣花蓮市中正路560/562號1-5/1-3樓'

    @unittest.skip("demonstrating skipping")
    def test地址地理編碼(self):
        from shapely.geometry import Point
        from zhongwen.地址 import 地址座標
        a = '花蓮市中美路295之59號'
        self.assertEqual(地址座標(a).x, 121.63128)

    def test_correct_name(self):
        from zhongwen.地址 import 修正誤植名稱
        self.assertEqual(修正誤植名稱('花蓮縣花蓮市美崙區永興路2號'), 
                        '花蓮縣花蓮市永興路2號')

    def test_road(self):
        from zhongwen.地址 import 標準路名
        self.assertEqual(標準路名("華城5街"), "華城五街")
        self.assertEqual(標準路名("民德民權四街"), "民權四街")
        self.assertEqual(標準路名('大學路二段'), '大學路2段')
        self.assertEqual(標準路名('中山路ㄧ段'), '中山路1段')
        self.assertEqual(標準路名('民有街五一巷'), '民有街51巷')

    def test_no(self):
        from zhongwen.地址 import 標準門牌號
        self.assertEqual(標準門牌號('康樂村加灣39號之16'), '加灣39-16號')
        self.assertEqual(標準門牌號('樂合里溫泉36號'), '溫泉36號')
        self.assertEqual(標準門牌號('加灣39號之16'), '加灣39-16號')
        self.assertEqual(標準門牌號('加灣39-16號'), '加灣39-16號')
        self.assertEqual(標準門牌號('富世村231-1號'), '富世231-1號')
        self.assertEqual(標準門牌號('152之2，152之3號'), ['152-2號', '152-3號'])
        self.assertEqual(標準門牌號('152之2,152之3號'), ['152-2號', '152-3號'])

        # 花蓮縣新城鄉順安村6鄰草林10-5號 = 花蓮縣新城鄉順安村草林10之5號
        # 花蓮縣新城鄉嘉里村嘉里路59號 = 花蓮縣新城鄉嘉里村5鄰嘉里路59號	
        # 花蓮縣花蓮市國聯三路42號1樓美容美髮服務業&化粧品零售業 = 花蓮縣花蓮市國聯三路42號1樓
        # 花蓮縣玉里鎮國武里民權街50號 = 花蓮縣玉里鎮民權街50號	 
        # print(標準地址('花蓮縣新城鄉大漢村4鄰七星街152之2，152之3號'))

    def test_level(self):
        from zhongwen.地址 import 標準樓
        self.assertEqual(標準樓('1樓及2樓'), ['1樓', '2樓'])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    unittest.main()
    suite = unittest.TestSuite()
    # suite.addTest(Test('test2'))  # 指定測試
    unittest.TextTestRunner().run(suite)
