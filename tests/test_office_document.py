import unittest
import logging

class Test(unittest.TestCase):

    def test_markdown(self):
        from zhongwen.office_document import 標題階層編號轉中文編號 
        from subprocess import check_output
        t = '6	擬議處理意見'
        o = '陸、擬議處理意見'
        self.assertEqual(標題階層編號轉中文編號(t), o)

        t = '1.2.1 三級管控核有缺失'
        o = '一、三級管控核有缺失'
        self.assertEqual(標題階層編號轉中文編號(t), o)

        out = check_output('py -m zhongwen.office_document --level_number_to_chinese_number "1.2.1 三級管控核有缺失"', shell=True)
        self.assertEqual(out.decode('cp950').rstrip(), '一、三級管控核有缺失')

    def test_markdown_to_docx(self):
        from docx import Document
        from pathlib import Path
        from zhongwen.number import 中文數字, 大寫中文數字
        import re
        f = r'g:\我的雲端硬碟\01.114-2花縣府觀旅處1013下午-28-1025提出\02.旅宿業輔導\旅宿業查核工作紀錄.docx'
        document = Document(f)
        階層 = 0
        for paragraph in document.paragraphs:
            print(paragraph.style.name)
            if m:='Heading' in paragraph.style.name:
                runs = list(paragraph.runs)
                if len(runs) > 0:
                    text = runs[0].text
                    pat = r'^((\d+.)*(\d+))$'
                    if m:=re.match(pat, text):
                        階層 = m[1].count('.')
                        編號 = m[3]
                        if 階層==0:
                            編號 = ''
                        elif 階層==1:
                            編號 = f'{大寫中文數字(編號)}、'
                        elif 階層==2: 
                            編號 = f'{中文數字(編號)}、'
                        elif 階層==3: 
                            編號 = f'({中文數字(編號)})'
                        elif 階層==4: 
                            編號 = f'{編號}.'
                        elif 階層==5: 
                            編號 = f'({編號})'
                        runs[0].text = text.replace(m[1], 編號)
            if 'Normal' in paragraph.style.name:
                if int(階層)>0:
                    paragraph.style = f'內文{階層+1}'
        f = Path(f)
        document.save(str(f.with_stem(f'{f.stem}新')))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)
 
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Test('test_markdown_to_docx'))  # 指定要執行的測試方法
    unittest.TextTestRunner().run(suite)
