import unittest
import openfile as ofile


class TestOpenFile(unittest.TestCase):

    def setUp(self):
        self.test_string = 'color:red,size_name:M'
        self.test_string_only_color = 'color:red'
        self.test_string_only_size = 'size:M'

    def test_parseColorValue(self):
        print('test parseColorValue')
        color = 'red'
        self.assertEqual(ofile.parseColorValue(self.test_string), color)
        self.assertEqual(ofile.parseColorValue(self.test_string_only_size),
                         None)

    def test_parseSizeValue(self):
        print('test parseSizeValue')
        size = 'M'
        self.assertEqual(ofile.parseSizeValue(self.test_string), size)
        self.assertEqual(ofile.parseSizeValue(self.test_string_only_color),
                         None)

    def test_findIdForValue(self):
        print('test findIdForValue')
        row = {
                'Attribute.id': '1',
                'AttributeValue.backendName': 'red',
                'AttributeValue.position': '1',
                'AttributeValueName.name': 'red',
                'AttributeValue.id': '9'
        }
        value = 'red'

        self.assertTrue(ofile.findIdForValue(value=value, row=row))
        self.assertFalse(ofile.findIdForValue(value='blue', row=row))

    def test_ColorTranslateValue(self):
        print('test ColorTranslateValue')
        row = {'item_sku': 'test1', 'color_name': 'red'}
        self.assertEqual('red', ofile.ColorTranslateValue(variation='test1',
                                                          row=row))
        self.assertEqual(None, ofile.ColorTranslateValue(variation='false1',
                                                         row=row))

    def test_SizeTranslateValue(self):
        print('test SizeTranslateValue')
        row = {'item_sku': 'test1', 'size_name': 'M'}
        self.assertEqual('M', ofile.SizeTranslateValue(variation='test1',
                                                        row=row))
        self.assertEqual(None, ofile.SizeTranslateValue(variation='false1',
                                                         row=row))


if __name__ == '__main__':
    unittest.main()
