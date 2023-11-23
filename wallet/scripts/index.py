from libs_account.models import Account
from libs_log.models import Withdraw
from datetime import datetime
from decimal import Decimal
from django.db.models import Sum

def kycCheck(accountId, usdValue):
	now = datetime.now()
	dailyCap = False
	account = Account.objects.get(id=accountId)
	if account.level == 1:
		newWithdraw = Decimal(usdValue)
		amountEqSum = Withdraw.objects.filter(account_id=accountId, created_at__gte=f'{now.year}-{now.month}-{now.day}').exclude(state='reject').aggregate(Sum('amount_eq'))
		if amountEqSum.get('amount_eq__sum') == None:
			amountEq = Decimal(0)
		else:
			amountEq = Decimal(amountEqSum.get('amount_eq__sum'))
		dailyCap = (amountEq + newWithdraw) <= 1000000
		print(amountEq + newWithdraw)
	elif account.level == 2:
		newWithdraw = Decimal(usdValue)
		amountEqSum = Withdraw.objects.filter(account_id=accountId, created_at__gte=f'{now.year}-{now.month}-{now.day}').exclude(state='reject').aggregate(Sum('amount_eq'))
		if amountEqSum.get('amount_eq__sum') == None:
			amountEq = Decimal(0)
		else:
			amountEq = Decimal(amountEqSum.get('amount_eq__sum'))
		dailyCap = (amountEq + newWithdraw) <= 1000000

	return dailyCap