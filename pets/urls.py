from . import views
from django.urls import path

urlpatterns = [
    path('adopt/<int:id>/', views.adopt_pet, name='adopt_pet'), 
    path('profile_history/', views.profile_history, name='profile_history'),

    path('add/',views.add_post_CreateView.as_view(),name="add_post"),
    path('edit/<int:post_id>', views.EditPostView.as_view(), name='edit_post'),
    path('delete/<int:post_id>', views.DeletePostView.as_view(), name='delete_post'),
]