from rest_framework import serializers
from libs_account.models import Account
from django.contrib.auth import authenticate
from libs_exchange_handler.og_exception import *

from libs_exchange_auth.crypto import *

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)
    userId = serializers.IntegerField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        userId = attrs.get('userId')

        if not email or not password:
            raise ValueError('Please give both email and password.')
        try:
            userInfo = Account.objects.get(user_id=userId, is_active=1)
        except:
            raise ValueError('Wrong Credentials.2')
        
        if Decrypt(userInfo.email) != email:
            raise ValueError('Wrong Credentials.3')

        user = authenticate(request=self.context.get('request'), email=userInfo.email, password=password, ogUserId=userId)

        if not user:
            raise ValueError('Wrong Credentials.4')
        
        attrs['user'] = user
        return attrs