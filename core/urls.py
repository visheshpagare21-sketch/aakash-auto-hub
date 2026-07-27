from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('categories/', views.categories, name='categories'),
    path('category/<slug:slug>/', views.category_detail, name='category-detail'),
    path('categories/<slug:slug>/', views.legacy_category_detail),
    path('product/<slug:slug>/', views.product_detail, name='product-detail'),
    path('product/<slug:slug>/enquiry/', views.log_whatsapp_enquiry, name='log-whatsapp-enquiry'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path("robots.txt", views.robots_txt, name="robots"),
]
