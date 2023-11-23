from libs_exchange_auth.crypto import Decrypt
import json
'''
A function that checks the value received from the client.
'''

def checkPincode(password):
    """Check the Pincode entered by the user.
    It's still being implemented.

    Args:
        method (str): Returns False if it is not 'POST'.
        body (request): Received request
    """
    return True

def validate(method: str, body):
    """Check Method and Password.

    Args:
        method (str): Returns False if it is not 'POST'.
        body (request): Password should be included as the received request.
    Returns:
        True | False -> boolean
    """

    # if method != 'POST':
    #     return False
    
    # if body is None or body.get('pincode') is None:
    #     return False

    # if checkPincode(body['pincode']) == False:
    #     return False

    return True