from unittest.mock import patch
import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'
    def test(self):
        from zhongwen.帳 import 取日記帳紀錄, 取交易表示文字
        from zhongwen.表 import 表示
        text = "115.4.11借國旅卡分期-114年度車險貸國旅卡617元，旺旺友聯產物保分12期之第12期。"
        # text = "115.4.1借公教貸款1000元借利息20元貸土銀1020元，繳公教貸款第84之2期。"
        print(取交易表示文字(text, 30))        
        self.assertTrue(False)

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
