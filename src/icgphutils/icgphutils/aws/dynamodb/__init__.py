import os
import json
import boto3

from decimal import Decimal
from botocore.exceptions import ClientError
from typing import Dict
from typing import List
from typing import Optional

from icgphutils.aws.dynamodb.types import DBTypes
from icgphutils.constants import Constants
from icgphutils.log import Logger


class DynamoDB:

    def __init__(self, table_name):
        self.__table_name = table_name
        self.__client = boto3.client('dynamodb', region_name=os.getenv('REGION', Constants.DEFAULT_REGION))
        self.__logger = Logger.get_logger()

        # For table-based queries
        dynamodb = boto3.resource('dynamodb', region_name=os.getenv('REGION', Constants.DEFAULT_REGION))
        self.__db_table = dynamodb.Table(self.__table_name)

    def transact_get_item(self, keys: Dict):
        """
        Transaction-based implementation of GetItem

        :param keys: dictionary of primary key and sort key (if any)
        :return: item info
        """
        item = None
        try:
            result = self.__client.transact_get_items(
                TransactItems=[
                    {
                        'Get': {
                            'Key': DBTypes.convert_dict_to_db_item(keys),
                            'TableName': self.__table_name
                        }
                    }
                ]
            )
        except ClientError as e:
            self.__logger.error(e.response.get('Error').get('Message'))
            raise
        else:
            db_item = result['Responses'][0].get('Item')
            if db_item is not None:
                item = DBTypes.convert_db_dict_to_generic_item(db_item)
        return item

    def transact_add_item(self, entry: Dict, keys: Optional[List] = None):
        """
        Transaction-based implementation of PutItem

        :param entry: dictionary of item to be added
        :param keys: list of primary key and sort key; if None,operation is always overwrite
        :return: result dictionary
        """
        try:
            if keys is None:
                # Always overwrite
                result = self.__client.transact_write_items(
                    TransactItems=[
                        {
                            'Put': {
                                'Item': DBTypes.convert_dict_to_db_item(entry),
                                'TableName': self.__table_name
                            }
                        }
                    ]
                )
            else:
                checks = ' AND '.join(f'attribute_not_exists({key})' for key in keys)
                result = self.__client.transact_write_items(
                    TransactItems=[
                        {
                            'Put': {
                                'Item': DBTypes.convert_dict_to_db_item(entry),
                                'TableName': self.__table_name,
                                'ConditionExpression': checks
                            }
                        }
                    ]
                )
        except ClientError as e:
            self.__logger.error(e.response.get('Error').get('Message'))
            raise
        return result

    def transact_update_item(self, keys: Dict, attributes: Dict):
        """
        Transaction-based implementation of UpdateItem

        :param keys: dictionary of primary key and sort key (if any)
        :param attributes: attributes for update
        :return: result dictionary
        """
        try:
            expr = 'set {}'.format(','.join(f'#{k}=:{k}' for k in attributes))
            expression_attribute_values = {f':{k}': v for k, v in attributes.items()}
            expr_names = {f'#{k}': k for k in attributes}
            checks = ' AND '.join(f'attribute_exists({key})' for key in keys)
            result = self.__client.transact_write_items(
                TransactItems=[
                    {
                        'Update': {
                            'Key': DBTypes.convert_dict_to_db_item(keys),
                            'TableName': self.__table_name,
                            'UpdateExpression': expr,
                            'ConditionExpression': checks,
                            'ExpressionAttributeNames': expr_names,
                            'ExpressionAttributeValues': DBTypes.convert_dict_to_db_item(expression_attribute_values)
                        }
                    }
                ]
            )
        except ClientError as e:
            self.__logger.error(e.response.get('Error').get('Message'))
            raise
        return result

    def transact_write_items(self, **kwargs):
        try:
            result = self.__client.transact_write_items(**kwargs)
        except ClientError as e:
            self.__logger.error(e.response.get('Error').get('Message'))
            raise
        return result

    def update_item_custom(self, **kwargs):
        try:
            result = self.__client.update_item(**kwargs)
        except ClientError as e:
            self.__logger.error(e.response.get('Error').get('Message'))
            raise
        return result

    def add_item(self, entry: Dict, keys: Optional[List] = None) -> Dict:
        payload = json.loads(json.dumps(entry), parse_float=Decimal)
        try:
            if keys is None:
                # Always overwrite
                response = self.__db_table.put_item(
                    Item=payload
                )
            else:
                checks = ' AND '.join(f'attribute_not_exists({key})' for key in keys)
                response = self.__db_table.put_item(
                    Item=payload,
                    ConditionExpression=checks
                )
        except ClientError as e:
            self.__logger.error(e.response.get('Error').get('Message'))
            raise
        return response

    def get_item(self, keys: Dict, consistent_read: Optional[bool] = True) -> Dict:
        response = None
        try:
            response = self.__db_table.get_item(
                Key=keys,
                ConsistentRead=consistent_read
            )
        except ClientError as e:
            self.__logger.error(e.response.get('Error').get('Message'))
            raise
        return response.get('Item')

    def query(self, **kwargs):
        try:
            response = self.__db_table.query(**kwargs)
        except ClientError as e:
            self.__logger.error(e.response.get('Error').get('Message'))
            raise
        return response

    def scan(self, **kwargs):
        try:
            response = self.__db_table.scan(**kwargs)
        except ClientError as e:
            self.__logger.error(e.response.get('Error').get('Message'))
            raise
        return DBTypes.replace_decimal(response)

    def update_item(self, keys: Dict, attributes: Dict):
        try:
            expr = 'set {}'.format(','.join(f'#{k}=:{k}' for k in attributes))
            expression_attribute_values = {f':{k}': v for k, v in attributes.items()}
            expr_names = {f'#{k}': k for k in attributes}
            checks = ' AND '.join(f'attribute_exists({key})' for key in keys)
            result = self.__db_table.update_item(
                Key=keys,
                UpdateExpression=expr,
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expression_attribute_values,
                ConditionExpression=checks,
                ReturnValues='ALL_NEW'
            )
        except ClientError as e:
            self.__logger.error(e.response.get('Error').get('Message'))
            raise
        return result

    def delete_item(self, keys: Dict):
        response = None
        try:
            response = self.__db_table.delete_item(
                Key=keys
            )
        except ClientError as e:
            self.__logger.error(e.response.get('Error').get('Message'))
            raise
        return response

    def execute_statement(self, **kwargs):
        response = None
        try:
            response = self.__client.execute_statement(**kwargs)
        except ClientError as e:
            self.__logger.error(e.response.get('Error').get('Message'))
            raise
        response['Items'] = DBTypes.convert_db_list_to_generic_item(response['Items'])
        return response