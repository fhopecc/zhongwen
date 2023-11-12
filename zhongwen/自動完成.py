def 同字首詞(字首, 字典):
    from pygtrie import PrefixSet
    from zhongwen.text import 是否為字元
    trie = PrefixSet(字典)
    suggests = []
    comps = []
    for i in range(0, len(字首)):
        prefix = 字首[-1*i-1:]
        if not 是否為字元(prefix[0]): 
            break
        s = [''.join(k) for k in trie.iter(prefix)]
        suggests = s+suggests
        comps = [c[len(prefix):] for c in s] + comps
    return [{'word':word, 'abbr':abbr, 'kind':'K'} for (word, abbr) in zip(comps, suggests)]


