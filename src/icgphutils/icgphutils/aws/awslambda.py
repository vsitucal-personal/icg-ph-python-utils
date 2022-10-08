import boto3
import os
import json
from typing import Optional
from typing import Dict
from icgphutils.constants import Constants


class Lambda:
    gl_client = boto3.client('lambda', region_name=os.getenv('REGION', Constants.DEFAULT_REGION))

    @classmethod
    def invoke(cls, function_name: str, payload: Optional[Dict] =None) -> Dict:

        if payload is not None:
            resp = cls.gl_client.invoke(
                FunctionName=function_name,
                Payload=bytes(json.dumps(payload).encode('utf-8'))
            )
        else:
            resp = cls.gl_client.invoke(
                FunctionName=function_name
            )
        response_payload = json.loads(resp['Payload'].read().decode())
        return response_payload
