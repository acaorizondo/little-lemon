from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from LittleLemonAPI.serializers import CartSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
import requests

@permission_classes([IsAuthenticated])    
class CartView(APIView):
    
    def get(self, request, format=None):
        user_id = Token.objects.get(key=request.auth.key).user_id
        if user_id:
            queryset = CartSerializer.Meta.model.objects.filter(user=user_id)
            serializer_class = CartSerializer(queryset, many=True)
            return Response(serializer_class.data, status=status.HTTP_200_OK)
               
    def post(self, request, format=None):
        
        # get menu item
        menuitem_id = request.POST.get('menuitem', None)
        url='http://127.0.0.1:8000/api/menu-items/'+str(menuitem_id)
        token = "Token " + str(Token.objects.get(key=request.auth.key))
        menuitem = requests.get(url, headers={'Authorization': token}).json()
        
        
        data = {"user": Token.objects.get(key=request.auth.key).user_id,
                "menuitem": menuitem["id"],
                "quantity": int(request.POST.get('quantity', None)),
                "unit_price": float(menuitem["price"])
        }
        
        serializer_class = CartSerializer(data=data)
        if serializer_class.is_valid():
            serializer_class.save()
            return Response(data=serializer_class.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        user_id = Token.objects.get(key=request.auth.key).user_id   
        if user_id:
            cart = CartSerializer.Meta.model.objects.filter(user=user_id)
            if cart:
               cart.delete()
               return Response({'message':'Cart eliminated succefully!'}, status=status.HTTP_200_OK)
            return Response({'error':'The cart does not exist!'},status=status.HTTP_400_BAD_REQUEST)
        return Response({'error':'The user does not exist!'},status=status.HTTP_400_BAD_REQUEST)