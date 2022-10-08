import boto3
import os

from icgphutils.constants import Constants


class SSM:
    gl_client = boto3.client('ssm', region_name=os.getenv('REGION', Constants.DEFAULT_REGION))

    @classmethod
    def get_parameter(cls, key, decrypt=False):
        resp = cls.gl_client.get_parameter(Name=key, WithDecryption=decrypt)
        return resp['Parameter']['Value']
