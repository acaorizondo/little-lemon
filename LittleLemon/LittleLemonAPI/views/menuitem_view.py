from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from LittleLemonAPI.serializers import MenuItemsSerializer
from LittleLemonAPI.paginations import CustomPagination

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

#from django_filters import rest_framework as filters
    
permission_classes([IsAuthenticated])    
class MenuItemView(viewsets.ModelViewSet):
    
    serializer_class = MenuItemsSerializer
    queryset = MenuItemsSerializer.Meta.model.objects.all()
    
    # filters
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['title', 'category__title']
    search_fields = ['title']
    ordering_fields = ['title', 'category__title', 'price']
    
    # pagination
    pagination_class = CustomPagination
    
    # throttle
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    """
    # to keep the default implementation to let filters work
    def get_queryset(self, pk=None):
        if pk is None:
            return self.get_serializer().Meta.model.objects.all()
        return Response(self.get_serializer().Meta.model.objects.filter(id=pk).first(), status=status.HTTP_200_OK)
    
    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many = True)        
        return Response(serializer.data, status=status.HTTP_200_OK)
    """
    
    def create(self, request):
            if request.user.groups.filter(name='Manager').exists():
                return super().create(request)
            else:
                return Response({"message":"Access denied"},403)
    
    def destroy(self, request, pk=None):
        if request.user.groups.filter(name='Manager').exists():
            menuitem = self.get_queryset().filter(id=pk).first() # get instance
            if menuitem:
                menuitem.delete()
                return Response({'message':'Menu item eliminated succefully!'}, status=status.HTTP_200_OK)
            return Response({'error':'The menu item does not exist!'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"Access denied"},403)
    
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
        
    def partial_update(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager').exists():
            obj = self.get_object()
            serializer = self.serializer_class(obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"Access denied"},403)