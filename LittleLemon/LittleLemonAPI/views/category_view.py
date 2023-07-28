from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework import viewsets
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from LittleLemonAPI.models import Category
from LittleLemonAPI.serializers import CategorySerializer

#@permission_classes([IsAuthenticated])    
class CategoryView(viewsets.ModelViewSet):
    
    serializer_class = CategorySerializer
    
    def get_queryset(self, pk=None):
        if pk is None:
            return self.get_serializer().Meta.model.objects
        return Response(self.get_serializer().Meta.model.objects.filter(id=pk).first(), status=status.HTTP_200_OK)
    
    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request):
            if request.user.groups.filter(name='Manager').exists():
                return super().create(request)
            else:
                return Response({"message":"Access denied"},403)
    
    def destroy(self, request, pk=None):
        if request.user.groups.filter(name='Manager').exists():
            category = self.get_queryset().filter(id=pk).first() # get instance
            if category:
                category.delete()
                return Response({'message':'Category eliminated succefully!'}, status=status.HTTP_200_OK)
            return Response({'error':'The category does not exist!'},404)
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