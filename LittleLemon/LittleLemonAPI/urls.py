from django.urls import path
from rest_framework.routers import DefaultRouter

from LittleLemonAPI.views.category_view import CategoryView
from LittleLemonAPI.views.menuitem_view import MenuItemView
from LittleLemonAPI.views.user_view import Managers, DeliveryCrew, UserView, GroupList
from LittleLemonAPI.views.cart_view import CartView
from LittleLemonAPI.views.order_view import OrderView

router = DefaultRouter(trailing_slash=False)
router.register(r'categories', CategoryView, basename='categories')
router.register(r'menu-items', MenuItemView, basename='menu-items')
router.register(r'users', UserView, basename='user')
router.register(r'orders', OrderView, basename='orders')

#router.register(r'cart/menu-items', CartManagementView, basename='cart')
#router.register(r'cart/menu-item', CartView, basename='cart')
#router.register(r'cart/menu-items', CartView, basename='cart-view')

urlpatterns = router.urls + [
    path('groups', GroupList.as_view()),
    path('groups/delivery-crew/users', DeliveryCrew.as_view()),
    path('groups/delivery-crew/users/<int:pk>', DeliveryCrew.as_view()),
    path('groups/manager/users', Managers.as_view()),
    path('groups/manager/users/<int:pk>', Managers.as_view()),
        
    path('cart/menu-items', CartView.as_view()),
    
]