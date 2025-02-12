from zhongwen.text import 刪空格, 臚列, 轉樣式表字串
def 隨機中文(最大字串長度):
    import random 
    return ''.join(chr(random.randint(0x4E00, 0x9FA5)) 
              for _ in range(random.randint(1, 最大字串長度)))

def 刪除末尾句號(字串):
    from zhongwen.text import 去除字串末句號
    return 去除字串末句號(字串)
