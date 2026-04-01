from lark import Transformer

def 取日記帳紀錄(交易紀錄):
    '''
    一、日記帳交易紀錄：日期、科目、備註、借、貸。
    二、交易紀錄借貸不平衡會引發錯誤。    
    '''
    from lark import Lark
    parser = Lark(accounting_grammar, parser='earley')
    transformer = AccountingTransformer()
    parsed_data = transformer.transform(parser.parse(交易紀錄))
    final_list = transform_and_validate(parsed_data)
    return final_list
         

# --- 1. 定義 Lark 語法 (同前述版本) ---
accounting_grammar = r"""
    start: date items summary
    date: YEAR "." MONTH "." DAY
    items: (debit_item | credit_item)+
    debit_item: "借" NAME AMOUNT "元"
    credit_item: "貸" NAME AMOUNT "元"
    summary: "，" ANY_TEXT
    YEAR: /\d+/
    MONTH: /\d+/
    DAY: /\d+/
    AMOUNT: /\d+/
    NAME: /.+?(?=\d+元)/
    ANY_TEXT: /.+/
    %import common.WS
    %ignore WS
"""

class AccountingTransformer(Transformer):
    def start(self, children):
        res = {"date": children[0], "debit": [], "credit": [], "summary": children[2]}
        for item in children[1]:
            if item['type'] == 'debit':
                res["debit"].append(item)
            else:
                res["credit"].append(item)
        return res

    def date(self, children):
        return f"{children[0]}.{children[1]}.{children[2]}"

    def items(self, children):
        return children

    def debit_item(self, children):
        return {"type": "debit", "name": str(children[0]).strip(), "amount": int(children[1])}

    def credit_item(self, children):
        return {"type": "credit", "name": str(children[0]).strip(), "amount": int(children[1])}

    def summary(self, children):
        return str(children[0])

# --- 2. 轉換與檢核函數 ---
def transform_and_validate(result_dict):
    output = []
    date = result_dict['date']
    summary = result_dict['summary']
    
    total_debit = 0
    total_credit = 0

    # 處理借方
    for item in result_dict['debit']:
        amt = item['amount']
        total_debit += amt
        output.append([date, item['name'], summary, amt, 0])
        
    # 處理貸方
    for item in result_dict['credit']:
        amt = item['amount']
        total_credit += amt
        output.append([date, item['name'], summary, 0, amt])

    # --- 檢核邏輯 ---
    if total_debit != total_credit:
        # 你可以選擇拋出異常 (Exception) 或回傳錯誤訊息
        raise ValueError(f"【分錄不平衡】借方總額：{total_debit} / 貸方總額：{total_credit} (差額：{total_debit - total_credit})")
    
    return output

