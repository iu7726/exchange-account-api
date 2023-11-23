from rest_framework.views import APIView
from libs_exchange_handler.og_exception import *
from libs_exchange_handler.og_response import OgResponse

class SocketInfoAPI(APIView):
    def get(self, request):
        try:
            response = OgResponse('account_'+str(request.user.id))
            return Response(response())
        except Exception as e:
            print(e)
            raise OgException('Get Socket Info Error')