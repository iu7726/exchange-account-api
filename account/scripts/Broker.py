import okx.NDBroker as NDBroker
import os

def create_subaccount(**params):
    try:
        api = NDBroker.NDBrokerAPI(os.getenv('OKEX_BROKER_KEY'), os.getenv('OKEX_BROKER_SECRET_KEY'), os.getenv('OKEX_BROKER_PASSPHRASE'), False, os.getenv('OKEX_BROEKR_FLAG'))

        return api.create_subaccount(**params)
    except Exception as e:
        print('Create Account Error: %s', e.message)

def create_subaccount_key(**params):
    try:
        api = NDBroker.NDBrokerAPI(os.getenv('OKEX_BROKER_KEY'), os.getenv('OKEX_BROKER_SECRET_KEY'), os.getenv('OKEX_BROKER_PASSPHRASE'), False, os.getenv('OKEX_BROEKR_FLAG'))

        params['ip'] = os.getenv('ALLOW_IP')
        return api.create_subaccount_apikey(**params)
    except Exception as e:
        print('Create Account Key Error: %s', e.message)

def delete_subaccount(**params):
    try:
        api = NDBroker.NDBrokerAPI(os.getenv('OKEX_BROKER_KEY'), os.getenv('OKEX_BROKER_SECRET_KEY'), os.getenv('OKEX_BROKER_PASSPHRASE'), False, os.getenv('OKEX_BROEKR_FLAG'))

        return api.delete_subaccount(**params)
    except Exception as e:
        print('Create Account Key Error: %s', e.message)

def get_nd_broker_info(**params):
    try:
        api = NDBroker.NDBrokerAPI(os.getenv('OKEX_BROKER_KEY'), os.getenv('OKEX_BROKER_SECRET_KEY'), os.getenv('OKEX_BROKER_PASSPHRASE'), False, os.getenv('OKEX_BROEKR_FLAG'))
        
        return api.get_broker_info()
    except Exception as e:
        print('NBBroker', e)
        return {}
    
def set_subaccount_level(**params):
    try:
        api = NDBroker.NDBrokerAPI(os.getenv('OKEX_BROKER_KEY'), os.getenv('OKEX_BROKER_SECRET_KEY'), os.getenv('OKEX_BROKER_PASSPHRASE'), False, os.getenv('OKEX_BROEKR_FLAG'))

        return api.set_subaccount_level(**params)
    except Exception as e:
        print("Broker account level: %s", e)
        return {}

def get_daily_rebate(**params):
    try:
        api = NDBroker.NDBrokerAPI(os.getenv('OKEX_BROKER_KEY'), os.getenv('OKEX_BROKER_SECRET_KEY'), os.getenv('OKEX_BROKER_PASSPHRASE'), False, os.getenv('OKEX_BROEKR_FLAG'))

        return api._request_with_params('GET','/api/v5/broker/nd/rebate-daily',params)
    except Exception as e:
        return {}