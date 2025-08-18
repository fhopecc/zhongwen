from zhongwen.text import 刪空格, 轉樣式表字串

def geturl(文):
    '找出文中的 url，如找不到傳回空白'
    import re

    # 這個正規表達式能匹配大多數常見的 URL 格式
    # 它可以處理 http/https，以及網址結尾的各種符號
    # `[a-zA-Z0-9-.]` 處理域名中的字元
    # `[^\s()<>]+` 處理路徑中的字元，並排除括號
    url_pattern = re.compile(r'https?://[a-zA-Z0-9-.]+(?:/[^\s()<>]+|)')

    # 使用 findall 方法找出所有符合模式的 URL
    urls = url_pattern.findall(文)

    if urls:
        for url in urls:
            return url
    else:
        return ''

def 刪除空行(文):
    return "\n".join(line for line in 文.splitlines() if line.strip())

def 刪除中文字間空白(文):
    import re
    new_text = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', '', 文)
    return new_text

def 臚列(項目):
    "['甲', '乙', '丙'] -> '甲、乙及丙'"
    項目 = [str(i) for i in 項目]
    if type(項目) == list:
        if len(項目) > 1:
            return f"{'、'.join(項目[:-1])}及{項目[-1]}" if len(項目) else ''
        return 項目[0]
    return 項目

def 刪除末尾句號(字串):
    from zhongwen.text import 去除字串末句號
    return 去除字串末句號(字串)

def 隨機中文(最大字串長度):
    import random 
    return ''.join(chr(random.randint(0x4E00, 0x9FA5)) 
              for _ in range(random.randint(1, 最大字串長度)))


def 臚列標題(文, 級別=3) -> str:
    """### 標題甲\n### 標題乙 -> 1.標題甲；2.標題乙
    """
    from zhongwen.數 import 取中文數字
    import re
    
    pattern = re.compile(rf'^{"#" * 級別}\s+(.+)$')
    lines = 文.splitlines()
    
    results = []
    counter = 1
    
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            numbered = f"({取中文數字(counter)}){match.group(1)}"
            results.append(numbered)
            counter += 1
    
    return '；'.join(results)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="提取 Markdown 标题并添加数字序号")
    parser.add_argument("file", help="Markdown 文件路径")
    parser.add_argument("-l", "--level", type=int, default=3, 
                       help="标题级别 (1-6)，默认为3")
    parser.add_argument("-s", "--separator", default="；",
                       help="输出分隔符，默认为中文分号")
    parser.add_argument("-n", "--no-space", action="store_true",
                       help="序号后不加空格 (1.标题)")
    
    args = parser.parse_args()
    
    try:
        result = extract_and_number_headers(
            args.file,
            level=args.level,
            output_separator=args.separator
        )
        
        # 处理不加空格的情况
        if args.no_space:
            result = result.replace(". ", ".")
        
        print(result)
    except Exception as e:
        print(f"错误: {e}")


