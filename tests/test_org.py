import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'
    def test(self):
        from zhongwen.org import 取超文本, org2docx
        from zhongwen.org import 取待辦事項, 排日程, 標記完成
        from zhongwen.表 import 表示
        from datetime import datetime
        from pathlib import Path            
        import os
        # org = Path(r'g:\我的雲端硬碟\00.115-1警察局114年度決算抽查114.12.22-115.1.6\04.道安專調底稿115年4月15日查復\道安查核紀錄.org')
        d = Path(r'g:\我的雲端硬碟')
        s = 排日程(d)
        task = "** TODO [#A] 信用卡結帳及繳費日及扣款帳戶"
        closed_timestamp = datetime.now().strftime("[%Y-%m-%d %a %H:%M]")
        closed_task = ("** DONE [#A] 信用卡結帳及繳費日及扣款帳戶\n"
                       f"CLOSED: {closed_timestamp}"
                      )
        self.assertEqual(標記完成(task), closed_task)
        # print(s)
        # 表示(取待辦事項(d), 顯示索引=False)
        # os.system('py -m zhongwen.org -t -d G:\我的雲端硬碟') 
        # 顯示所有待辦事項(d)
 
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    unittest.main()
