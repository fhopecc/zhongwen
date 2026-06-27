from unittest.mock import patch
import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'
    def test(self):
        from zhongwen.帳 import 分錄, 交易  
        from zhongwen.帳 import 取日記帳紀錄, 取交易表示文字, 自備註取交易
        from zhongwen.帳 import 取交易表示繪文字
        from zhongwen.帳 import 自備註取交易, 重載
        from zhongwen.表 import 表示
        import re 

        t = 交易('115.6.19'
                ,'至佛堂獻端午晚香，回程開車經小路撞到狗，回到美崙提款洗車'
                ,'行', 400, '現金', -400)
        self.assertTrue(t.分錄清單[0].科目, '行')
        print(t)
        self.assertFalse(True)
        t = ''
        t = '美崙牛排午餐800元'
        t = 自備註取交易(t) 

        t = "給品500元零用"
        emoji = 取交易表示繪文字(t)
        print(emoji)
        self.assertFalse(True)
        d = 取日記帳紀錄(t)
        d = 自備註取交易(t)
        print(d)        
        l = [['國旅卡分期-114年度車險', 400, 0], ['現金', 0, 400]]
        print(取分錄明細等寬字表達(l))
        print(取交易表示文字(text, 30))        

        text = "115.4.11借國旅卡分期-114年度車險貸國旅卡617元，旺旺友聯產物保分12期之第12期。"
        d = 取日記帳紀錄(text)
        self.assertEqual(d[0][1], '國旅卡分期-114年度車險')
        self.assertEqual(d[1][1], '國旅卡')

        text = "郵局網銀"
        d = 取日記帳紀錄(text)
        self.assertEqual(d, text)
 
        text = "115.4.4"
        print(text)
        d = 取日記帳紀錄(text)
        print(d)

        text = "統一超提現3000元。"
        print(text)
        d = 取日記帳紀錄(text)

        print(d)
        text = "沖土銀應付泰銘股款。"
        print(text)
        d = 取日記帳紀錄(text)
        self.assertEqual(d.沖轉科目, '土銀應付泰銘股款')
        text = "1沖土銀應付泰銘股款。"
        print(text)
        d = 取日記帳紀錄(text)
        print(d)
        text = "沖土銀應付泰銘股款1000元。"
        print(text)
        d = 取日記帳紀錄(text)
        print(d)
        text = "1沖土銀應付泰銘股款1000元。"
        print(text)
        d = 取日記帳紀錄(text)
        print(d)
        text = "115.4.1沖土銀應付泰銘股款1000元。"
        print(text)
                
        d = 取日記帳紀錄(text)
        print(d)

        text = "115.4.1借公教貸款1000元借利息20元貸土銀1020元，繳公教貸款第84之2期。"
        print(text)
        d = 取日記帳紀錄(text)
        print(d)
        text = "借公教貸款貸土銀1000元，繳公教貸款第84之2期。"
        print(text)
        d = 取日記帳紀錄(text)
        self.assertEqual(d[0][1], '公教貸款')
        self.assertEqual(d[1][1], '土銀')
        print(d)
        text = "昨借土銀貸公教貸款1000元，貸出公教貸款。"
        print(text)
        d = 取日記帳紀錄(text)
        print(d)
        text = "15借公教貸款貸土銀1000元，繳公教貸款第84之2期。"
        print(text)
        d = 取日記帳紀錄(text)
        print(d)
 
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
