from django.urls import path
from .views import *
 
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', user_logout, name="logout"),
    path('author_post_pets/', author_post_pets, name="author_post_pets"),
    path('profile/', UserAccountUpdateView.as_view(), name='profile' ),
    path('profile/pass_change/', PasswordChangeView.as_view(), name='pass_change')
]