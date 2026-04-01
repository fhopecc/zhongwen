from lark import Transformer

def 取日記帳紀錄(交易):
    '''
    一、日記帳交易紀錄：日期、科目、備註、借、貸。
    二、交易紀錄借貸不平衡會引發錯誤。    
    '''
    from lark import Lark
    正規交易 = 補全簡寫交易(交易)
    parser = Lark(accounting_grammar, parser='earley')
    transformer = AccountingTransformer()
    parsed_data = transformer.transform(parser.parse(正規交易))
    final_list = transform_and_validate(parsed_data)
    return final_list
         

def 補全簡寫交易(簡寫交易):
    """
    一、將簡寫敘述轉換為標準會計敘述格式
    二、範例：昨借新光優利貸利息20元 -> 115.3.31借新光優利20元貸利息20元
    三、昨 (T-1), 前 (T-2), 大前 (T-3)
    """
    import re
    from datetime import datetime, timedelta
    raw_text = 簡寫交易
    today = datetime.now()
    roc_year_offset = 1911
    current_roc_year = today.year - roc_year_offset
    
    # --- 1. 摘要切分 ---
    if "，" in raw_text:
        main_part, summary_part = raw_text.split("，", 1)
        summary_part = "，" + summary_part
    else:
        main_part = raw_text
        summary_part = "，無"

    # --- 2. 日期補全 ---
    date_str = ""
    content = main_part.replace(" ", "") # 移除空格防止干擾
    
    date_mapping = {"昨": 1, "前": 2, "大前": 3}
    for keyword, days_back in date_mapping.items():
        if content.startswith(keyword):
            target_date = today - timedelta(days=days_back)
            date_str = f"{target_date.year - roc_year_offset}.{target_date.month}.{target_date.day}"
            content = content[len(keyword):]
            break
            
    if not date_str:
        m_d = re.match(r"^(\d+\.\d+)(?=借)", content)
        if m_d:
            date_str = f"{current_roc_year}.{m_d.group(1)}"
            content = content[len(m_d.group(1)):]
        else:
            d_only = re.match(r"^(\d+)(?=借)", content)
            if d_only:
                date_str = f"{current_roc_year}.{today.month}.{d_only.group(1)}"
                content = content[len(d_only.group(1)):]

    if not date_str and content.startswith("借"):
        date_str = f"{current_roc_year}.{today.month}.{today.day}"

    # --- 3. 智慧補全邏輯 (修正重複補元的問題) ---
    
    # A. 針對「一對一共用金額」：借A貸B 20元 -> 借A 20元 貸B 20元
    # 判斷標準：字串裡只有一個「元」字，且位於結尾
    if content.count("元") == 1 and content.endswith("元"):
        one_on_one_pattern = r"^借(.+?)貸(.+?)(\d+)元$"
        match = re.search(one_on_one_pattern, content)
        if match:
            sub_debit = match.group(1)
            sub_credit = match.group(2)
            amount = match.group(3)
            content = f"借{sub_debit}{amount}元貸{sub_credit}{amount}元"
            return f"{date_str}{content}{summary_part}"

    # B. 針對多借多貸或標準格式：補齊漏掉的「元」
    # 修正重點：使用負向預覽 (?!元)，只有當數字後面「不是元」才補
    # 並且確保匹配範圍不跨越下一個「借」或「貸」
    content = re.sub(r"([借貸][^借貸元]+?)(\d+)(?!元)(?=[借貸]|$)", r"\1\2元", content)
    
    return f"{date_str}{content}{summary_part}"

# --- 1. 定義 Lark 語法 (同前述版本) ---
accounting_grammar = r"""
    start: date items summary

    date: YEAR "." MONTH "." DAY
    items: (debit_item | credit_item)+
    
    debit_item: "借" NAME AMOUNT "元"
    credit_item: "貸" NAME AMOUNT "元"
    
    # 強制要求：逗號後面的所有內容皆為摘要
    summary: "，" SUMMARY_CONTENT
    
    YEAR: /\d+/
    MONTH: /\d+/
    DAY: /\d+/
    AMOUNT: /\d+/
    
    # 科目名稱：匹配直到遇見「數字+元」
    NAME: /.+?(?=\d+元)/
    
    # 摘要內容：匹配剩餘所有字元
    SUMMARY_CONTENT: /.+/

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
        from zhongwen.時 import 取日期
        return 取日期(f"{children[0]}.{children[1]}.{children[2]}")

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

