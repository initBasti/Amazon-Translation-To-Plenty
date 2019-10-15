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
        test_dict = dict()
        result_dict_1 = {'id': '9', 'backend': 'red'}
        result_dict_2 = {'id': None, 'backend': None}

        test_dict = ofile.findIdForValue(value=value, row=row)
        self.assertDictEqual(test_dict, result_dict_1)
        test_dict = ofile.findIdForValue(value='blue', row=row)
        self.assertDictEqual(test_dict, result_dict_2)

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

    def test_find_duplicates(self):
        print('test find_duplicates')
        test_dict = {
            'test1': {'color_value': 'rot', 'color_id': 10,
                      'color_value_translation': 'red'},
            'test2': {'color_value': 'blau', 'color_id': 11,
                      'color_value_translation': 'blue'},
            'test3': {'color_value': 'gruen', 'color_id': 12,
                      'color_value_translation': 'green'},
            'test4': {'color_value': 'rot', 'color_id': 14,
                      'color_value_translation': 'red1'},
            'test5': {'color_value': 'rot1', 'color_id': 10,
                      'color_value_translation': 'red12'},
            'test6': {'color_value': 'rot13', 'color_id': 15,
                      'color_value_translation': 'red'}
        }
        good_result = ['test1', 'test2', 'test3']

        new_dict = ofile.find_duplicates(test_dict)

        self.assertListEqual([*new_dict], good_result)


if __name__ == '__main__':
    unittest.main()
