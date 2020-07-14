import packages.assignment as assign
import collections


class ConflictChecker():
    def __init__(self, attributes, translation, mapping):
        self.attributes = attributes
        self.translation = translation
        self.mapping = mapping

    def __fill_up_barcode(self, barcode):
        """
            Used for special cases, were a UPC was used as an EAN
            and the number was prepended with an '0'.
            In that case we have to make sure that the length of
            the number is correct.

            Parameter:
                barcode [String] : barcode as a string

            Return:
                [String] : Either the correct barcode returned
                           without modification or a wrong barcode
                           preceded by '0'
        """
        if len(str(barcode)) == 12:
            return '0' + str(barcode)
        return str(barcode)

    def get_attribute_users(self, map_df, attribute):
        """
            Get a list of parent variation numbers, where any child
            variation uses the particular attribute ID.

            Parameter:
                attribute [Integer] : The ID of an attribute value from
                                      Plentymarkets.

            Return:
                [List] : sorted list of parent variation numbers.
        """
        result = set()

        filtered = map_df[map_df['attribute_id'] == attribute]
        if len(filtered.index) == 0:
            return []
        filtered = filtered.astype({'external_product_id': object})

        ean = filtered['external_product_id']
        ean = ean.apply(lambda x: self.__fill_up_barcode(x))

        for code in ean.values:
            mask = self.translation['external_product_id'] == code
            result.add(self.translation[mask]['item_sku'].values[0])
        return list(sorted(result))

    def __get_amount_of_user_parents(self, user):
        """
            Check how many parent articles the variations come from.

            Parameter:
                user [List] : A list of child variation numbers

            Return:
                [Integer] Amount of detected parents
        """
        parents = set()

        trans = self.translation
        for i in user:
            parent = trans[trans['item_sku'] == i]['parent_sku'].values
            if len(parent) != 0:
                parents.add(parent[0])

        return len(parents)

    def __get_new_attribute_values(self, user, key):
        """
            Fetch the values for a specific attribute, for each user
            variation of the attribute id.

            Parameter:
                user [List] : A list of child variation numbers
                key [String]: Amazon flatfile column name of the attribute

            Return:
                [List] List of attribute values in the same order as the users.
        """
        attr = collections.OrderedDict()

        trans = self.translation
        for i in user:
            color = trans[trans['item_sku'] == i][key].values
            if len(color) != 0:
                attr[color[0]] = None
                continue
            attr['NOT FOUND'] = None

        return list(attr.keys())

    def detect_color_collision(self):
        """
            For each attribute that is used by multiple parent variations.
            Create a dataframe, that contains each attribute together with
            the values saved on Plentymarkets, the values provided by the
            Translation file and the users of the attribute.

            Return:
                [DataFrame]
        """
        data = {
            'connect': self.mapping,
            'translation': self.translation,
            'attribute': self.attributes
        }
        map_df = assign.sku_attribute_mapping(data)

        attr = self.attributes
        attr['collisions'] = attr['AttributeValue.id'].apply(
            lambda x: self.get_attribute_users(map_df=map_df, attribute=x))
        attr['amount_parents'] = attr['collisions'].apply(
            lambda x: self.__get_amount_of_user_parents(user=x)
        )
        attr = attr[attr['amount_parents'] > 1]
        attr['upload_values']  = attr['collisions'].apply(
            lambda x: self.__get_new_attribute_values(user=x, key='color_name')
        )
        collision = attr[['AttributeValue.id', 'AttributeValueName.name',\
                          'upload_values', 'collisions']]
        collision = collision.reset_index(drop=True)
        return collision
