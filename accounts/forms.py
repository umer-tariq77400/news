from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Form for creating a new user.

    Args:
        UserCreationForm (Form): Django form for creating a new user.
    """
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "username", "email")


class CustomUserChangeForm(UserChangeForm):
    """Form for updating an existing user.
    Args:
        UserChangeForm (Form): Django form for updating an existing user.
    """
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "username", "email", "bio", "profile_image", "x_link", "linkedin_link", "github_link", "website_link")