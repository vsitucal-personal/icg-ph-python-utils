from decimal import Decimal
from boto3.dynamodb.types import TypeDeserializer
from boto3.dynamodb.types import TypeSerializer


class DBTypes:
    """
    Contains DB utility methods
    """

    @staticmethod
    def convert_db_dict_to_generic_item(db_item: dict) -> dict:
        """
        Converts a ddb-formatted dict to its python equivalent
        :param db_item: Data to be converted
        :return: dict containing python-formatted data
        """
        deserializer = TypeDeserializer()
        deserialized_dict = {k: deserializer.deserialize(v) for k, v in db_item.items()}
        item = DBTypes.__replace_decimal(deserialized_dict)
        return item

    @staticmethod
    def convert_db_list_to_generic_item(db_list: list) -> list:
        """
        Converts a ddb-formatted list to its python equivalent
        :param db_list: Data to be converted
        :return: list containing python-formatted data
        """

        generic_list = []

        for item in db_list:
            if isinstance(item, dict) and item:
                generic_list.append(DBTypes.convert_db_dict_to_generic_item(item))
            elif isinstance(item, Decimal):
                generic_list.append(DBTypes.__replace_decimal(item))
            elif isinstance(item, list) and list:
                generic_list.append(DBTypes.convert_db_list_to_generic_item(item))
            else:
                generic_list.append(item)

        return generic_list

    @staticmethod
    def convert_dict_to_db_item(generic_info: dict) -> dict:
        """
        Converts a python dict to its ddb equivalent format
        :param generic_info: Data to be converted
        :return: dict containing ddb-formatted data
        """

        serializer = TypeSerializer()
        serialized_dict = {}

        for k, v in generic_info.items():
            if isinstance(v, float):
                serialized_dict[k] = {'N': str(v)}
            elif isinstance(v, dict) and v:
                serialized_dict[k] = {'M': DBTypes.convert_dict_to_db_item(v)}
            else:
                serialized_dict[k] = serializer.serialize(v)

        return serialized_dict

    @staticmethod
    def convert_list_to_db_item(generic_list: list) -> list:
        """
        Converts a python list to its ddb equivalent format
        :param generic_list: Data to be converted
        :return: list containing ddb-formatted data
        """
        db_item_list = []

        for item in generic_list:
            if isinstance(item, dict) and item:
                db_item_list.append(DBTypes.convert_dict_to_db_item(generic_info=item))
            elif isinstance(item, float):
                db_item_list.append(Decimal(str(item)))
            elif isinstance(item, list) and item:
                db_item_list.append(DBTypes.convert_list_to_db_item(generic_list=item))
            else:
                db_item_list.append(item)

        return db_item_list

    @staticmethod
    def __replace_decimal(obj):
        """
        Replaces decimal into int or float

        :param obj: dictionary
        :return: dictionary with replaced decimal value
        """
        if isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = DBTypes.__replace_decimal(obj[i])
            return obj
        elif isinstance(obj, dict):
            for k in obj.keys():
                obj[k] = DBTypes.__replace_decimal(obj[k])
            return obj
        elif isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        else:
            return obj

    @staticmethod
    def replace_decimal(obj):
        """
        Replaces decimal into int or float

        :param obj: dictionary
        :return: dictionary with replaced decimal value
        """
        if isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = DBTypes.replace_decimal(obj[i])
            return obj
        elif isinstance(obj, dict):
            for k in obj.keys():
                obj[k] = DBTypes.replace_decimal(obj[k])
            return obj
        elif isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        else:
            return obj
