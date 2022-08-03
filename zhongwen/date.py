'日期處理'
import re
from datetime import date
from datetime import datetime

def 取日期(d, first=True):
    pat = r'\d{4}/\d{1,2}/\d{1,2}'
    if m:=re.match(pat, d):
        return datetime.strptime(m[0], '%Y/%m/%d')
    pat = r'\d{4}.\d{1,2}.\d{1,2}'
    if m:=re.match(pat, d):
        return datetime.strptime(m[0], '%Y.%m.%d')

    # 民國日期格式109/05/29
    pat = r'(\d{3})/(\d{1,2})/(\d{1,2})'
    if m:=re.match(pat, d):
        return datetime(int(m[1])+1911, int(m[2]), int(m[3]))
    return d

def 取民國日期(d, last=True):
    return rocdate(d, last)

def r(d, last=True):
    return rocdate(d, last)

def 上月():
    '上月'
    d = date.today()
    return f'{d.year-1911:03}{d.month-1:02}'

def rocdate(d, last=True, ignore_error=True):
    '自字串萃取民國日期並轉為datetime，last 取得最後一個找到的日期'
    try:
        import numbers
        do = d
        #日期如為數字，先轉7位字串
        if isinstance(d, numbers.Number):
            d = f'{d:07d}'
            #print(f'{d} is number')

        #日期格式為980101,1090529
        pat = r'(\d{2,3})(\d\d)(\d\d)'
        if r:=re.search(pat, d): return datetime(int(r[1])+1911, int(r[2]), int(r[3]))
        #日期格式為106年3月12日
        r = re.search((r'(?s:.*)' if last else '') +
                       r'(\d{2,3})年(\d{1,2})月(\d{1,2})日', d)
        if(r): return datetime(int(r[1])+1911, int(r[2]), int(r[3]))

        #日期格式為109/05/29
        r = re.search((r'(?s:.*)' if last else '') + r'(\d{2,3})/(\d{1,2})/(\d{1,2})', d)
        if(r): return datetime(int(r[1])+1911, int(r[2]), int(r[3]))

        #日期格式為98.1.1, 109.5.29, 110.1.20
        pat = r'(\d{2,3}).(\d{1,2}).(\d{1,2})'
        r = re.search(pat, d)
        if r: return datetime(int(r[1])+1911, int(r[2]), int(r[3]))
    except ValueError:
        if ignore_error: return None
        raise ValueError(f'[{do}]為錯誤日期格式!')
    if ignore_error: return None
    raise ValueError(f'[{do}]為錯誤日期格式!')

def 民國日期(d):
    if isinstance(d, str):
        # 110.11.10 -> 110年11月10日
        pat = '\d{7}'
        if re.match(pat, d): 
            return f'{d[0:3]}年{int(d[3:5])}月{int(d[5:7])}日'
        pat = '(\d{2,3}).(\d{1,2}).(\d{1,2})'
        if m := re.match(pat, d): 
            year = m[1]
            mon = m[2]
            day = m[3]
            return f'{year}年{mon}月{day}日'

    return f'{d.year-1911}年{d.month}月{d.day}日'

def 約年(timedelta):
    return f'{timedelta.days/365:0.0f}年餘'

def 逾(start, end):
    return f'逾{約年(r(end) - r(start))}'

def 上年度():
    d = date.today()
    return f'{d.year-1911-1}年度'

def 本年度():
    d = date.today()
    return f'{d.year-1911}年度'

def 上上年度():
    d = date.today()
    return f'{d.year-1911-2}年度'

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", help="設定環境", action="store_true")
    parser.add_argument("--rocdate", help="民國日期")
    args = parser.parse_args()
    if args.rocdate:
        print(民國日期(args.rocdate))
