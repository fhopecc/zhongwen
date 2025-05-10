from zhongwen.text import 刪空格, 轉樣式表字串

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
