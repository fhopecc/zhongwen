import re
小寫數字表 = "零一二三四五六七八九"
大寫數字表 = "零壹貳參肆伍陸柒捌玖"
大写数字表 = "零壹贰叁肆伍陆柒捌玖"
大寫位名表 = "拾佰仟"
小寫位名表 = "十百千"
組名表 = "萬億兆京垓秭穰溝澗正載"
组名表 = "万亿兆京垓秭穰沟涧正载"

def 中文數字(
    n: int | float | str,
    大寫: bool = False,
    簡體: bool = False,
    異體零: bool = False,
    兩: bool = False
) -> str:
    # system = NumberingSystem(numbering_type)
    位名表 = 大寫位名表 if 大寫 else 小寫位名表
    _組名表 = 组名表 if 簡體 else 組名表
    數字表 = 大寫數字表 if 大寫 else 小寫數字表 
    數字表 = 大写数字表 if 大寫 and 簡體 else 數字表 
    數字表 = re.sub('二', '兩', 數字表) if 兩 else 數字表 
    點 =  '点' if 簡體 else '點' 
    
    n:str = str(n)
    i:str = n
    d = ""

    if "." in n:
        i, d= n.split(".", 1)
        d = d.rstrip("0")
    cn = ''
    i = list(reversed(i))

    def 轉中文數字(i):
        cn = ''
        for pos, digit in enumerate(i):
        # breakpoint()
            位名 = ""
            if digit != '0' and pos > 0:
                位名 = 位名表[pos-1]
            cn = 數字表[int(digit)] + 位名 + cn
        return cn

    for pos, 一組阿拉伯數字 in enumerate([i[idx:idx + 4] for idx in range(0, len(i), 4)]):
        _cn = 轉中文數字(一組阿拉伯數字)
        if pos > 0: 
            _cn = _cn + _組名表[pos-1]
        cn = _cn + cn 


    #一萬零六百零零 -> 一萬零六百
    cn = re.sub('零+$', '', cn)
    #一十六 -> 十六
    cn = re.sub('^一十', '十', cn)
    #一千六百 -> 一千六
    cn = re.sub(f'(千[{數字表}])百$', r'\1', cn)
    #一百一十 -> 一百一
    cn = re.sub(f'(百[{數字表}])十$', r'\1', cn)
    if d != "":
        cn += 點 + d.translate(str.maketrans('0123456789', 數字表))
    return cn    

    result_symbols = get_value(int_string)
    # Remove last 0 for number larger than 10
    if (len(result_symbols) > 1) and (getattr(result_symbols[-1], "int_value", None) == 0):
        result_symbols = result_symbols[:-1]

    # Remove leading 0 for non-zero numbers
    if (len(result_symbols) > 1) and (getattr(result_symbols[0], "int_value", None) == 0):
        result_symbols = result_symbols[1:]

    dec_symbols = [system.digits[int(c)] for c in dec_string]

    if "." in num_str:
        result_symbols += [system.math.point] + dec_symbols  # type: ignore

    if alt_two:
        liang = ChineseNumberDigit(
            2,
            system.digits[2].alt_s,
            system.digits[2].alt_t,
            system.digits[2].capital_simplified,
            system.digits[2].capital_traditional,
        )
        for i, v in enumerate(result_symbols):
            if not isinstance(v, ChineseNumberDigit):
                continue
            if v.int_value != 2:
                continue
            next_symbol = result_symbols[i + 1] if i < len(result_symbols) - 1 else None
            if not isinstance(next_symbol, ChineseNumberUnit):
                continue
            if next_symbol.power > 1:
                result_symbols[i] = liang

    # if capitalize is True, '两' will not be used and `alt_two` has no impact on output
    if traditional:
        attr_name = "traditional"
    else:
        attr_name = "simplified"

    if capitalize:
        attr_name = "capital_" + attr_name

    # remove trailing units, 1600 -> 一千六, 10600 -> 一萬零六百, 101600 -> 十萬一千六
    if len(result_symbols) > 3 and isinstance(result_symbols[-1], ChineseNumberUnit):
        if getattr(result_symbols[::-1][2], "power", None) == (result_symbols[-1].power + 1):
            result_symbols = result_symbols[:-1]

    result = "".join([getattr(s, attr_name) for s in result_symbols])

    for p in POINT:
        if not result.startswith(p):
            continue
        result = CHINESE_DIGITS[0] + result
        break

    if alt_zero:
        result = result.replace(getattr(system.digits[0], attr_name), system.digits[0].alt_s)

    return result
def 中文数字(n):
    return 中文數字(n, 簡體=True)
