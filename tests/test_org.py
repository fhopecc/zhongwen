import unittest

class Test(unittest.TestCase):
    '依方法名稱字母順序測試'
    def test(self):
        from pathlib import Path            
        from zhongwen.org import 取超文本, org2docx
        org = Path(r'g:\我的雲端硬碟\文件\鞋.org')
        # html = 取超文本(org)
        org2docx(org)
 
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    unittest.main()
