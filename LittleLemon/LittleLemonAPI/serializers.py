from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.validators import UniqueTogetherValidator

from decimal import Decimal

from .models import Category, MenuItem, Order, Cart, OrderItem
from django.contrib.auth.models import User, Group
import bleach

class CategorySerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        max_length=255,
        validators=[UniqueValidator(queryset=Category.objects.all())]
        )
    
    def validate_title(self, value):
        return bleach.clean(value)
    
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']
        
#--------------------------------------------------------------------------------------------

class MenuItemsSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        max_length=255,
        validators=[UniqueValidator(queryset=MenuItem.objects.all())]
        )
    featured = serializers.BooleanField()
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    
    def validate(self, attrs):
        if(attrs['price']<0):
            raise serializers.ValidationError('Price cannot be negative')
        
        # sanitize fields
        attrs['title'] = bleach.clean(attrs['title'])
        
        return super().validate(attrs)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']
        depth = 1
        
#--------------------------------------------------------------------------------------
class GroupSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Group
        fields = ['id', 'name']
        #fields = '__all__'
        #depth = 1

class UserSerializer(serializers.ModelSerializer):
    
    groups = GroupSerializer(many=True, read_only=True)
       
    class Meta:
        model = User
        fields = ['id','username','email','groups']
        #fields = '__all__'
        #depth = 1
        
#--------------------------------------------------------------------------------------
        
class CartSerializer(serializers.ModelSerializer):
    
    price = serializers.SerializerMethodField(method_name='calculate_price')

    class Meta:
        model = Cart
        fields = ['user','menuitem','quantity','unit_price','price']
        #fields = '__all__'
        #depth = 1
    
    def calculate_price(self, cart:Cart):
        return round(cart.unit_price*cart.quantity,2)
#---------------------------------------------------------------------------------------
class OrderItemSerializer(serializers.ModelSerializer):
    #items = OrderSerializer(many=True, read_only=True)
    menuitem = MenuItemsSerializer()
    
    class Meta:
        model = OrderItem
        fields = ['order','menuitem','quantity','unit_price','price',]
        #depth = 1

class OrderSerializer(serializers.ModelSerializer):
 
    items = OrderItemSerializer(many=True, read_only=False)
    user = UserSerializer()
    delivery_crew = UserSerializer()
    
    class Meta:
        model = Order
        #fields = '__all__'
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'items']
        #depth = 1


        


        


    