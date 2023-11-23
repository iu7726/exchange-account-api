from rest_framework import serializers
from libs_log.models import *
from libs_exchange_handler.og_exception import *

class AccountLogSerializer(serializers.Serializer):
    account_id = serializers.IntegerField(required=True)
    type = serializers.CharField(required=True)
    ip = serializers.CharField()
    device = serializers.CharField()
    
    def create(self, validated_data):
        return Account.objects.create(**validated_data)

class RefreshLogSerializer(serializers.Serializer):
    account_id = serializers.IntegerField(required=True)
    ip = serializers.CharField()
    device = serializers.CharField()
    timestamp = serializers.IntegerField()

    def create(self, validated_data):
        return Refresh.objects.aupdate_or_create(**validated_data)

class AccessLogSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    headers = serializers.JSONField()
    path = serializers.CharField()
    ip = serializers.CharField()
    device = serializers.CharField()