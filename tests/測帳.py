from unittest.mock import patch
import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'
    def test(self):
        from zhongwen.帳 import 紀錄, 交易
        from zhongwen.帳 import 取日記帳紀錄, 取交易表示文字, 自備註取交易
        from zhongwen.帳 import 取交易表示繪文字
        from zhongwen.帳 import 自備註取交易, 重載
        from zhongwen.表 import 表示
        from 財務.日記帳 import 日記帳
        import re

        t = 交易.自文字解析("縣府福利社購當歸茶葉蛋2顆25元作早餐")
        print(t.多行表達)
        self.assertFalse(True)
        t = 交易.自文字解析("115.4.1繳公教貸款第84之2期，分錄為借記公教貸款1000元、利息20元，貸記土銀1020元")

        t = 交易.自文字解析('申請6月18時加班費，分錄為借記應收6月加班費6516元，貸記薪資6516元')
        print(t)
        j = 日記帳()
        j.插入交易(t)
        t = 交易.自文字解析('6.19至佛堂獻端午晚香，回程開車經小路撞到狗，回到美崙提款洗車，分錄為借記行400元，貸記現金400元')
        t = 交易('115.6.19'
                ,'至佛堂獻端午晚香，回程開車經小路撞到狗，回到美崙提款洗車'
                ,'行', 400, '現金', -400)
        self.assertEqual(t.紀錄清單[0].科目, '行')
        t = 交易.自文字解析('115.6.19至佛堂獻端午晚香，回程開車經小路撞到狗，回到美崙提款洗車，分錄為借記行400元，貸記現金400元')        
        self.assertEqual(t.紀錄清單[0].科目, '行')
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
