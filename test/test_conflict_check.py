import pytest
import pandas
from pandas.testing import assert_frame_equal

from packages.conflict_check import ConflictChecker
from packages.assignment import sku_attribute_mapping

@pytest.fixture
def sample_attributes():
    sample = pandas.DataFrame(
        [
            [1, 'Red', 1, 'Red', 25], [1, 'Blue', 2, 'Blue', 26],
            [1, 'Black', 3, 'Black', 27], [1, 'White', 4, 'White', 28],
            [1, 'Violet', 5, 'Violet', 29],
            [1, 'Pacific-Blue', 6, 'Pacific-Blue', 30],
            [1, 'Yellow', 7, 'Yellow', 31]
        ], columns=['Attribute.id', 'AttributeValue.backendName',
                    'AttributeValue.position', 'AttributeValueName.name',
                    'AttributeValue.id']
    )

    return sample

@pytest.fixture
def sample_flatfile():
    sample = pandas.DataFrame(
        [
            ['1234x', '1234567891011', 'EAN', 'Blue',
             'blue', 'M', 'Cotton', 'Medium', '1230x'],
            ['1235x', '1234567891012', 'EAN', 'Blue',
             'blue', 'L', 'Cotton', 'Large', '1230x'],
            ['1236x', '1234567891013', 'EAN', 'Blue',
             'blue', 'XL', 'Cotton', 'X-Large', '1230x'],
            ['2345x', '1234567891014', 'EAN', 'Red',
             'red', 'M', 'Cotton', 'Medium', '2340x'],
            ['2346x', '1234567891015', 'EAN', 'Red',
             'red', 'L', 'Cotton', 'Large', '2340x'],
            ['3456x', '1234567891016', 'EAN', 'Yellow',
             'yellow', 'M', 'Cotton', 'Medium', '3450x'],
            ['4567x', '1234567891017', 'EAN', 'Deep-Blue',
             'blue', 'M', 'Cotton', 'Medium', '4560x'],
            ['4568x', '1234567891018', 'EAN', 'Deep-Blue',
             'blue', 'L', 'Cotton', 'Large', '4560x'],
            ['4569x', '1234567891019', 'EAN', 'Deep-Blue',
             'blue', 'XL', 'Cotton', 'X-Large', '4560x'],
            ['5678x', '0234567891010', 'EAN', 'Black',
             'black', 'M', 'Cotton', 'Medium', '5670x'],
            ['6789x', '0234567891011', 'EAN', 'Pacific-Blue',
             'blue', 'M', 'Cotton', 'Medium', '6780x'],
            ['7891x', '0234567891012', 'EAN', 'Pitch-Black',
             'black', 'M', 'Cotton', 'Medium', '7890x'],
            ['8911x', '0234567891013', 'EAN', 'Pink',
             'pink', 'L', 'Cotton', 'Medium', '8910x']
        ], columns = ['item_sku', 'external_product_id',
                      'external_product_id_type', 'color_name',
                      'color_map', 'size_name', 'material_type',
                      'size_map', 'parent_sku']
    )

    return sample

@pytest.fixture
def sample_mapfile():
    sample = pandas.DataFrame(
        [
            [0, 'color_name:Blue,size_name:M', '1234567891011'],
            [0, 'color_name:Blue,size_name:L', '1234567891012'],
            [0, 'color_name:Blue,size_name:XL', '1234567891013'],
            [0, 'color_name:Red,size_name:M', '1234567891014'],
            [0, 'color_name:Red,size_name:L', '1234567891015'],
            [0, 'color_name:Yellow,size_name:M', '1234567891016'],
            [0, 'color_name:Blue,size_name:M', '1234567891017'],
            [0, 'color_name:Blue,size_name:L', '1234567891018'],
            [0, 'color_name:Blue,size_name:XL', '1234567891019'],
            [0, 'color_name:Black,size_name:M', '0234567891010'],
            [0, 'color_name:Pacific-Blue,size_name:M', '0234567891011'],
            [0, 'color_name:Black,size_name:M', '0234567891012']
        ], columns=['Variation.isMain',
                    'VariationAttributeValues.attributeValues',
                    'VariationBarcode.code']
    )

    return sample

@pytest.fixture
def sample_checker(sample_attributes, sample_flatfile, sample_mapfile):
    checker = ConflictChecker(attributes=sample_attributes,
                              translation=sample_flatfile,
                              mapping=sample_mapfile)
    return checker

@pytest.fixture
def map_df(sample_checker):
    data = {
        'connect': sample_checker.mapping,
        'translation': sample_checker.translation,
        'attribute': sample_checker.attributes
    }
    return sku_attribute_mapping(data)

def test_detect_color_collision(sample_checker):
    expect = pandas.DataFrame(
        [
            [26, 'Blue', ['Blue', 'Deep-Blue'],
             ['1234x','1235x','1236x', '4567x', '4568x', '4569x']],
            [27, 'Black', ['Black', 'Pitch-Black'],['5678x', '7891x']]
        ], columns=['AttributeValue.id', 'AttributeValueName.name', 'upload_values',
                    'collisions']
    )

    result = sample_checker.detect_color_collision()

    assert_frame_equal(expect, result)

def test_get_attribute_users(sample_checker, map_df):
    expect = [
        ['2345x', '2346x'],
        ['1234x','1235x','1236x', '4567x', '4568x', '4569x'],
        ['5678x', '7891x'], [], [], ['6789x'], ['3456x']]
    attributes = [25, 26, 27, 28, 29, 30, 31]

    for index, attr in enumerate(attributes):
        result = sample_checker.get_attribute_users(map_df=map_df,
                                                    attribute=attr)
        assert expect[index] == result

def test_fill_up_barcode(sample_checker):
    new = ['1234567891011', '0753456789101', '753456789101', '123', '',
          '123456789101112']
    expect = ['1234567891011', '0753456789101', '0753456789101', '123', '',
          '123456789101112']
    for index, ean in enumerate(new):
        result = sample_checker._ConflictChecker__fill_up_barcode(ean)
        assert expect[index] == result

def test_get_amount_of_user_parents(sample_checker):
    new = [['1234x', '1235x'], ['2345x'], ['5678x', '7891x', '6789x'], [],
           ['1111x'], ['1234x', '0010x', '3456x'], ['1230x']]
    expect = [1, 1, 3, 0, 0, 2, 0]

    for index, user in enumerate(new):
        result = sample_checker._ConflictChecker__get_amount_of_user_parents(user=user)
        assert expect[index] == result

def test_get_new_attribute_values(sample_checker):
    new = [['1234x', '1235x', '2345x', '3456x'], ['5678x', '7891x'],
           ['1111x', '1236x'], ['0', '']]
    expect = [['Blue', 'Red', 'Yellow'], ['Black', 'Pitch-Black'],
              ['NOT FOUND', 'Blue'], ['NOT FOUND']]

    for index, user in enumerate(new):
        result = sample_checker._ConflictChecker__get_new_attribute_values(
            user=user, key='color_name')
        assert expect[index] == result
