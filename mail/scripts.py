import random, string, datetime, os
from libs_mail.models import MailVerificationCode, MailHistory
from django.db.models import F, Func, Value
from django.db.models.expressions import RawSQL
from libs_exchange_auth.token import Decrypt
import datetime

def mail_check(email, type, reqCode):
    decrypted_email = RawSQL("TO_BASE64(AES_ENCRYPT(%s, SHA2(CONCAT(%s,%s), 256)))", (Decrypt(email), os.getenv('COMMUNITY_KEY_1'), os.getenv('COMMUNITY_KEY_2')))
    
    code = MailVerificationCode.objects.filter(email=decrypted_email, type=type).values('code', 'expiry_time', 'created_at').order_by('-created_at').first()

    if code is None:
        return False

    now = datetime.datetime.now().astimezone(tz=datetime.timezone.utc)

    expiry = code.get('created_at') + datetime.timedelta(seconds=code.get('expiry_time'))
    
    return reqCode == code.get('code') and now < expiry

def today_mail_count(email, type):
    decrypted_email = RawSQL("TO_BASE64(AES_ENCRYPT(%s, SHA2(CONCAT(%s,%s), 256)))", (Decrypt(email), os.getenv('COMMUNITY_KEY_1'), os.getenv('COMMUNITY_KEY_2')))
    print(datetime.date.today())
    return MailVerificationCode.objects.filter(email=decrypted_email, type=type, created_at__gte=datetime.date.today()).count()
    