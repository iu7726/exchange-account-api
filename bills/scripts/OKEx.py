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

    def get_bills(self, **params):
        '''Retrieve the bills of the account. The bill refers to all transaction records that result in changing the balance of an account. Pagination is supported, and the response is sorted with the most recent first. This endpoint can retrieve data from the last 7 days.

        https://www.okx.com/docs-v5/en/?python#trading-account-rest-api-get-bills-details-last-7-days
        '''
        try:
            api = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
            
            return api.get_account_bills(**params)
        except Exception as e:
            print('biils history error', e)
            raise OgException('Get Bills Error')

    def get_bills_archive(self, **params):
        '''Retrieve the account’s bills. The bill refers to all transaction records that result in changing the balance of an account. Pagination is supported, and the response is sorted with most recent first. This endpoint can retrieve data from the last 3 months.

        https://www.okx.com/docs-v5/en/?python#trading-account-rest-api-get-bills-details-last-3-months
        '''
        try:
            api = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.get_account_bills_archive(**params)
        except:
            raise OgException('Get Bills Archive Error')