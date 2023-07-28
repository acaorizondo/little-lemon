from rest_framework import viewsets
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status

from LittleLemonAPI.serializers import OrderSerializer, OrderItemSerializer, MenuItemsSerializer, UserSerializer, CartSerializer

import requests
from datetime import datetime

from LittleLemonAPI.paginations import CustomPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

permission_classes([IsAuthenticated])    
class OrderView(viewsets.ModelViewSet):
    
    queryset = OrderSerializer.Meta.model.objects.all()
    serializer_class = OrderSerializer
    
    # filters
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user','date']
    search_fields = ['user']
    ordering_fields = ['user', 'date']
    
    # pagination
    pagination_class = CustomPagination
    
    # throttle
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def retrieve(self, request, *args, **kwargs):
        user_id = Token.objects.get(key=request.auth.key).user_id
        
        order_obj=OrderSerializer.Meta.model.objects.filter(user=user_id).filter(id=self.kwargs['pk'])
        if order_obj:
            return super().retrieve(request, *args, **kwargs)
        else:
            return Response({"message":"The order requested doesn’t belong to the current user"}, 404)
        
    def list(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager').exists():
            return super().list(request, *args, **kwargs)
        else:
            user_id = Token.objects.get(key=request.auth.key).user_id
            if request.user.groups.filter(name='Delivery crew').exists():
                order_obj=OrderSerializer.Meta.model.objects.filter(delivery_crew=user_id)
            else:
                order_obj=OrderSerializer.Meta.model.objects.filter(user=user_id)
            serializer_class = OrderSerializer(order_obj, many=True)
            return Response(serializer_class.data, status=status.HTTP_200_OK)
 
    def create(self, request):
        # get authenticated user
        user_id = Token.objects.get(key=request.auth.key).user_id
        
        # get items stored in user's cart
        """
        url='http://127.0.0.1:8000/api/cart/menu-items'
        token = "Token " + str(Token.objects.get(key=request.auth.key))  
        cart = requests.get(url, headers={'Authorization': token}).json()
        """
       
        cart_list_obj = CartSerializer.Meta.model.objects.filter(user=user_id).all()
        serializer = CartSerializer(cart_list_obj, many=True)
        cart_list_json = serializer.data
        
        if cart_list_obj:
            # create new order
            total = 0
            user_obj = UserSerializer.Meta.model.objects.filter(id=user_id).first()
            order_obj = OrderSerializer.Meta.model.objects.create(user=user_obj, 
                                                              #delivery_crew=delivery_crew_obj, 
                                                              status=0, 
                                                              total=total, 
                                                              date=datetime.now().date()
                                                              )
            for item in cart_list_json:
                menuitem_obj = MenuItemsSerializer.Meta.model.objects.filter(id=item["menuitem"]).first()
                #menuitem_obj = MenuItemsSerializer.Meta.model.objects.filter(id=item.menuitem.id).first()
                OrderItemSerializer.Meta.model.objects.create(order=order_obj,
                                                          menuitem=menuitem_obj,
                                                          quantity=item["quantity"],
                                                          unit_price=item["unit_price"],
                                                          price=item["price"] )
                total+=item["price"]
        
            # update total value in the order
            order_obj.total=total
            order_obj.save()
        
            try:
                serializer_order = OrderSerializer(instance=order_obj)
                # delete cart
                cart_list_obj.delete()
                #requests.delete(url, headers={'Authorization': token}).json()
                return Response(data=serializer_order.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"message":"The order creation was failed"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"The user's cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, pk=None):
        if request.user.groups.filter(name='Manager').exists():
            order = self.get_queryset().filter(id=pk).first() # get instance
            if order:
                order.delete()
                return Response({"message":"Order eliminated succefully!"}, status=status.HTTP_200_OK)
            return Response({"error":"The order does not exist!"}, 404)
        else:
            return Response({"message":"Access denied"},403)
        
    def partial_update(self, request, *args, **kwargs):
        #order = self.get_queryset().filter(id=self.kwargs['pk']).first() # get instance
        order = self.get_object()
        data_input = request.data
        
        if order:
            # updates granted to a delivery crew member
            if request.user.groups.filter(name='Delivery crew').exists():
                order_status = data_input['status']
                if order_status:
                    a=int(data_input['status'])
                    b=int(order.status)
                    change_1 = (a!=b) and order_status
                    if change_1:
                        order.status=order_status
                        order.save()
                        serializer_order = OrderSerializer(instance=order)
                        data = {"message":"Order updated succefully!", "order": serializer_order.data}
                        return Response(data=data, status=status.HTTP_200_OK)
                    else:
                        serializer_order = OrderSerializer(instance=order)
                        data={"message":"There is no changes in the order that a delivery crew member can do", 
                              "order": serializer_order.data}
                        return Response(data=data, status=status.HTTP_200_OK)
                serializer_order = OrderSerializer(instance=order)
                data={"message":"Order not updated. Status field in blank", "order": serializer_order.data}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            
            # updates granted to a Manager
            elif request.user.groups.filter(name='Manager').exists():
                # update status
                # order_status = request.POST.get('status', None)
                
                order_status = data_input['status']
                a=int(data_input['status'])
                b=int(order.status)
                change_1 = (a!=b) and order_status and (a==0 or a==1)

                if change_1: 
                    order.status=order_status

                # update delivery crew
                if order.delivery_crew:
                    change_2 = order.delivery_crew.id != int(data_input['delivery_crew'])
                    if change_2:
                        delivery_crew_obj = UserSerializer.Meta.model.objects.filter(id=data_input['delivery_crew']).first()
                        order.delivery_crew = delivery_crew_obj
                else:
                    change_2 = True
                    delivery_crew_obj = UserSerializer.Meta.model.objects.filter(id=data_input['delivery_crew']).first()
                    order.delivery_crew = delivery_crew_obj
                    
                
                if change_1 or change_2:
                    order.save()
                    serializer_order = OrderSerializer(instance=order)
                    data = {"message":"Order updated succefully!", 
                            "order": serializer_order.data}
                    return Response(data=data, status=status.HTTP_200_OK)
                else:
                    serializer_order = OrderSerializer(instance=order)
                    data = {"message":"There is no changes in the order that a Manager can do", 
                            "order": serializer_order.data}
                    return Response(data=data, status=status.HTTP_200_OK)
            
            # updates granted to a customer
            else:
                item = OrderItemSerializer.Meta.model.objects.filter(order=order.id).filter(menuitem=data_input['menuitem']).first()
                if item:
                    quantity = int(data_input['quantity'])
                    if quantity and item.quantity != quantity:
                        item.quantity = quantity
                        item.price = quantity*item.unit_price
                        item.save()
                        
                        orderitem_list = OrderItemSerializer.Meta.model.objects.filter(order=order.id).all()
                        total = 0
                        for oi in orderitem_list:
                            total += oi.price
                        order.total=total
                        order.save()
                        
                        serializer_order = OrderSerializer(instance=order)
                        data = {"message":"Order updated succefully!", 
                                "order": serializer_order.data}
                        return Response(data=data, status=status.HTTP_200_OK)
                    else:
                        serializer_order = OrderSerializer(instance=order)
                        data={"message":"There is no changes in the order", 
                              "order": serializer_order.data}
                        return Response(data=data, status=status.HTTP_200_OK)
                return Response({"message":"Order item doesn't exist"}, 404)            
        return Response({'error':'The order does not exist!'},404)
    
    def update(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager').exists():
            obj = self.get_object()
            serializer = self.serializer_class(obj, data=request.data, partial=False)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"Access denied"},403)
            
