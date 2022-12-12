import unittest
from pathlib import Path
import pandas as pd
import os

class Test(unittest.TestCase):

    def test(self):
        from zhongwen.花蓮縣法規 import 法規
        # df = cache.get('花蓮縣法規')
        # print(df)
        # for k in cache.iterkeys():
            # print(k)
        # print(cache.iterkeys())
        df = 法規().query('法規體系=="建設"')
        df = df[['法規名稱', '公發布日']]
        df.reset_index(inplace=True)
        df = df.iloc[:100]
        html = Path.home() / 'TEMP' / 'output.html'
        df.to_html(html)
        os.system(f'start {html}')

if __name__ == '__main__':
    unittest.main()
