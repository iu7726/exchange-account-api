from libs_exchange_handler.og_exception import *
from libs_exchange_handler.og_response import OgResponse
from .scripts.OKEx import getClient
from rest_framework import exceptions, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from util.script import getRequestParams

# Create your views here.
class BillsAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            response = OgResponse(getClient(request).get_bills(**params))

            return Response(response())
        except Exception as e:
            print(e)
            raise OgException('Bills API error')

class BillsArchiveAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            response = OgResponse(getClient(request).get_bills_archive(**params))

            return Response(response())
        except:
            raise OgException('Bills Archvie API Error')