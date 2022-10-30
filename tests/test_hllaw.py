import unittest
from pathlib import Path
import pandas as pd
import os

class Test(unittest.TestCase):

    def test(self):
        from zhongwen.hllaw import 法規
        df = 法規().query('法規體系=="消防"')
        # df = df[['法規名稱', '修正日期']]
        # df = df.query('法規內容.str.contains("城鄉發展處|工務處|會計科")')
        # df = df.iloc[:100]
        # html = Path.home() / 'TEMP' / 'output.html'
        # df.to_html(html)
        # os.system(f'start {html}')

        from zhongwen.hllaw import 開啟網頁
        開啟網頁()


if __name__ == '__main__':
    unittest.main()
