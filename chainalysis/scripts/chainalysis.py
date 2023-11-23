import requests, datetime, os

def get_withdraw_alert(
    subAcct,
    withdrawal_attempt_data
):
    try:
        headers = {
            'Token': os.getenv('CHAINALYSIS_KEY'),
            'Accept': 'application/json'
        }

        attempt = requests.post(f'https://api.chainalysis.com/api/kyt/v2/users/{subAcct}/withdrawal-attempts', headers=headers, json=withdrawal_attempt_data)
        externalId = attempt.json().get('externalId')
        print(attempt.json())
        data = requests.get(f'https://api.chainalysis.com/api/kyt/v2/withdrawal-attempts/{externalId}/alerts', headers=headers)
        print(data.status_code)
        print(data.json())
        data.raise_for_status()

        return data.json()
    except Exception as e:
        print('error', e)
        raise None

