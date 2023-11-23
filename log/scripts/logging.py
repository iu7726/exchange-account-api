import re, json, math
from ..serializers import *
from decimal import Decimal
from datetime import datetime
from libs_log.models import *
from account.scripts.community import checkOgToken
from util.script import getRequestParams

PRIVATE_IPS_PREFIX = ('10.', '172.', '192.', )

def get_client_ip(request):
    """get the client ip from the request
    """
    remote_address = request.META.get('REMOTE_ADDR')
    # set the default value of the ip to be the REMOTE_ADDR if available
    # else None
    ip = remote_address
    # try to get the first non-proxy ip (not a private ip) from the
    # HTTP_X_FORWARDED_FOR
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        proxies = x_forwarded_for.split(',')
        # remove the private ips from the beginning
        while (len(proxies) > 0 and
                proxies[0].startswith(PRIVATE_IPS_PREFIX)):
            proxies.pop(0)
        # take the first ip which is not a private one (of a proxy)
        if len(proxies) > 0:
            ip = proxies[0]

    return ip

def getIp(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip

def getClientInfo(value):
    request = value.get('request')
    value['ip'] = getIp(request)
    value['user_agent'] = request.META.get('HTTP_USER_AGENT')

    return value

def createAccountLog(values):
    try:
        values = getClientInfo(values)
        serializer = AccountLogSerializer(data = values)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            return print({'errors': serializer.errors})
    except Exception as e:
        return e

def createRefreshLog(values):
    try:
        request = values.get('request')
        values['account_id'] = request.user.id
        values['timestamp'] = math.floor(datetime.now().timestamp())
        values = getClientInfo(values)
        
        serializer = RefreshLogSerializer(data=values)

        if serializer.is_valid(raise_exception=True):
            log = Refresh()
            log.account_id = request.user.id
            log.timestamp = math.floor(datetime.now().timestamp())
            log.ip = values['ip']
            log.user_agent = values['user_agent']

            log.save()
        else:
            raise Exception("Refresh Log Error")
    except Exception as e:
        raise e

def createAccessLog(values, location):
    try:
        locationStr = None

        if location.get('country') != None:
            locationStr = location.get('country')

        if location.get('city') != None:
            locationStr = locationStr + '-' + location.get('city')

        log = AccessAccount()
        log.user_id = checkOgToken(values)
        log.account_id = values.user.id
        headers = {k[5:]: v for k, v in values.META.items() if k.startswith('HTTP_')}
        log.headers = headers
        log.path = values.path
        log.method = values.method
        log.param = getRequestParams(values.GET) if values.method == 'GET' else values.body.decode('utf-8')
        log.location = locationStr
        log.ip = getIp(values)
        log.user_agent = values.META.get('HTTP_USER_AGENT')
        log.save()

        return None
    except Exception as e:
        print(e)
        return None
   


