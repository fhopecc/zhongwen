from lark import Transformer

def 取日記帳紀錄(交易紀錄):
    '''
    一、日記帳交易紀錄：日期、科目、備註、借、貸
    
    '''
    from lark import Lark
    import re
    parser = Lark(accounting_grammar, start='start', parser='earley')
    transformer = AccountingTransformer()
    tree = parser.parse(交易紀錄)
    d = transformer.transform(tree)
    output = []
    date = d['交易日期']
    summary = d['摘要']
    
    # 定義內部處理邏輯：提取名稱與金額
    def parse_item(item_str):
        # 匹配「科目名稱」與「數字」
        match = re.match(r"(.+?)(\d+)元", item_str)
        if match:
            return match.group(1), int(match.group(2))
        return item_str, 0

    for item in d['借項科目']:
        name, amount = parse_item(item)
        output.append([date, name, summary, amount, 0])
    for item in d['貸項科目']:
        name, amount = parse_item(item)
        output.append([date, name, summary, 0, amount])
    return output

# 基礎交易語法規則
accounting_grammar = r"""
    start: date items summary

    date: YEAR "." MONTH "." DAY
    
    # 這裡讓 items 可以包含多個借或貸，順序不限更靈活
    items: (debit_item | credit_item)+
    
    # 使用 ? 做非貪婪匹配，直到遇見「數字+元」為止
    debit_item: "借" NAME AMOUNT "元"
    credit_item: "貸" NAME AMOUNT "元"
    
    # 摘要由逗號開始，抓取剩餘所有文字
    summary: "，" ANY_TEXT
    
    YEAR: /\d+/
    MONTH: /\d+/
    DAY: /\d+/
    AMOUNT: /\d+/
    
    # 核心修正：NAME 不包含數字，且遇到「借/貸 + 數字」前就會停止
    # 使用負向預覽 (negative lookahead) 確保不把作為標記的「借/貸」吃進去
    NAME: /.+?(?=\d+元)/
    
    ANY_TEXT: /.+/

    %import common.WS
    %ignore WS
"""

class AccountingTransformer(Transformer):
    def start(self, children):
        # 初始化結構
        res = {"交易日期": children[0], "借項科目": [], "貸項科目": [], "摘要": children[2]}
        items = children[1]
        for item in items:
            if item['type'] == 'debit':
                res["借項科目"].append(f"{item['name']}{item['amount']}元")
            else:
                res["貸項科目"].append(f"{item['name']}{item['amount']}元")
        return res

    def date(self, children):
        return f"{children[0]}.{children[1]}.{children[2]}"

    def items(self, children):
        return children

    def debit_item(self, children):
        return {"type": "debit", "name": str(children[0]).strip(), "amount": str(children[1])}

    def credit_item(self, children):
        return {"type": "credit", "name": str(children[0]).strip(), "amount": str(children[1])}

    def summary(self, children):
        return str(children[0])


