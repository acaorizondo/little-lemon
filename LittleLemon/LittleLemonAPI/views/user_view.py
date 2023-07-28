from django.contrib.auth.models import User, Group
from LittleLemonAPI.serializers import UserSerializer, GroupSerializer

from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.core import serializers

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

@permission_classes([IsAuthenticated])    
class UserView(viewsets.ModelViewSet):
    
    serializer_class = UserSerializer
    
     # filters
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['groups__name']
    search_fields = ['username']
    ordering_fields = ['username']
    
    def get_queryset(self, pk=None):
        if pk is None:
            return self.get_serializer().Meta.model.objects
        return Response(self.get_serializer().Meta.model.objects.filter(id=pk).first(), status=status.HTTP_200_OK)
    
    def list(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager').exists():
            return super().list(request, *args, **kwargs)
        else:
            return Response({"message":"Access denied"},403)
    
    """
    def list(self, request):
        if request.user.groups.filter(name='Manager').exists():
            serializer = self.get_serializer(self.get_queryset(), many = True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message":"Access denied"},403)
    """
    
class GroupList(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    
"""
class ManagersList(generics.ListAPIView):
    queryset = User.objects.filter(groups__name='Manager').values()
    serializer_class = UserSerializer
    
class DeliveryCrewList(generics.ListAPIView):
    queryset = User.objects.filter(groups__name='Delivery crew').values()
    serializer_class = UserSerializer
"""  
@permission_classes([IsAuthenticated])
class Managers(APIView):
    def get(self, request, format=None):
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            queryset = User.objects.filter(groups__name='Manager').values()
            serializer_class = UserSerializer(queryset, many=True)
            return Response(serializer_class.data)
        else:
            return Response({"message":"Access denied"},403)
    
    def post(self, request, format=None):
        if request.user.groups.filter(name='Manager').exists() or  request.user.is_superuser:
            username = request.data['username']
            if username:
                user = get_object_or_404(User, username=username)
                managers = Group.objects.get(name="Manager")
                managers.user_set.add(user)
                return Response({"message":"ok"}, status.HTTP_201_CREATED)
            return Response({"message":"error"}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"Access denied"},403)
        
    def delete(self, request, pk, format=None):
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            user = get_object_or_404(User, pk=pk)
            managers = Group.objects.get(name="Manager")
            if user.groups.filter(name="Manager").exists():
                managers.user_set.remove(user)
                return Response({"message":"User removed from Manager Group"}, status.HTTP_200_OK)
            else:
                return Response({"message":"User requested is not in Manager Group"}, 404)
        else:
            return Response({"message":"Access denied"},403)
        
@permission_classes([IsAuthenticated])
class DeliveryCrew(APIView):
    def get(self, request, format=None):
        if request.user.groups.filter(name='Manager').exists():
            queryset = User.objects.filter(groups__name='Delivery crew').values()
            serializer_class = UserSerializer(queryset, many=True)
            return Response(serializer_class.data)
        else:
            return Response({"message":"Access denied"},403)
    
    def post(self, request, format=None):
        if request.user.groups.filter(name='Manager').exists():
            username = request.data['username']
            if username:
                user = get_object_or_404(User, username=username)
                managers = Group.objects.get(name="Delivery crew")
                managers.user_set.add(user)
                return Response({"message":"User added to Delivery Group"}, status.HTTP_201_CREATED)
            return Response({"message":"error"}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"Access denied"},403)
        
    def delete(self, request, pk, format=None):
        if request.user.groups.filter(name='Manager').exists():
            user = get_object_or_404(User, pk=pk)
            delivery = Group.objects.get(name="Delivery crew")
            if user.groups.filter(name="Delivery crew").exists():
                delivery.user_set.remove(user)
                return Response({"message":"User removed from Delivery Group"}, status.HTTP_200_OK)
            else:
                return Response({"message":"User requested is not in Delivery Group"}, 404)
        else:
            return Response({"message":"Access denied"},403)

    
        
    
    