from zhongwen.pandas_tools import 可顯示
from pathlib import Path
from diskcache import Cache
import pandas as pd
cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

def 中央法律():
    url = 'https://sendlaw.moj.gov.tw/PublicData/GetFile.ashx?DType=XML&AuData=CF'
    z = Path.home() / 'TEMP' / 'falv.zip'
    下載(url, z)
    falv = Path.home() / 'TEMP' / 'law' / 'FalV.xml'
    解壓(z, falv.parent)
    from xml.etree.cElementTree import parse
    return parse(falv)

def 中央命令():
    url = 'https://sendlaw.moj.gov.tw/PublicData/GetFile.ashx?DType=XML&AuData=CM'
    z = Path.home() / 'TEMP' / 'mingling.zip'
    下載(url, z)
    minling = Path.home() / 'TEMP' / 'law' / 'MingLing.xml'
    解壓(z, minling.parent)
    from xml.etree.cElementTree import parse
    return parse(minling)

@可顯示
@cache.memoize(expire=30*24*60*60)
def 法規條文() -> pd.DataFrame:
    '法規條文係以法規名稱、異動日期及條號為索引來查詢條文內容'
    from pandas import DataFrame, concat
    l = 中央法律()
    def 法條資料表(法規):
        def 條號數(s):
            pat = r'第[^\d]*([-\d]+)[^\d]*條'
            if m:=re.match(pat, s):
                return m[1]
            return s
        條號 = [條號數(n.find('條號').text) for n in 法規.findall('*/條文')]
        條文內容 = [n.find('條文內容').text for n in 法規.findall('*/條文')]
        df = DataFrame(data = {'條號':條號, '條文內容':條文內容})
        df['法規名稱'] = 法規.find('法規名稱').text
        df['異動日期'] = 法規.find('最新異動日期')
        return df[['法規名稱', '異動日期', '條號', '條文內容']]
    law = concat([法條資料表(法規) for 法規 in 中央法律().findall('法規')])
    mingling = concat([法條資料表(法規) for 法規 in 中央命令().findall('法規')]) 
    df = concat([law, mingling])
    from zhongwen.date import 取日期
    df['異動日期'] = df.異動日期.map(取日期)
    return df

def 產製法規文字檔(法規名稱):
    df = 法規條文()
    df = df.query('法規名稱==@法規名稱')[["條號", "條文內容"]]
    content = '\n'.join([f"第{r.條號}條{r.條文內容}"for r in df.itertuples()])
    txt = Path(f'{法規名稱}.txt')
    txt.write_text(content)

if __name__ == '__main__':
    法規條文(顯示=True)
