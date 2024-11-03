def 取學校簡稱(學校名稱):
    import re
    s = 學校名稱
    if s == '宜蘭縣立慈心華德福教育實驗高級中等學校':
        return '慈心華德福實驗高中'
    if s == '慈心高中':
        return '慈心華德福實驗高中'
    if s == '慈心華德福高中':
        return '慈心華德福實驗高中'
    if s == '慈心華德福國小':
        return '慈心華德福實驗高中'
    if s == '慈心華德福':
        return '慈心華德福實驗高中'
    n = s
    pat = r'(.+縣立|.+縣.+[鄉鎮市])(.+)(高中|(國民(中|小|中小)學))(.+分[校班])?'
    if m:=re.match(pat, s):
        n = f'{m[2]}{m[3]}{m[6] if m[6] else ""}'
    n = n.replace('國民中學', '國中').replace('國民小學', '國小')
    n = n.replace('國民中小學', '國中小')
    return n

def 取分校簡稱(學校名稱):
    import re
    s = 學校名稱
    pat = r'.+國小(.+)(分[校班])'
    if m:=re.match(pat, s):
        return m[1] + m[2]
    return s
