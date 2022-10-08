from typing import Dict
from typing import Optional
from icgphutils.aws.awslambda import Lambda
from icgphutils.log import Logger
from icgphutils.log import FormatMessage


class CognitoCustomAuthorizer:
    gl_logger = Logger.get_logger()

    @staticmethod
    def __generate_policy(principal_id, effect, resource, context):
        return {
            'principalId': principal_id,
            'policyDocument': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        "Action": "execute-api:Invoke",
                        "Effect": effect,
                        "Resource": resource
                    }
                ]
            },
            "context": context
        }


    @classmethod
    def authorize(
        cls,
        token_decoder_function_name: str,
        token: str,
        method_arn: str,
        group: Optional[str] = None
    ) -> Dict:
        # Default
        policy = CognitoCustomAuthorizer.__generate_policy('CognitoCustomAuthorizer', 'Deny', method_arn, None)

        try:
            decoded_message = Lambda.invoke(
                function_name=token_decoder_function_name,
                payload=dict(id_token=token)
            )
        except Exception as e:
            cls.gl_logger.error(
                FormatMessage(
                    'Exception: {}',
                    e
                )
            )
        else:
            if decoded_message.get('claims') is not None:
                groups = decoded_message['claims'].get('cognito:groups', [])
                if group is None or group in groups:
                    principal_id = decoded_message['claims']['email']
                    context = decoded_message['claims']
                    if 'cognito:groups' in context:
                        # Convert list to comma-delimited string
                        context['cognito:groups'] = ",".join(context['cognito:groups'])
                    policy = CognitoCustomAuthorizer.__generate_policy(principal_id, 'Allow', method_arn, decoded_message['claims'])
                else:
                    cls.gl_logger.error(
                        FormatMessage(
                            'Client {} is not a member of {}',
                            decoded_message['claims']['email'],
                            group
                        )
                    )
            else:
                cls.gl_logger.error(
                    FormatMessage(
                        'Error: {}',
                        decoded_message
                    )
                )
        return policy
