from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),

    # category filter
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),

    # cart
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),

    # auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # checkout
    path('checkout/', views.checkout, name='checkout'),

    # detail
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]

