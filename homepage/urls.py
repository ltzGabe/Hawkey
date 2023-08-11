from django.contrib.auth.decorators import login_required
from django.urls import path, include
from . import views
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views

from django_email_verification import urls as email_urls
urlpatterns = [
    path('products/<int:currentTab>/<str:product>/',views.Product.as_view(), name="Product"),
    path('products/<int:currentTab>/',views.Tracker.as_view(), name="Tracker"),
    path('', RedirectView.as_view(url='products/0'),name="Landing"),
    path('about/', views.About.as_view(), name="About"),
    path('contactUs/', views.Contact.as_view(), name="ContactUs"),
    path('donate/', views.Donate.as_view(), name="Donate"),
    path('register/', views.register, name="register"),
    path('login/', views.loginUser.as_view(), name="loginUser"),
    path('account/', login_required(login_url="loginUser")(views.Account.as_view()), name="Account"),
    path('logout/', views.logoutUser, name="logout"),
    path('delete/', views.deleteUser, name="delete"),
    path('email/', include(email_urls)),	
    path('reset/', auth_views.PasswordResetView.as_view(template_name="homepage/password_reset.html"), name='password_reset', ),
    path('reset_sent/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name = "password_reset_complete"),
    
]
