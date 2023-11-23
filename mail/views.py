import os
from rest_framework.views import APIView
from rest_framework import permissions

from util.script import getRequestParams
from util.rabbitmq import send_mq
from mail.scripts import today_mail_count

from libs_exchange_handler.og_exception import *
from libs_exchange_handler.og_response import OgResponse

from libs_account.models import Account
from libs_mail.models import MailHistory

# Create your views here.
class MailAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            param = getRequestParams(request.GET)

            if param.get('type') is None:
                raise OgException('Invalid Type')

            account = Account.objects.get(id=request.user.id)
            
            count = today_mail_count(account.email, param.get('type'))

            if count >= 100:
                raise OgException('Max Mail Send')

            send_mq(
                message={'userId': account.user_id, 'type': param.get('type')}, 
                exchange=os.getenv('MQ_EXCHANGE'),
                route=os.getenv('MQ_MAIL_ROUTE')
            )

            response = OgResponse('Mail Send Success')

            return Response(response())
        except OgException as e:
            raise e
        except Exception as e:
            print("Mail Send Error: ", e)
            raise OgException('Mail Send Error')