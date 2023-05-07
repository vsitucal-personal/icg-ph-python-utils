import json
from typing import Union
from typing import List
from typing import Optional
from typing import Any


class HttpUtils:
    # HTTP Constants
    HTTP_HEADERS = 'headers'
    HTTP_STATUS_CODE = 'statusCode'
    HTTP_BODY = 'body'

    # HTTP Status Codes
    HTTP_STATUS_SUCCESS = 200
    HTTP_STATUS_CREATED = 201
    HTTP_STATUS_BADREQUEST = 400
    HTTP_STATUS_UNAUTHORIZED = 401
    HTTP_STATUS_FORBIDDEN = 403
    HTTP_STATUS_NOTFOUND = 404
    HTTP_STATUS_INTERNALSERVER_ERROR = 500
    HTTP_STATUS_NOTIMPLEMENTED_ERROR = 501

    # Error Codes
    INTERNAL_ERROR = 'InternalError'
    BADREQUEST_ERROR = 'BadRequestError'
    NOTFOUND_ERROR = 'NotFoundError'
    UNAUTHORIZED_ERROR = 'UnauthorizedError'
    FORBIDDEN_ERROR = 'ForbiddenError'
    NOTIMPLEMENTED_ERROR = 'NotImplementedError'

    # Error Messages
    NOTFOUND_MSG = 'Not found'

    @staticmethod
    def generate_http_response(
        response_payload: Union[dict, List],
        status_code: Optional[int] = HTTP_STATUS_SUCCESS
    ) -> dict:
        """
        Generates HTTP response to be returned to client
        :param response_payload: Response payload
        :param status_code: Status code of response
        :return: Response dictionary
        """
        body = json.dumps(response_payload)

        # Add headers as necessary
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': str(len(body)),
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS,PATCH',
            'Access-Control-Allow-Headers':
                'Origin,X-Requested-With,Content-Type,Accept,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        }

        response = {}
        response.setdefault(HttpUtils.HTTP_HEADERS, headers)
        response.setdefault(HttpUtils.HTTP_STATUS_CODE, status_code)
        response.setdefault(HttpUtils.HTTP_BODY, body)

        return response

    @staticmethod
    def assemble_error_payload(message, code=INTERNAL_ERROR):
        payload = {
                'code': code,
                'message': message
        }
        return payload

    @staticmethod
    def assemble_bad_request_payload(message: Any):
        if isinstance(message, dict):
            payload = message
        else:
            payload = {
                'code': HttpUtils.BADREQUEST_ERROR,
                'message': message
            }
        return payload

    @staticmethod
    def assemble_server_error_payload(message: Any):
        if isinstance(message, dict):
            payload = message
        else:
            payload = {
                'code': HttpUtils.INTERNAL_ERROR,
                'message': message
            }
        return payload
