市縣 = ["臺北市" ,"新北市" ,"桃園市" ,"臺中市" ,"臺南市" ,"高雄市"
,"基隆市" ,"宜蘭縣" ,"新竹縣" ,"新竹市" ,"苗栗縣" ,"彰化縣" ,"南投縣"
,"雲林縣" ,"嘉義縣" ,"嘉義市" ,"屏東縣" ,"花蓮縣" ,"臺東縣" ,"澎湖縣"
,"金門縣" ,"連江縣"]

def 取歸屬市縣(名稱, 排除市縣='宜蘭縣'):
    應彙整市縣 = set(市縣) - set(排除市縣)
    for n in list(應彙整市縣):
        if n in 名稱:
            return n
    if '桃' in 名稱:
        if not '桃園市' in 排除市縣: return '桃園市'
    if '高雄' in 名稱:
        if not '高雄市' in 排除市縣: return '高雄市'
    if '基' in 名稱:
        if not '基隆市' in 排除市縣: return '基隆市'
    if '竹縣' in 名稱:
        if not '新竹縣' in 排除市縣: return '新竹縣'
    if '竹市' in 名稱:
        if not '新竹市' in 排除市縣: return '新竹市'
    if '苗' in 名稱:
        if not '苗栗縣' in 排除市縣: return '苗栗縣'
    if '彰' in 名稱:
        if not '彰化縣' in 排除市縣: return '彰化縣'
    if '雲林' in 名稱:
        if not '雲林縣' in 排除市縣: return '雲林縣'
    if '嘉市' in 名稱:
        if not '嘉義市' in 排除市縣: return '嘉義市'
    if '花' in 名稱:
        if not '花蓮縣' in 排除市縣: return '花蓮縣'
    if '澎' in 名稱:
        if not '澎湖縣' in 排除市縣: return '澎湖縣'

def 未回覆市縣(回覆文件目錄, 排除市縣='宜蘭縣'):
    from collections.abc import Iterable 
    if isinstance(排除市縣, str) or not isinstance(排除市縣, Iterable):
        排除市縣 = [排除市縣]
    已回覆市縣 = []
    for fn in 回覆文件目錄.glob("*"):
        回覆市縣 = 取歸屬市縣(fn.stem, 排除市縣=排除市縣)
        if 回覆市縣:
            已回覆市縣.append(回覆市縣)
    未回覆市縣 = set(市縣) - set(已回覆市縣)
    未回覆市縣 -= set(排除市縣)
    return 未回覆市縣

if __name__ == '__main__':
    from pathlib import Path
    print(未回覆市縣(Path(__file__).parent))
