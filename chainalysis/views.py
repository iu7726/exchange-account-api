from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from libs_exchange_auth.crypto import *
from libs_exchange_auth.otp import *

from libs_exchange_auth.token import *

from libs_exchange_handler.og_exception import *
from libs_exchange_handler.og_response import OgResponse

import boto3
import os
import base64
from datetime import datetime

import requests

class DepositAPI(APIView):
    def get(self, request):
        try:
            headers = {
                'Token': os.getenv('CHAINALYSIS_KEY'),
                'Accept': 'application/json',
            }

            transfer_data = [{
                'network': 'Tron',
                'asset': 'TRX',
                'transferReference': '6540e9250ce0214ee063619cb2c9b90eb82376932dcebe8416cb3d886f26992b:TY4Bf4Kj9pe5YjUBJGFee73JB6YVVt383k',
            }]
            data = requests.post('https://api.chainalysis.com/api/kyt/v1/users/oguser4679/transfers/received', headers=headers, json=transfer_data)
            print(data.status_code)
            print(data.json()[0])
            data.raise_for_status()
            response = OgResponse(data.json()[0])
            
            return Response(response())
        except Exception as e:
            print('error', e)
            raise OgException('Chainalysis Auth Error')

class WithdrawAPI(APIView):
    def get(self, request):
        try:
            headers = {
                'Token': os.getenv('CHAINALYSIS_KEY'),
                'Accept': 'application/json'
            }

            withdrawal_attempt_data = [{
                'network': 'XRP',
                'asset': 'XRP',
                'address': 'raQwCVAJVqjrVm1Nj5SFRcX8i22BhdC9WA'
            }]

            data = requests.post('https://api.chainalysis.com/api/kyt/v1/users/oguser4679/withdrawaladdresses', headers=headers, json=withdrawal_attempt_data)
            print(data.status_code)
            print(data.json()[0])
            data.raise_for_status()
            response = OgResponse(data.json()[0])

            return Response(response())
        except Exception as e:
            print('error', e)
            raise OgException('Chainalysis Withdraw Error')

class AlertAPI(APIView):
    def get(self, request):
        try:
            headers = {
                'Token': os.getenv('CHAINALYSIS_KEY'),
                'Accept': 'application/json'
            }

            withdrawal_attempt_data = {
                'network': 'XRP',
                'asset': 'XRP',
                'address': 'raQwCVAJVqjrVm1Nj5SFRcX8i22BhdC9WA',
                'attemptIdentifier': 'oguser4679attempt4',
                'assetAmount': 22,
                'attemptTimestamp': datetime.utcnow().isoformat() + "Z",
            }

            attempt = requests.post('https://api.chainalysis.com/api/kyt/v2/users/oguser4679/withdrawal-attempts', headers=headers, json=withdrawal_attempt_data)
            externalId = attempt.json().get('externalId')
            print(attempt.json())
            data = requests.get(f'https://api.chainalysis.com/api/kyt/v2/withdrawal-attempts/{externalId}/alerts', headers=headers)
            print(data.status_code)
            print(data.json())
            data.raise_for_status()
            response = OgResponse(data.json())

            return Response(response())
        except Exception as e:
            print('error', e)
            raise OgException('Alert API Error')
        