from rest_framework.permissions import BasePermission
from libs_account.models import Permission, Account
from libs_log.models import Deposit, Withdraw
from django.db.models import Sum
from .scripts.redis import redis_conn
import json
from decimal import Decimal
from datetime import datetime

class IsDeposit(BasePermission):
    """
    Allows access Deposit permission
    """

    def has_permission(self, request, view):
        account = Account.objects.get(id=request.user.id)
        is_kyc = False

        if account.is_freeze == True:
          return bool(False)

        if account.level > 0:
          is_kyc = True

        permission_ban = Permission.objects.filter(account_id=request.user.id, type='deposit')
        
        return bool(
          request.user and 
          permission_ban.exists() == False and 
          is_kyc
        )

class IsWithdraw(BasePermission):
    """
    Allows access Withdraw permission
    """

    def has_permission(self, request, view):
        account = Account.objects.get(id=request.user.id)

        if account.is_freeze == True:
          return bool(False)

        permission_ban = Permission.objects.filter(id=request.user.id, type='withdraw')

        now = datetime.now()
        dailyCap = False
        try:
          if account.level == 1:
            if request.data.get('ccy') == 'USDT':
              price = Decimal(1)
            else:
              priceObj = redis_conn.hget('$USDT:price$', request.data.get('ccy'))
              price = Decimal((json.loads(priceObj)).get('price'))
            newWithdraw = price * Decimal(request.data.get('amt'))
            amountEqSum = Withdraw.objects.filter(account_id=request.user.id, created_at__gte=f'{now.year}-{now.month}-{now.day}').exclude(state='reject').aggregate(Sum('amount_eq'))
            if amountEqSum.get('amount_eq__sum') == None:
              amountEq = Decimal(0)
            else:
              amountEq = Decimal(amountEqSum.get('amount_eq__sum'))
            dailyCap = (amountEq + newWithdraw) <= Decimal(1000000)
          elif account.level == 2:
            if request.data.get('ccy') == 'USDT':
              price = Decimal(1)
            else:
              priceObj = redis_conn.hget('$USDT:price$', request.data.get('ccy'))
              price = Decimal((json.loads(priceObj)).get('price'))

            newWithdraw = price * Decimal(request.data.get('amt'))
            amountEqSum = Withdraw.objects.filter(account_id=request.user.id, created_at__gte=f'{now.year}-{now.month}-{now.day}').exclude(state='reject').aggregate(Sum('amount_eq'))
            if amountEqSum.get('amount_eq__sum') == None:
              amountEq = Decimal(0)
            else:
              amountEq = Decimal(amountEqSum.get('amount_eq__sum'))
            dailyCap = (amountEq + newWithdraw) <= Decimal(2000000)

          return bool(
            request.user and 
            permission_ban.exists() == False and
            dailyCap
          )
        except Exception as e:
          print('permission', e)
          return bool(False)