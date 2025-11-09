from django.urls import path
from .views import SignUpView, ProfileView, EditProfileView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name='signup'),
    path("edit_profile/", EditProfileView.as_view(), name='edit_profile'),
    path("profile/<int:pk>/", ProfileView.as_view(), name='profile'),
]
