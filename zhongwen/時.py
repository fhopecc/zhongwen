from zhongwen.date import 取日期, 自起日按日列舉迄今
from zhongwen.date import 今日, 民國日期, 上年底, 年底

def 正式民國日期(d=None):
    '格式如：112年7月29日'
    if not d:
        d = 今日()
    return 民國日期(d, "%Y年%M月%D日")

