import uuid, math, re, time
from datetime import datetime
from decimal import Decimal
from django.db.models import F

from chainalysis.scripts.chainalysis import get_withdraw_alert
from chainalysis.scripts.Network import get_network
from libs_exchange_auth.crypto import *
from libs_exchange_auth.otp import *
from libs_exchange_handler.og_exception import *
from libs_exchange_handler.og_response import OgResponse
from libs_account.models import Account, Balance
from libs_log.models import Withdraw as LogWithdraw, Deposit as LogDeposit, WithdrawAlert
from rest_framework import exceptions, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from util.script import getRequestParams
from util.address_format import getAddrCheck
from .scripts.OKEx import getClient
from .scripts.redis import redis_conn
from util.rabbitmq import send_mq

from account.scripts.community import getUserIdBySubAcct, getSubAccountIdByUserId

from mail.scripts import mail_check

from .permission import *

class BalanceAccoountAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            response = OgResponse(getClient(request).get_balance_account(**params))

            return Response(response())
        except Exception as e:
            print(e)
            raise OgException('Balance Failed')

class BalanceHistoryAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        balance = Balance.objects.filter(account_id=request.user.id)

        if balance.exists() == False:
            response = OgResponse([])
            return Response(response())

        balance = balance.annotate(
            uTime = F('u_time'),
            isoEq = F('iso_eq'),
            createdAt = F('created_at'),
            totalEq = F('total_eq')
        ).order_by('-created_at')[:24]

        response = OgResponse({'code': '0', 'data': list(balance.values(
            'details',
            'uTime',
            'imr',
            'isoEq',
            'totalEq',
            'createdAt'
        ))})

        return Response(response())

class BalanceAssetAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            response = OgResponse(getClient(request).get_balance_assets(**params))

            return Response(response())
        except Exception as e:
            print(e)
            raise OgException('Balance Failed')

class DepositInfoAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        now = datetime.now()
        dailySum = Deposit.objects.filter(account_id=request.user.id, created_at__gte=f'{now.year}-{now.month}-{now.day}').exclude(state='reject').aggregate(Sum('amount_eq'))
        totalSum = Deposit.objects.filter(account_id=request.user.id).exclude(state='reject').aggregate(Sum('amount_eq'))

        daily = dailySum.get('amount_eq__sum')
        total = totalSum.get('amount_eq__sum')

        if daily is None:
            daily = 0
        
        if total is None:
            total = 0
        
        response = OgResponse({
            "daily": daily,
            "total": total
        })

        return Response(response())

class DepositAPI(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDeposit]

    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            response = OgResponse(
                getClient(request).get_deposit_address(**params)
            )
            
            return Response(response())
        except Exception as e:
            raise e

class DepositHistoryAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            # getClient(request).get_deposit_history(**params)
            page = params.get('page')

            if page is None:
                page = 1
            else:
                page = int(page)

            offset = ((page - 1) * 30)

            count = LogDeposit.objects.filter(account_id=request.user.id).count()
            history = LogDeposit.objects.filter(account_id=request.user.id).order_by('-created_at')

            history = history.annotate(
                depId=F('dep_id'), 
                accountId=F('account_id'),
                okxUid=F('okx_uid'),
                txId = F('tx_id'),
                amountEq = F('amount_eq'),
                to = F('address'),
                createdAt = F('created_at')
            )[offset:offset + 30]


            response = OgResponse({
                "totalPage": math.trunc(count/30) + 1,
                "page": page,
                "data": list(history.values(
                    'depId', 'accountId', 'okxUid', 'txId', 'state', 'amountEq', 'to', 'asset', 'amount', 'network', 'createdAt'
                ))
            })
                
            return Response(response())
        except Exception as e:
            raise e

class WithdrawInfoAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        now = datetime.now()
        dailySum = Withdraw.objects.filter(account_id=request.user.id, created_at__gte=f'{now.year}-{now.month}-{now.day}').exclude(state='reject').aggregate(Sum('amount_eq'))
        totalSum = Withdraw.objects.filter(account_id=request.user.id).exclude(state='reject').aggregate(Sum('amount_eq'))
        account = Account.objects.get(id=request.user.id)

        limit = 0
        daily = dailySum.get('amount_eq__sum')
        total = totalSum.get('amount_eq__sum')

        if account.level == 1:
            limit = 1000000
        elif account.level == 2:
            limit = 2000000

        if daily is None:
            daily = 0
        
        if total is None:
            total = 0
        
        response = OgResponse({
            "limit": limit,
            "daily": daily,
            "total": total
        })

        return Response(response())

class WithdrawAPI(APIView):
    permission_classes = [permissions.IsAuthenticated, IsWithdraw]

    def post(self, request):
        try:
            addr = str(request.data.get('toAddr')).split(':')[0]

            if getAddrCheck(addr, request.data.get('chain')) == False:
                raise OgException("Invalid address")

            user = Account.objects.get(id=request.user.id)

            if validateOtp(Decrypt(user.otp_secret), request.data.get('otp')) == False or mail_check(user.email, 'withdraw', request.data.get('code')) == False:
                raise OgException("Invalid Verify")

            og_wd_id = uuid.uuid4().hex[:16] + str(math.ceil(time.time()))
    
            client = getClient(request)
            currencies = client.get_currencies(**{"ccy": request.data.get('ccy')})
            
            infoList = currencies.get('data')
            minWd = '0'
            for currency in infoList:
                if currency.get('chain') == request.data.get('chain'):
                    minWd = currency.get('minWd')

            if Decimal(request.data.get('amt')) < Decimal(minWd):
                raise OgException(f"Withdraw Min Value {minWd}")
            
            # internal withdraw check
            if str(request.data.get('dest')) == '3':

                reciveOgUserId = getUserIdBySubAcct(request.data.get('toAddr'))[4]

                ogUser = Account.objects.filter(user_id=reciveOgUserId)
                if (ogUser.exists()):
                    if (ogUser[0].level == 0):
                        raise OgException('Invalid ogUser kyc')  
                    else:
                        addressInfo = client.get_deposit_address(**{"ccy": request.data.get('ccy')})
                        for address in addressInfo.get('data'):
                            if address.get('chain') == request.data.get('chain'):
                                addr = address.get('addr')     
                else:
                    raise OgException('Invalid ogUser')   
            
            withdrawal_attempt_data = {
                'network': get_network(request.data.get('chain')),
                'asset': request.data.get('ccy'),
                'address': addr,
                'attemptIdentifier': og_wd_id,
                'assetAmount': request.data.get('amt'),
                'attemptTimestamp': datetime.utcnow().isoformat() + "Z",
            }
                
            chainalysis_res = get_withdraw_alert(
                subAcct=getSubAccountIdByUserId(user.user_id), 
                withdrawal_attempt_data=withdrawal_attempt_data
            )
            
            auto = False
            res = None

            state = 'pending'
            isManual = False

            if chainalysis_res is None:
                raise OgException('Chainalysis Error')

            if len(chainalysis_res.get('alerts')) == 0:
                # TODO: Automatic withdraw
                auto = True
                state = 'approved'
                # res = getClient(request).withdraw(**request.data)
                res = 'Withdraw Approved'
            else:
                # TODO: review
                alertDict = {
                    'SEVERE': 3, 
                    'HIGH': 2, 
                    'MEDIUM': 1, 
                    'LOW': 0
                }
                
                alertLevel = 0

                for alert in chainalysis_res.get('alerts'):
                    if alertLevel < alertDict[alert.get('alertLevel')]:
                        alertLevel = alertDict[alert.get('alertLevel')]

                    logAlert = WithdrawAlert()
                    logAlert.id = uuid.uuid4().hex
                    logAlert.account_id = request.user.id
                    logAlert.alert_level = alert.get('alertLevel')
                    logAlert.amount = alert.get('alertAmount')
                    logAlert.category = alert.get('category')
                    logAlert.category_id = alert.get('categoryId')
                    logAlert.service = alert.get('service')
                    logAlert.okx_uid = user.okx_uid
                    logAlert.wd_id = og_wd_id
                    logAlert.raw = json.dumps(alert)

                    logAlert.save()

                if alertLevel < 2:
                    auto = True
                    state = 'approved'
                    # res = getClient(request).withdraw(**request.data)
                    res = 'Withdraw Approved'
                else:
                    isManual = True
                    state = 'review'

            if request.data.get('ccy') == 'USDT':
                price_eq = Decimal(1)
            else:
                priceObj = json.loads(redis_conn.hget('$USDT:price$', request.data.get('ccy')))
                price_eq = Decimal(priceObj.get('price'))

            logWithdraw = LogWithdraw()
            logWithdraw.id = og_wd_id
            logWithdraw.state = state
            logWithdraw.account_id = request.user.id
            logWithdraw.user_id = user.user_id
            logWithdraw.okx_uid = user.okx_uid
            logWithdraw.amount = Decimal(request.data.get('amt')) - (Decimal(request.data.get('fee')) * Decimal(0.002))
            logWithdraw.amount_eq = price_eq * Decimal(request.data.get('amt'))
            logWithdraw.dest = request.data.get('dest')
            logWithdraw.to_address = request.data.get('toAddr')
            logWithdraw.network = request.data.get('chain')
            logWithdraw.asset = request.data.get('ccy')
            logWithdraw.fee = request.data.get('fee')
            logWithdraw.from_address = request.data.get('fromAddr')
            logWithdraw.is_manual = isManual
            logWithdraw.save()

            
            
            transfer_params = {
                'amt': str(Decimal(request.data.get('amt')) + (Decimal(request.data.get('fee')) - (Decimal(request.data.get('fee')) * Decimal(0.001)))),
                'ccy': request.data.get('ccy'),
                'from_': '18',
                'to': '6'
            }
            transferRes = getClient(request).transfer(**transfer_params)

            if transferRes.get('code') != '0':
                raise OgException(detail=transferRes.get('msg'), code=transferRes.get('code'))

            response = OgResponse({'auto': auto, 'res': res})
            
            try:
                if state == 'approved':
                    send_mq(
                        message={'id': og_wd_id, 'userId': user.user_id}, 
                        exchange=os.getenv('MQ_COMMUNITY'),
                        route=os.getenv('MQ_MAIL_WITHDRAW_REQUEST')
                    )
                elif state == 'review':
                    send_mq(
                        message={'userId': user.user_id}, 
                        exchange=os.getenv('MQ_COMMUNITY'),
                        route=os.getenv('MQ_MAIL_REVIEW')
                    )
            except:
                print('Mail Send Error', og_wd_id)

            return Response(response())
        except Exception as e:
            print(e)
            raise e

class WithdrawHistoryAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            page = params.get('page')
            

            if page is None:
                page = 1
            else:
                page = int(page)

            offset = int((page - 1) * 30)

            count = LogWithdraw.objects.filter(account_id=request.user.id).count()
            history = LogWithdraw.objects.filter(account_id=request.user.id).order_by('-created_at')

            history = history.annotate(
                accountId=F('account_id'),
                okxUid=F('okx_uid'),
                txId = F('tx_id'),
                amountEq = F('amount_eq'),
                createdAt = F('created_at')
            )[offset:offset + 30]


            response = OgResponse({
                "totalPage": math.trunc(count/30) + 1,
                "page": page,
                "data": list(history.values(
                    'id', 'accountId', 'okxUid', 'txId', 'state', 'asset', 'amount', 'createdAt', 'amountEq', 'network'
                ))
            })
            
            return Response(response())
        except Exception as e:
            raise e

class TransferStateAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            params = getRequestParams(request.GET)
            response = OgResponse(
                getClient(request).get_transfer_state(**params)
            )
            
            return Response(response())
        except Exception as e:
            raise e

class MaxWithdrawalAPI(APIView):
    permission_classes = [permissions.IsAuthenticated, IsWithdraw]

    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            response = OgResponse(
                getClient(request).get_max_withdraw(**params)
            )

            return Response(response())
        except:
            raise OgException('Get Max Withdraw Error')

class TranscationStateAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            response = OgResponse(
                getClient(request).get_deposit_withdraw_status(**params)
            )

            return Response(response())
        except:
            raise OgException('Get Transcation State Error')

class CurrenciesAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            response = OgResponse(
                getClient(request).get_currencies(**params)
            )
            
            return Response(response())
        except Exception as e:
            print('currencies error: ', e)
            raise OgException('Get Currencies Error')

class DepositLightningAPI(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDeposit]

    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            response = OgResponse(
                getClient(request).get_deposit_lightning(**params)
            )

            return Response(response())
        except:
            raise OgException('Get Deposit Lightning Error')

class WithdrawLightningAPI(APIView):
    permission_classes = [permissions.IsAuthenticated, IsWithdraw]

    def post(self, request):
        try:
            response = OgResponse(
                getClient(request).withdrawal_lightning(**request.data)
            )
            
            return Response(response())
        except Exception as e:
            raise e