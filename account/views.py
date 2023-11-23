import os

from auth.scripts.validate import *
from chainalysis.scripts.chainalysis import get_withdraw_alert
from django.core.serializers import serialize
from libs_account.models import Account, Permission, Accept
from libs_exchange_auth.crypto import *
from libs_exchange_auth.otp import *
from libs_exchange_auth.token import *
from libs_exchange_handler.og_exception import *
from libs_exchange_handler.og_response import OgResponse
from libs_log.models import AccessAccount, WithdrawAlert
from log.models import LOG_ACCOUNT_TYPE
from log.scripts.logging import createAccountLog
from mail.scripts import mail_check
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from util.script import getRequestParams, random_string
from util.rabbitmq import send_mq

from account.scripts.userInfo import UserInfo

from .scripts.Broker import *
from .scripts.community import *
from .scripts.OKEx import getClient
from .scripts.onfido import getLink, getKycState
from .serializers import (CreateUserSerializer, UpdateOTPserializer,
                          UpdatePincodeSerializer)


class CheckAPI(APIView):
    def get(self, request):
        ogUserId = checkOgToken(request)
        if ogUserId == 0:
            raise OgException('Invaild Data')

        ogUserInfo = CommunitySql(ogUserId)
        if ogUserInfo is None:
            raise OgException('Invaild User')


        obj = {
            'isExist': False,
            'hasOtp': False,
            'isActive': False,
            'isDeposit': False,
            'isFreeze': False,
            'banPermission': [],
            'accept': [],
            'subAcct': getSubAccountIdByUserId(ogUserInfo[0]),
            'level': 0,
            'kycState': None,
            'vip': 0
        }
        
        try:
            account = Account.objects.get(user_id=ogUserInfo[0])

            obj['isExist'] = True
            obj['hasOtp'] = account.is_otp
            obj['isActive'] = account.is_active
            obj['isDeposit'] = account.is_deposit
            obj['level'] = account.level
            obj['vip'] = account.vip
            obj['isFreeze'] = account.is_freeze

            banPermission = []
            permission = Permission.objects.filter(user_id=ogUserInfo[0])

            if permission.exists():
                for per in permission:
                    banPermission.append(per.type)
            
            obj['banPermission'] = banPermission

            accept = []
            acceptAry = Accept.objects.filter(user_id=ogUserInfo[0])
            
            if acceptAry.exists():
                for apt in acceptAry:
                    accept.append(apt.type)
            obj['accept'] = accept

            obj['kycState'] = getKycState(ogUserInfo[0])

        except Account.DoesNotExist:
            account = None

        response = OgResponse(obj)

        return Response(response())

class CreateAPI(APIView):
    serializer_class = CreateUserSerializer

    def __insertDB(self):
        """Create a new account
        """
        serializer = CreateUserSerializer(data = {
            'email': Encrypt(self.ogUserInfo[1]),
            'user_id': self.ogUserId,
            'password': os.getenv('SUB_ACCOUNT_TAG') + str(self.ogUserId),
            'nickname': self.ogUserInfo[2],
            'tag': Encrypt(self.tag),
            'wallet_key': encryptKMS(self.apiKey.get('apiKey')),
            'wallet_secret': encryptKMS(self.apiKey.get('secretKey')),
            'okx_uid': self.subaccountId,
            'otp_secret': Encrypt(self.otpSecret)
        })

        if serializer.is_valid(raise_exception = True):
            try:
                user = serializer.save()
            except Exception as e:
                raise OgException(e)

            createAccountLog({
                'request': self.request, 
                'account_id': user.id, 
                'type': LOG_ACCOUNT_TYPE[0][0]
            })
            return True
        else:
            return False
    

    def post(self, request):
        """Create a new sub account
        
        Returns:
            subaccount (object)
            email (str)
            otp (str)
        """
        if validate(request.method, request.data) == False:
            raise OgException('Invaild Data')

        ogUserId = checkOgToken(request)
        if ogUserId == 0:
            raise OgException('Invaild Data')
        self.ogUserId = ogUserId

        ogUserInfo = CommunitySql(ogUserId)
        if ogUserInfo is None:
            raise OgException('Invaild User')
        self.ogUserInfo = ogUserInfo

        isAccount = Account.objects.filter(user_id=ogUserId)
        if isAccount.exists():
            raise OgException('Account already exists')

        self.subAcct = getSubAccountIdByUserId(str(ogUserId))
        subaccount = create_subaccount(**{
            'subAcct': self.subAcct,
            'label': str(ogUserId)
        })
        if subaccount is None or subaccount.get('code') != '0':
            print(subaccount.get('msg'))
            raise OgException('Sub Account Create Failed')

        subaccount = subaccount.get('data')[0]
        self.subaccountId = subaccount.get('uid')
        self.tag = 'Og-' + random_string(8) + str(ogUserId)
        apiKey = create_subaccount_key(**{
            'subAcct': self.subAcct,
            'label': str(ogUserId),
            'passphrase': self.tag,
            'perm': 'read_only,trade,withdraw'
        })
        if apiKey is None or apiKey.get('code') != '0':
            raise OgException(apiKey.get('msg'))
        self.apiKey = apiKey.get('data')[0]

        set_subaccount_level(
            subAcct=os.getenv('SUB_ACCOUNT_TAG') + str(ogUserId),
            acctLv='2'
        )

        self.otpSecret = createOtpBase()
        
        insertAccount = self.__insertDB()
        if insertAccount is None or insertAccount == False:
            raise OgException('Sub Account Insert Failed')

        response = OgResponse({
            # "subaccount": subaccount,
            # "email": self.ogUserInfo[1],
            "otp": "otpauth://totp/{}?secret={}&issuer=exchange.og.xyz".format(ogUserInfo[1], self.otpSecret)
        })
        return Response(response())

class OTPAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try: # refesh
            param = getRequestParams(request.GET)
            account = Account.objects.get(id=request.user.id)

            if account.is_otp == 1:
                return Response(OgResponse('Allready OTP')())

            if param.get('is_refresh') == True:
                account.otp_secret = Encrypt(createOtpBase())
                account.save()
            
            response = OgResponse(
                "otpauth://totp/{}?secret={}&issuer=exchange.og.xyz".format(Decrypt(account.email), Decrypt(account.otp_secret))
            )
            return Response(response())
        except Exception as e:
            print(e)
            raise OgException(e)

    def post(self, request):
        '''Update Add OTP

        otp (Str)
        '''
        account = Account.objects.get(id=request.user.id)
        if mail_check(account.email, 'otp', request.data.get('code')) == False:
            raise OgException('Invalid Mail Code')
        
        if validateOtp(Decrypt(account.otp_secret), request.data.get('otp')) == False:
            raise OgException('Invalid OTP')

        serializer = UpdateOTPserializer(data = {
            'id': request.user.id,
            'is_otp': True
        })
        try:
            if serializer.is_valid(raise_exception=True):
                account.is_otp = True
                account.save()

                otp = "otpauth://totp/{}?secret={}&issuer=exchange.og.xyz".format(Decrypt(account.email), Decrypt(account.otp_secret))

                response = OgResponse({
                    'msg': 'success change',
                    'otp': otp
                })

                try:
                    send_mq(
                        message={'userId': account.user_id}, 
                        exchange=os.getenv('MQ_COMMUNITY'),
                        route=os.getenv('MQ_MAIL_OTP')
                    )
                except:
                    print("OTP Mail Error", account.user_id)

                return Response(response())
            else:
                raise OgException('Invalid OTP')
        except Exception as e:
            print(e)
            raise OgException('Add OTP Error')

class OTPDisabledAPI(APIView):
    def post(self, request):
        account = Account.objects.get(id=request.user.id)

        if validateOtp(Decrypt(account.otp_secret), request.data.get('otp')) == False or mail_check(account.email, 'otp', request.data.get('code')) == False:
            raise OgException("Invalid Verify")
        
        account.is_otp = False
        account.save()
        
        response = OgResponse('OTP Disabled')

        return Response(response())

class MeAPI(APIView):
    def get(self, request):
        try:
            account = Account.objects.get(id=request.user.id)
            response = OgResponse({
                'email': Decrypt(account.email),
                'nickname': account.nickname,
                'isStaff': account.is_staff,
                'isAdmin': account.is_superuser,
                'hasOtp': account.is_otp
            })

            return Response(response())
        except Exception as e:
            raise OgException('Invalid User')

class ConfigAPI(APIView):
    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            response = OgResponse(
                getClient(request).get_config(**params)
            )

            return Response(response())
        except:
            raise OgException('Config API Error')

class LeverageAPI(APIView):
    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            response = OgResponse(
                getClient(request).get_leverage(**params)
            )

            return Response(response())
        except:
            raise OgException('Leverage API Error')

    def post(self, request):
        try:
            response = OgResponse(getClient(request).set_leverage(**request.data))

            return Response(response())
        except:
            raise OgException('Leverage API Error')

class MaxSizeAPI(APIView):
    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            response = OgResponse(
                getClient(request).get_max_size(**params)
            )

            return Response(response())
        except:
            raise OgException('Max Size API Error')

class MaxAvailSizeAPI(APIView):
    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            response = OgResponse(
                getClient(request).get_max_avail_size(**params)
            )

            return Response(response())
        except:
            raise OgException('Max Size API Error')

class FeeRateAPI(APIView):
    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            response = OgResponse(
                getClient(request).get_trade_fee(**params)
            )

            return Response(response())
        except:
            raise OgException('Fee Rate API Error')

class KYCAPI(APIView):
    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            link = getLink(request.user.id, params.get('path'))

            response = OgResponse(link)

            return Response(response())
        except:
            raise OgException('GET KYC API Error')        

class LevelAPI(APIView):
    def post(self, request):
        try:
            user = Account.objects.get(id=request.user.id)
            response = OgResponse(
                set_subaccount_level(
                    subAcct=os.getenv('SUB_ACCOUNT_TAG') + str(user.user_id),
                    acctLv=request.data.get('acctLv')
                )
            )

            return Response(response())
        except Exception as e:
            print('Level API Error: %s', e)
            raise OgException('Level API Error')    

class LoginHistoryAPI(APIView):
    def get(self, request):
        account = Account.objects.get(id=request.user.id)

        history = AccessAccount.objects.filter(user_id=account.user_id, path='/token').order_by('-created_at')[:10]

        if history is None:
            history = []
        
        response = OgResponse({'code':'0', 'data': list(history.values('created_at', 'ip', 'location'))})
        
        return Response(response())

class FreezeAPI(APIView):
    def post(self, request):
        account = Account.objects.get(id=request.user.id)

        if type(request.data.get('freeze')) != bool:
            raise OgException("Invalid Freeze Value")
        
        account.is_freeze = request.data.get('freeze')
        account.save()

        response = OgResponse('Freeze Value Changeed Success')

        return Response(response())

class AcceptAPI(APIView):
    def post(self, request):
        account = Account.objects.get(id=request.user.id)

        accept = Accept()
        accept.account_id = request.user.id
        accept.user_id = account.user_id
        accept.type = request.data.get('type')

        accept.save()

        response = OgResponse(f'Account {accept.type} Add Success')

        return Response(response())

class AcceptRemoveAPI(APIView):
    def post(self, request):
        accept = Accept.objects.filter(account_id=request.user.id, type=request.data.get('type'))

        if accept.exists() == False:
            raise OgException('Not Exists Accept')

        accept[0].delete()

        response = OgResponse(f"Account {request.data.get('type')} Remove Success")

        return Response(response())
        