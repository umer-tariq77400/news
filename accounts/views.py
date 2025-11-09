from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, CustomUserChangeForm


class SignUpView(CreateView):
    """A view to handle user sign-up.
    Args:
        CreateView (class): Django generic create view for creating a new object.
    """

    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class ProfileView(DetailView):
    """A view to display user profile information.

    Args:
        DetailView (class): Django generic detail view for displaying a single object.
    """

    model = get_user_model()
    template_name = "registration/profile.html"


class EditProfileView(UpdateView):
    """A view to edit user profile information.
    Args:
        UpdateView (class): Django generic update view for updating an existing object.
    """

    form_class = CustomUserChangeForm
    success_url = reverse_lazy("profile")
    template_name = "registration/edit_profile.html"

    def get_object(self):
        return self.request.user
