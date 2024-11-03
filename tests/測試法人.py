import unittest

class Test(unittest.TestCase):
    def test(self):
        from zhongwen.法人 import 取學校簡稱, 取分校簡稱
        self.assertEqual(取學校簡稱('宜蘭縣立宜蘭國民中學'), '宜蘭國中')
        self.assertEqual(取學校簡稱('宜蘭縣立岳明國民中小學'), '岳明國中小')
        self.assertEqual(取學校簡稱('宜蘭縣立內城國民中小學化育分校'), '內城國中小化育分校')
        self.assertEqual(取學校簡稱('宜蘭縣縣立南澳高中'), '南澳高中')
        self.assertEqual(取學校簡稱('人文國民中小學'), '人文國中小')
        self.assertEqual(取分校簡稱('龍潭國小匏崙分校'), '匏崙分校') 

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('googleclient').setLevel(logging.CRITICAL)
    logging.getLogger('matplotlib').setLevel(logging.CRITICAL)
    logging.getLogger('faker').setLevel(logging.CRITICAL)
    unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Test('test'))  # 指定測試
    unittest.TextTestRunner().run(suite)
