from libs_exchange_handler.og_exception import *
from .userInfo import UserInfo
from rest_framework.exceptions import ValidationError

import okx.Account as Account


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

    def get_config(self, **params):
        '''Retrieve current account configuration.

        https://www.okx.com/docs-v5/en/?python#trading-account-rest-api-get-account-configuration
        '''
        try:
            api = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.get_account_config(**params)
        except:
            raise OgException('Get Account Config Error')
    
    def get_leverage(self, **params):
        try:
            '''Get Leverage

            https://www.okx.com/docs-v5/en/?python#trading-account-rest-api-get-leverage
            '''
            api = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.get_leverage(**params)
        except Exception as e:
            print(e)
            raise OgException('Get Account Leverage Error')

    def set_leverage(self, **params):
        '''Set leverage for MARGIN instruments under isolated/cross-margin trade mode at pairs level.

        https://www.okx.com/docs-v5/en/?python#trading-account-rest-api-set-leverage
        '''
        try:
            api = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.set_leverage(**params)
        except Exception as e:
            print(e)
            raise OgException('Set Account Leverage Error')

    def get_max_size(self, **params):
        '''Get maximum buy/sell amount or open amount
        
        https://www.okx.com/docs-v5/en/?python#trading-account-rest-api-get-maximum-buy-sell-amount-or-open-amount
        '''
        try:
            api = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.get_max_order_size(**params)
        except Exception as e:
            print(e)
            raise OgException('Get Account Max Size Error')
    
    def get_max_avail_size(self, **params):
        '''Get maximum available tradable amount
        
        https://www.okx.com/docs-v5/en/?python#trading-account-rest-api-get-maximum-available-tradable-amount
        '''
        try:
            api = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
            
            return api.get_max_avail_size(**params)
        except:
            raise OgException('Get Account Max Size Error')

    def get_trade_fee(self, **params):
        '''Get fee rates

        https://www.okx.com/docs-v5/en/?python#trading-account-rest-api-get-fee-rates
        '''
        try:
            api = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
            
            return api.get_fee_rates(**params)
        except:
            raise OgException('Get Account Fee Rate Error')

    def set_account_level(self, **params):
        try:
            api = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api._request_with_params('POST', '/api/v5/account/set-account-level', params)
        except Exception as e:
            print('account level api error: %s', e)
            raise OgException("Set Account Mode Error")
