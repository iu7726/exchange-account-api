from ..serializers import *
from libs_exchange_handler.og_exception import *
from rest_framework.exceptions import ValidationError
from account.scripts.userInfo import UserInfo

import okx.Account as Account
import okx.PublicData as Public

import json, os, time, math

def getClient(request):
    userInfo = UserInfo()
    keys = userInfo.getUserKey(request.user.id)
    if keys is None:
        raise OgException('Invalid User', status_code=400)

    return OKExClient(**keys)

class OKExClient():
    def __init__(self, **keys):
        self.api_key = keys.get('wallet_key')
        self.secret_key = keys.get('wallet_secret')
        self.passphrase = keys.get('tag')
        self.flag = '0'
    
    def get_positions(self, **params):
        '''Retrieve information on your positions. When the account is in net mode, net positions will be displayed, and when the account is in long/short mode, long or short positions will be displayed. Return in reverse chronological order using ctime.

        https://www.okx.com/docs-v5/en/?python#trading-account-rest-api-get-positions
        '''
        try:
            api = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api._request_with_params('GET', '/api/v5/account/positions', params)
        except Exception as e:
            print(e)
            raise OgException('Get Position Error')

    def get_positions_history(self, **params):
        '''Retrieve the updated position data for the last 3 months. Return in reverse chronological order using utime.

        https://www.okx.com/docs-v5/en/?python#trading-account-rest-api-get-positions-history
        '''
        try:
            api = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.get_positions_history(**params)
        except:
            raise OgException('Get Position History Error')

    def get_position_risk(self, **params):
        '''Get account and position risk
        
        https://www.okx.com/docs-v5/en/?python#trading-account-rest-api-get-account-and-position-risk
        '''
        try:
            api = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.get_position_risk(**params)
        except:
            raise OgException('Get Position Risk Error')

    def set_position_mode(self, **params):
        try:
            api = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.set_position_mode(**params)
        except Exception as e:
            print(e)
            raise OgException('Set Postion Mode')