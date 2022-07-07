import unittest

class Test(unittest.TestCase):
    
    def test(self):
        from chinese import 中文數字

        self.assertEqual(中文數字(3.4, 簡體=True), '三点四')
        self.assertEqual(中文數字(182.1, 簡體=True), '一百八十二点一')
        self.assertEqual(中文數字(16), '十六')
        self.assertEqual(中文數字(10600, 簡體=True), '一万零六百')
        self.assertEqual(中文數字(1600), '一千六')
        self.assertEqual(中文數字(110), '一百一')
       

        """
    >>> num2cn('023232.005184132423423423300', numbering_type="high", alt_two=True, capitalize=False, traditional=True)
    '兩萬三仟兩佰三拾二點零零五一八四一三二四二三四二三四二三三'
    >>> num2cn('023232.005184132423423423300', numbering_type="high", alt_two=False, capitalize=False, traditional=True)
    '二萬三仟二佰三拾二點零零五一八四一三二四二三四二三四二三三'
    >>> num2cn(111180000)
    '一亿一千一百一十八万'
    >>> num2cn(1821010)
    '一百八十二万一千零一十'
    """


if __name__ == '__main__':
    unittest.main()
