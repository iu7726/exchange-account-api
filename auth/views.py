import os
from datetime import datetime

from account.scripts.community import *
from account.scripts.userInfo import UserInfo
from django.contrib.auth import login
from knox import views as knox_views
from libs_account.models import Account
from libs_exchange_auth.crypto import *
from libs_exchange_auth.otp import *
from libs_exchange_auth.token import *
from libs_exchange_handler.og_exception import *
from libs_exchange_handler.og_response import OgResponse
from log.models import LOG_LOGIN_TYPE
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer


def getOgUserInfo(request):
    """Get OG User Info

    Args:
        request (Request)
    """
    ogUserId = checkOgToken(request)
    if ogUserId == 0:
        raise OgException('Invaild Data')

    ogUserInfo = CommunitySql(ogUserId)
    if ogUserInfo is None:
        raise OgException('Invaild Data')
    
    return ogUserInfo

def executeLogin(self, serializer, request):
    """Execute Knox Login

    Args:
        serializer (obj)
        request (obj)
    """
    user = serializer.validated_data['user']
    login(request, user)
    response = self.super().post(request, format=None)

    return response

class LoginOtpAPI(knox_views.LoginView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        """Login OTP Knox

        Args:
            otp (str)
        Returns:
            expiry (str)
            token (str)
            user (obj) -> {
                id (int)
                email (str)
                nickname (str)
            }
            oauth (str)
            refresh_token (str)
        """
        try:
            otp = request.data.get('otp')

            ogUserInfo = getOgUserInfo(request)

            account = Account.objects.filter(user_id=ogUserInfo[0], is_active=1)

            if not account.exists():
                raise OgException('Not Exists Account', -200)
            
            if Decrypt(account[0].email) != ogUserInfo[1]:
                raise OgException('Invalid Data', -201)

            # print(account[0].is_otp, validateOtp(Decrypt(account[0].otp_secret), otp), otp)
            # if account[0].is_otp and not validateOtp(Decrypt(account[0].otp_secret), otp):
            #     raise OgException('Invalid Data3', -202)

            tag = os.getenv('SUB_ACCOUNT_TAG') + str(ogUserInfo[0])
            serializer = self.serializer_class(data={
                'email': ogUserInfo[1],
                'password': tag,
                'userId': ogUserInfo[0]
            })

            if serializer.is_valid(raise_exception=True) == False:
                raise OgException(serializer.errors)

            user = serializer.validated_data['user']
            login(request, user)
            response = super().post(request, format=None)

            token = generatorToken()
            refreshToken = generaterefreshToken()

            ogResponse = OgResponse({
                'authBase': response.data.get('token'),
                'authAccess': token,
                'refreshToken': refreshToken
            })
            return Response(ogResponse())
        except OgException as e:
            raise e
        except Exception as e:
            print(e)
            raise OgException('Login Server Error')
class AuthTokenAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """refresh Access Token

        Args:
            refresh_token (str)
        Returns:
            access_token (str)
        """
        try:
            token = request.headers.get('X-Auth-Access')
            if token is None:
                raise OgException('Invalid Data')
            
            token = decryptToken(token)
            refreshToken = request.data.get('refreshToken')

            if isValidToken(token, decryptToken(refreshToken)):
                raise OgException('Invalid Data')
            
            token['exp'] = datetime.now().timestamp() + (60*5)        

            response = OgResponse(encryptToken(token))

            return Response(response())
        except Exception as e:
            print(e)
            raise OgException('Refresh Token Error')
