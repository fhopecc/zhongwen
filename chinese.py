import re
小寫數字表 = "零一二三四五六七八九"
大寫數字表 = "零壹贰叁肆伍陆柒捌玖"
簡體大寫數字 = "零壹贰叁肆伍陆柒捌玖"
大寫位名 = "拾佰仟萬" # 10^1, 10^2, 10^3, 10^4.
小寫位名表 = "十百千萬" # 10^1, 10^2, 10^3, 10^4.
簡體小寫位名表 = "十百千万"
大位名 = "億兆京垓秭穰溝澗正載"
簡體大位名 = "亿兆京垓秭穰沟涧正载"

def 中文數字(
    n: int | float | str,
    大寫: bool = False,
    簡體: bool = False,
    異體零: bool = False,
    異體二: bool = False
) -> str:
    # system = NumberingSystem(numbering_type)
    位名表 = 小寫位名表
    數字表 = 小寫數字表
    點 = '點'

    if 簡體:
        位名表 = 簡體小寫位名表
        點 = '点'

    n:str = str(n)
    i:str = n
    d = ""

    if "." in n:
        i, d= n.split(".", 1)
        d = d.rstrip("0")
    cn = ''

    for pos, digit in enumerate(reversed(i)):
        # breakpoint()
        位名 = ""
        if digit != '0' and pos > 0:
            位名 = 位名表[pos-1]

        cn = 數字表[int(digit)] + 位名 + cn

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
