import requests, json, os, uuid, datetime
from libs_account.models import KYCHistory, Account
from libs_webhook.models import KYC

def createApplicate():
    # URL and Headers
    url = "https://api.eu.onfido.com/v3.6/applicants/"
    headers = {
        "Authorization": f"Token token={os.getenv('ONFIDO_API_TOKEN')}",
        "Content-Type": "application/json"
    }

    # Payload/Data
    data = {
        "id": uuid.uuid4().hex,
        "first_name": "Jane",
        "last_name": "Doe",
        "dob": "1990-01-31",
        "location": {
            "country_of_residence": "GBR",
        }
    }

    # Making the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # You can also handle the response based on status code or JSON data
    if response.status_code == 201 or response.status_code == 200:
        return response.json()
    else:
        print(response.text)
        return None

def createWorkflow(applicantId, userId, path):
    url = "https://api.eu.onfido.com/v3.6/workflow_runs"
    headers = {
        "Authorization": f"Token token={os.getenv('ONFIDO_API_TOKEN')}",
        "Content-Type": "application/json"
    }
    data = {
        "applicant_id": applicantId,
        "workflow_id": os.getenv('WORKFLOW_ID_LV1'),
        "custom_data": {
            "user_id": userId
        }
    }

    if path is not None:
        data["link"] = {
            "completed_redirect_url": path
        }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200 or response.status_code == 201:
        return response.json()
    else:
        print(response.text)
        return None

def createLink(accountId, userId, path):
    try:
        applicant = createApplicate()
        workflow = createWorkflow(applicant.get('id'), userId, path)

        history = KYCHistory()
        history.account_id = accountId
        history.user_id = userId
        history.workflow_run_id = workflow.get('id')
        history.applicant_id = applicant.get('id')
        history.raw = {"applicant": applicant, "workflow": workflow}
        history.created_at = datetime.datetime.now()
        history.save()

        return workflow.get('link').get('url')
    except Exception as e:
        print(e)
        return None

def getLink(accountId, path):
    kyc = KYCHistory.objects.filter(account_id=accountId)

    if kyc.exists():
        
        return f'https://eu.onfido.app/l/{kyc[0].workflow_run_id}'
    else:
        account = Account.objects.get(id=accountId)
        return createLink(account.id, account.user_id, path)

def getKycState(user_id):
    kyc = KYC.objects.filter(user_id=user_id, resource_type='workflow_run').order_by('-created_at')[:1]

    if kyc.exists():
        return kyc[0].status
    else:
        return None

        