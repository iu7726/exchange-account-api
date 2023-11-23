from libs_account.models import Account
from libs_exchange_auth.crypto import *
import json
from libs_exchange_handler.og_exception import *

class UserInfo():
    user = None
    wallet_key = None
    wallet_secret = None
    def __init__(self):
        pass

    def getUser(self, userId):
        try:
            user = Account.objects.get(id=userId)
        except Account.DoesNotExist:
            user = None
        return user

    def getUserWelletKey(self, user):
        try:
            wallet_key = user.wallet_key
        except Account.DoesNotExist:
            wallet_key = None
        return decryptKMS(wallet_key)

    def getUserWelletSecret(self, user):
        try:
            wallet_secret = user.wallet_secret
        except Account.DoesNotExist:
            wallet_secret = None
        return decryptKMS(wallet_secret)

    def getUserTag(self, user):
        try:
            tag = user.tag
        except:
            tag = None
        return Decrypt(tag)

    def getUserKey(self, userId):
        if userId is None:
            raise ValueError("Invalid User")

        try:
            user = self.getUser(userId)
            wallet_key = self.getUserWelletKey(user)
            wallet_secret = self.getUserWelletSecret(user)
            tag = self.getUserTag(user)

            return {
                'wallet_key': wallet_key, 
                'wallet_secret': wallet_secret,
                'tag': tag
            }
        except Exception as e:
            print(e)
            raise OgException(e)


