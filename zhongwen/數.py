from zhongwen.number import 半型數字表, 全型數字表, 小寫數字表, 小寫位名表
from zhongwen.number import 大寫數字表, 大写数字表, 大寫位名表, 組名表, 组名表
from zhongwen.number import 最簡約數
全數字表  = 半型數字表 + 全型數字表 + 小寫數字表 + 小寫位名表
全數字表 += 大寫數字表 + 大写数字表 + 大寫位名表 + 組名表 + 组名表

def 取數值(n):
    from zhongwen.number import 轉數值
    return 轉數值(n)
    # pat = f'[{全數字表}]+'
    # if ms:=re.search(pat, n):
        # return m[1]
    # return n
