from rest_framework import serializers
from libs_account.models import Account
from libs_exchange_handler.og_exception import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'email', 'nickname')

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
        extra_kwards = {
            'password': {
                'required': True
            }
        }
    
    def validate(self, attrs):
        ogUserId = attrs.get('user_id')
        if Account.objects.filter(user_id=ogUserId).exists():
            raise OgException('User with this og community id already exists.', status_code=400)
        return attrs
    
    def create(self, validated_data):
        user = Account.objects.create_user(**validated_data)
        return user

class SuccessCreateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['email', 'nickname']

class ExchangeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'user_id', 'wallet_key', 'wallet_secret')

class UpdatePincodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'tag']

class UpdateOTPserializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'is_otp']

