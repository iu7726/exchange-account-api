from libs_exchange_handler.og_exception import *
from libs_exchange_handler.og_response import OgResponse
from .scripts.OKEx import getClient
from rest_framework import exceptions, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from util.script import getRequestParams


class OpenPositionAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            response = OgResponse(getClient(request).get_positions(**params))

            return Response(response())
        except Exception as e:
            print(e)
            raise OgException('Open Position Failed')

class PositionHistoryAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            response = OgResponse(getClient(request).get_positions_history())

            return Response(response())

        except Exception as e:
            print(e)
            raise OgException('Open Position history Failed')

class PositionRiskAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            params = getRequestParams(request.GET)

            response = OgResponse(
                getClient(request).get_position_risk(**params)
            )
            
            return Response(response())
        except Exception as e:
            raise OgException('Position Risk Error')

class PostionModeAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            response = OgResponse(
                getClient(request).set_position_mode(**request.data)
            )

            return Response(response())
        except Exception as e:
            print(e)
            raise OgException('Postiion Mode Error')

