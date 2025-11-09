from django.urls import path

from .views import HomePageView, ContactPageView, ContactSuccessView

urlpatterns = [
    path("", HomePageView.as_view(), name='home'),
    path("contact/", ContactPageView.as_view(), name='contact'),
    path("contact/success/", ContactSuccessView.as_view(), name='contact_success'),
]
