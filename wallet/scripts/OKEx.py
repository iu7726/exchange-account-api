from ..serializers import *
from libs_exchange_handler.og_exception import *
from rest_framework.exceptions import ValidationError
from account.scripts.userInfo import UserInfo

import okx.Account as Account
import okx.Funding as Funding

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
    
    def get_balance_account(self, **params):
        '''Retrieve a list of assets (with non-zero balance), remaining balance, and available amount in the trading account.

        https://www.okx.com/docs-v5/en/?python#trading-account-rest-api-get-balance
        '''
        try:
            api = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.get_account_balance(**params)
        except Exception as e:
            raise OgException('Error getting account balance')

    def get_balance_assets(self, **params):
        '''Retrieve the funding account balances of all the assets and the amount that is available or on hold.

        https://www.okx.com/docs-v5/en/?python#funding-account-rest-api-get-balance
        '''
        try:
            api = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
        
            return api.get_balances(**params)
        except Exception as e:
            raise OgException('Error getting assets balance')

    def get_deposit_address(self, **params):
        """Retrieve the deposit addresses of currencies, including previously-used addresses.

        https://www.okx.com/docs-v5/en/?python#funding-account-rest-api-get-deposit-address
        """
        try:
            api = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.get_deposit_address(**params)
        except Exception as e:
            print(e)
            raise OgException('Get Deposit Address Error')
    
    def get_deposit_history(self, **params):
        '''Retrieve the deposit records according to the currency, deposit status, and time range in reverse chronological order. The 100 most recent records are returned by default.
Websocket API is also available, refer to Deposit info channel.

        https://www.okx.com/docs-v5/en/?python#funding-account-rest-api-get-deposit-history
        '''
        try:
            api = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.get_deposit_history(**params)
        except:
            raise OgException('Get Deposit History Error')

    def get_deposit_withdraw_status(self, **params):
        '''Retrieve deposit's and withdrawal's detailed status and estimated complete time.

        https://www.okx.com/docs-v5/en/?python#funding-account-rest-api-get-withdrawal-history
        '''
        try:
            api = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.get_deposit_withdraw_status(**params)
        except:
            raise OgException('Get Deposit History Error')
    
    def get_max_withdraw(self, **params):
        '''Retrieve the maximum transferable amount from trading account to funding account. If no currency is specified, the transferable amount of all owned currencies will be returned.

        https://www.okx.com/docs-v5/en/?python#trading-account-rest-api-get-maximum-withdrawals
        '''
        try:
            api = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.get_max_withdrawal(**params)
        except:
            raise OgException('Get Max Withdraw error')

    def get_currencies(self, **params):
        '''Retrieve a list of all currencies.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-currencies
        '''
        try:
            api = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.get_currencies(**params)
        except Exception as e:
            print("OKX Currencies Error: ", e)
            raise OgException('Get Currencies Error')

    def withdraw(self, **params):
        '''Withdrawal of tokens. Common sub-account does not support withdrawal.

        https://www.okx.com/docs-v5/en/?python#funding-account-rest-api-withdrawal
        '''
        try:
            api = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.withdrawal(**params)
        except Exception as e:
            print(e)
            raise OgException('Withdraw error')
    
    def get_withdraw_history(self, **params):
        '''Withdrawal of tokens. Common sub-account does not support withdrawal.

        https://www.okx.com/docs-v5/en/?python#funding-account-rest-api-withdrawal
        '''
        try:
            api = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.get_withdrawal_history(**params)
        except Exception as e:
            print(e)
            raise OgException('GET Withdraw history error')

    def transfer(self, **params):
        '''This endpoint supports the transfer of funds between your funding account and trading account

        https://www.okx.com/docs-v5/en/?python#funding-account-rest-api-funds-transfer
        '''
        try:
            api = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.funds_transfer(**params)
        except Exception as e:
            print(e)
            raise OgException('Transfer Error')

    def get_transfer_state(self, **params):
        '''Retrieve the transfer state data of the last 2 weeks.

        https://www.okx.com/docs-v5/en/?python#funding-account-rest-api-get-funds-transfer-state
        '''
        try:
            api = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            return api.transfer_state(**params)
        except Exception as e:
            print(e)
            raise OgException('Get transfer state Error')

    def withdrawMaster(self, **params):
        '''Withdrawal of tokens. Common sub-account does not support withdrawal.

        https://www.okx.com/docs-v5/en/?python#funding-account-rest-api-withdrawal
        '''
        try:
            api = Funding.FundingAPI(os.getenv('OKEX_BROKER_KEY'), os.getenv('OKEX_BROKER_SECRET_KEY'), os.getenv('OKEX_BROKER_PASSPHRASE'), False, os.getenv('OKEX_BROEKR_FLAG'))

            return api.withdrawal(**params)
        except Exception as e:
            print(e)
            raise OgException('Withdraw Master error')

    def get_deposit_lightning(self, **params):
        '''Users can create up to 10,000 different invoices within 24 hours.

        https://www.okx.com/docs-v5/en/?python#funding-account-rest-api-asset-bills-details
        '''
        try:
            api = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)
            
            if params.get('ccy') == None:
                params['ccy'] = 'BTC'
            
            return api._request_with_params('GET', '/api/v5/asset/deposit-lightning', params)
        except Exception as e:
            print(e)
            raise OgException('Error Get deposit lighting')
    
    def withdrawal_lightning(self, **params):
        '''The maximum withdrawal amount is 0.1 BTC per request, and 1 BTC in 24 hours. The minimum withdrawal amount is approximately 0.000001 BTC. Sub-account does not support withdrawal.

        https://www.okx.com/docs-v5/en/?python#funding-account-rest-api-lightning-withdrawals
        '''
        try:
            api = Funding.FundingAPI(self.api_key, self.secret_key, self.passphrase, False, self.flag)

            if params.get('ccy') == None:
                params['ccy'] = 'BTC'

            return api.withdrawal_lightning(**params)
        except Exception as e:
            print(e)
            raise OgException('Error Withdrawal Lightning')
