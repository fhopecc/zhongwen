from lark import Lark, Transformer, Tree
from datetime import datetime, timedelta
from diskcache import Cache
from pathlib import Path
from functools import lru_cache
cache = Cache(Path.home() / 'cache')

def 取交易表示文字(交易, 行寬=30):
    'telegram 約三十字寬'
    from zhongwen.數 import 取中文數字 
    from zhongwen.文 import 左補齊, 右補齊, 定寬折行補齊
    import cjkwrap
    金額寬 = 7
    科目寛 = 行寬 // 2 - 金額寬 - 2 # 貸項會右縮2空白
    首欄寬 = 行寬 - 科目寛 - 金額寬 - 2 - 1 # -1 是中間有空白

    raw_data = 取日記帳紀錄(交易) if isinstance(交易, str) else 交易

    d = raw_data[0][0]
    d = 左補齊(f'{d.month}.{d.day}({取中文數字(d.dayofweek+1)})', 首欄寬)
    content = raw_data[0][2]
    left_lines = 定寬折行補齊(f'{d}{content}', 首欄寬)

    right_lines = []
    for r in raw_data:
        '金額係右齊，但借方向左移2個空白。'
        if (debit:=r[3]) > 0:
            rs = cjkwrap.wrap(r[1], 科目寛)
            debit = f'{debit:,}'
            right_lines.append(f"{左補齊(rs[0], 科目寛)}{右補齊(debit, 金額寬)}")
            for r2 in rs[1:]:
                right_lines.append(r2)
        else:
            rs = cjkwrap.wrap(r[1], 科目寛)
            credit = r[4]
            credit = f'{credit:,}'
            right_lines.append(f"  {左補齊(rs[0], 科目寛)}{右補齊(credit, 金額寬)}")
            for r2 in rs[1:]:
                right_lines.append("  "+r2)

    max_height = max(len(left_lines), len(right_lines))
    combined_rows=[] 
    for i in range(max_height):
        l_part = left_lines[i] if i < len(left_lines) else ""
        l_formatted = 左補齊(l_part, 首欄寬) + ' '
        r_part = right_lines[i] if i < len(right_lines) else ""
        r_part = 左補齊(r_part, 行寬-首欄寬-1)
        combined_rows.append(l_formatted + r_part)
    return "\n".join(combined_rows)

def 取交易表示(交易):
    '''
    5.2(五)午餐美崙牛排550元，食 550 
                                 現金  550
    '''
    from zhongwen.數 import 取中文數字 
    ts = 取日記帳紀錄(交易) if isinstance(交易, str) else 交易
    d = ts[0][0] 
    t = ts[0][2]
    content = ts[0][2]
    debit = ts[0][1]
    amount = ts[0][3]
    others = ''
    td_style = "max-width: 5em; word-break: break-all; vertical-align: top;"
    for t in ts[1:]:
        if t[3] > 0:
            others += f'<tr><td></td><td style="{td_style}">{t[1]}</td>'
            others += f'<td style="text-align: right">{t[3]:,}元</td>''' 
        else:
            others += f'<tr><td></td><td></td><td style="{td_style}">{t[1]}</td>'
            others += f'<td style="text-align: right">{t[4]:,}元</td>'   
    html = f'''
    <table>
    <tr><td style="max-width: 20em; word-break: break-all; vertical-align: top;">
           {d.month}.{d.day}({取中文數字(d.dayofweek+1)}){content}
        </td>
        <td style="{td_style}">{debit}</td>
        <td style="text-align: right">{amount:,.0f}元</td></tr>
    {others}
    </table>
    '''
    return html

def 取交易日(日期):
    '將日期以日記帳交易語言表達，即115.4.4'
    from zhongwen.時 import 取民國日期
    return f'{取民國日期(日期, 格式="%Y.%M.%D")}'

def 取日記帳紀錄(交易):
    '''
    一、日記帳交易紀錄：日期、科目、備註、借、貸。
    二、交易紀錄借貸不平衡會引發錯誤。    
    三、僅有日期則傳回日期物件。
    四、沖帳交易傳回字典。
    '''
    from zhongwen.時 import 取日期
    import pandas as pd
    try:
        parser = Lark(accounting_grammar, parser='earley')
        transformer = AccountingTransformer()
        parsed_data = transformer.transform(parser.parse(交易))
        final_list = transform_and_validate(parsed_data)
        return final_list
    except Exception as e: pass
    try:
        return 取沖帳交易(交易)
    except Exception as e: pass
    try:
        return 取日記帳紀錄(自備註取交易(交易))
    except Exception as e: pass
    
    d = 取日期(交易)
    if pd.notna(d):
        return d
    return 交易

# --- 1. 定義 Lark 語法 ---
accounting_grammar = r"""
    start: [date] items summary

    ?date: relative_date | short_date | full_date
    relative_date: RELATIVE_KEY
    short_date: (MONTH ".")? DAY
    full_date: YEAR "." MONTH "." DAY

    RELATIVE_KEY: "今" | "昨" | "前" | "大前"
    YEAR: /\d+/
    MONTH: /\d+/
    DAY: /\d+/

    ?items: shorthand_items | standard_items
    
    # 1 借 1 貸 1 金額模式
    shorthand_items: "借" DNAME "貸" CNAME AMOUNT "元"

    standard_items: (debit_item | credit_item)+
    debit_item: "借" DNAME AMOUNT "元"
    credit_item: "貸" CNAME AMOUNT "元"
    
    summary: "，" SUMMARY_CONTENT
    
    # 【邏輯核心】
    # 匹配任何非特殊字元。
    # 遇到「貸」字時，只有在後面「不是」款、項、、字、數字、元、逗號時才停止。
    # 這確保了「公教貸款」會被完整抓取。
    DNAME: /((?!\d+元)\d+|[^\d借貸元，\s]|貸(?=款))++/
    CNAME: /((?!\d+元)\d+|[^\d借貸元，\s]|貸(?=款))++/
    
    AMOUNT: /\d+/
    SUMMARY_CONTENT: /.+/

    %import common.WS
    %ignore WS
"""

# --- 2. 定義 Transformer ---
class AccountingTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.today = datetime.now()

    def relative_date(self, children):
        mapping = {"今": 0, "昨": 1, "前": 2, "大前": 3}
        delta = mapping.get(str(children[0]), 0)
        return self.today - timedelta(days=delta)

    def short_date(self, children):
        if len(children) == 1:
            m, d = self.today.month, int(children[0])
        else:
            m, d = int(children[0]), int(children[1])
        return datetime(self.today.year, m, d)

    def full_date(self, children):
        y, m, d = map(int, children)
        if y < 1000: y += 1911 
        return datetime(y, m, d)

    def shorthand_items(self, children):
        n_debit, n_credit = str(children[0]).strip(), str(children[1]).strip()
        amt = int(children[2])
        return [
            {"type": "debit", "name": n_debit, "amount": amt},
            {"type": "credit", "name": n_credit, "amount": amt}
        ]

    def standard_items(self, children):
        return children

    def debit_item(self, children):
        return {"type": "debit", "name": str(children[0]).strip(), "amount": int(children[1])}

    def credit_item(self, children):
        return {"type": "credit", "name": str(children[0]).strip(), "amount": int(children[1])}

    def summary(self, children):
        return str(children[0]).strip()

    def start(self, children):
        dt = next((c for c in children if isinstance(c, datetime)), self.today)
        items = next(c for c in children if isinstance(c, list))
        sum_content = str(children[-1])

        roc_year = dt.year - 1911
        formatted_date = f"{roc_year}.{dt.month}.{dt.day}"
        
        res = {"date": formatted_date, "debit": [], "credit": [], "summary": sum_content}
        for item in items:
            res["debit" if item['type'] == 'debit' else "credit"].append(item)
        return res

# --- 3. 轉換與檢核 ---
def transform_and_validate(result_dict):
    from zhongwen import 時
    output = []
    date, summary = result_dict['date'], result_dict['summary']
    date = 時.取日期(result_dict['date'])
    total_debit = sum(item['amount'] for item in result_dict['debit'])
    total_credit = sum(item['amount'] for item in result_dict['credit'])

    if total_debit != total_credit or total_debit == 0:
        raise ValueError(f"【分錄不平衡】借方：{total_debit} / 貸方：{total_credit}")

    for item in result_dict['debit']:
        output.append([date, item['name'], summary, item['amount'], 0])
    for item in result_dict['credit']:
        output.append([date, item['name'], summary, 0, item['amount']])
    return output

# 定義語法變數為 accounting2， 針對沖轉

# 語法修正重點：
# 1. DATE_STR 改為只要是 數字、點、斜線的組合即可，甚至只有一個數字
# 2. account 排除掉開頭的 "沖" 與結尾的數字/元/句號
accounting2 = r"""
    ?start: [date] "沖" account [amount] [DOT]

    date: DATE_STR
    account: /.+?(?=\d|元|。|$)/
    amount: NUMBER [UNIT]
    
    DATE_STR: /[\d\.\/]+/
    UNIT: "元"
    DOT: "。"

    %import common.NUMBER
    %import common.WS
    %ignore WS
"""

class Accounting2Transformer(Transformer):
    def date(self, items):
        return str(items[0])

    def account(self, items):
        return str(items[0]).strip()

    def amount(self, items):
        # 將數字與單位結合成字串，如 "1000元"
        return "".join([str(i) for i in items if i])

    def start(self, items):
        res = {"日期": "", "沖轉科目": "", "金額": ""}
        for item in items:
            if isinstance(item, Tree):
                if item.data == 'date':
                    res["日期"] = str(item.children[0])
                elif item.data == 'account':
                    res["沖轉科目"] = str(item.children[0])
                elif item.data == 'amount':
                    # 如果子規則 amount 已經被轉換成字串
                    res["金額"] = "".join([str(c) for c in item.children if c])
            # 容錯處理：如果項目已經被轉換器轉成字串
            elif isinstance(item, str):
                if item == "。": continue
                # 這裡的邏輯：如果 res 裡面的位置還是空的，就按順序填入
                # 或是根據內容特徵判斷
                pass 
        
        # 由於 LALR 可能會提早轉換子項，我們可以直接在 transform 階段處理
        return res

def 取沖帳交易(沖帳交易):
    '''
    一、傳回日期、沖轉科目及金額。
    '''
    from zhongwen.數 import 取數值
    from zhongwen.時 import 取日期
    import pandas as pd
    parser = Lark(accounting2, parser='earley') 
    tree = parser.parse(沖帳交易)
    日期 = 沖轉科目 = 借項科目 = 貸項科目 = 金額 = ''
    # 建立一個簡單的提取器
    for subtree in tree.children:
        if not isinstance(subtree, Tree): continue
        if subtree.data == 'date':
            日期 = 取交易日(str(subtree.children[0]))
        elif subtree.data == 'account':
            沖轉科目 = str(subtree.children[0]).strip()
        elif subtree.data == 'amount':
            # 結合數字與單位
            金額 = "".join([str(c) for c in subtree.children if c])
    s = pd.Series()
    s['日期'] = 日期
    s['沖轉科目'] = 沖轉科目
    s['金額'] = 金額
    return s
    # return f'{日期}借{借項科目}貸{貸項科目}{金額}，沖銷{沖轉科目}'
    # if '應付' in 沖轉科目:
    #     借項科目 = 沖轉科目
    #     貸項科目 = 沖轉科目.split('應')[0]
    #     from 財務.日記帳 import 日記帳
    #     try:
    #         沖轉科目餘額 = 日記帳().應付餘額明細().loc[沖轉科目].餘額
    #     except KeyError:
    #         raise ValueError(f'「{沖帳交易}」無該項沖轉科目！')
    # if 借項科目 == '':
    #     raise ValueError(f'「{沖帳交易}」推論借項科目為空！')
    # if 貸項科目 == '':
    #     raise ValueError(f'「{沖帳交易}」推論貸項科目為空！')
    # if 沖轉科目餘額 == 0:
    #     raise ValueError(f'「{沖帳交易}」沖轉科目無待沖轉金額即科目餘額為零！')
    # if 金額 == '':
    #     金額 = f'{沖轉科目餘額:.0f}元'
    # else:
    #     金額數 = 取數值(金額)
    #     if 金額數 > 沖轉科目餘額:
    #         raise ValueError(f'「{沖帳交易}」沖轉金額大於待沖轉金額{沖轉科目餘額:.0f}元！')
    # print('沖帳交易')

# 備註推論交易
@lru_cache
@cache.memoize(tag='關鍵字模式表')
def 載入關鍵字模式表(f=Path(__file__).parent / 'resource' / '借項關鍵字'):
    '關鍵字表不能包含空行'
    import re
    print(f'重新戴入{f}！')
    with open(f, 'r', encoding='utf8') as f:
        ls = f.readlines()
        for l in ls:
            kws = l.strip().split(' ')            
        return [(re.compile("("+'|'.join(kws[1:])+")", flags=re.IGNORECASE)
               ,kws[0]) for kws in [l.strip().split(' ') for l in ls]]

def 重載():
    載入關鍵字模式表.cache_clear()
    cache.evict('關鍵字模式表')

def 取借項(desc):
    '依備註所含關鍵字推論借項科目'
    for pat in 載入關鍵字模式表(f=Path(__file__).parent / 'resource' / '借項關鍵字'):
        if pat[0].search(desc):
            return pat[1] 
    return '食'

def 取貸項(desc):
    for pat in 載入關鍵字模式表(f=Path(__file__).parent / 'resource' / '貸項關鍵字'):
        if pat[0].search(desc):
            return pat[1] 
    return '現金'

def 取金額(desc):
    '從交易描述取出金額'
    from zhongwen.數 import 取數值
    import re
    pat = r'(\d+)元'
    if m:=re.findall(pat, desc):
        return sum(map(取數值, m))
    return None

def 自備註取交易日(desc):
    from zhongwen.時 import 今日
    import re
    pat = r'^(\d{3}\.\d{1,2}\.\d{1,2})'
    if m:=re.search(pat, desc):
        return 取交易日(m)
 
    pat = r'^(\d{1,2}\.\d{1,2})'
    if m:=re.search(pat, desc):
        return 取交易日(m)
    return ''

def 自備註取交易(備註):
    from zhongwen.數 import 取數值
    日期 = 借項科目 = 貸項科目 = 金額 = ''
    日期 = 取交易日(自備註取交易日(備註))
    借項科目 = 取借項(備註)
    貸項科目 = 取貸項(備註)
    金額 = 取金額(備註)
    if 金額 is None:
        raise ValueError(f'「{備註}」無金額！')
    print('自備註取交易')
    return f'{日期}借{借項科目}貸{貸項科目}{金額:.0f}元，{備註}'
