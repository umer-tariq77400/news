from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from .forms import ContactForm
from .models import ContactSubmission
from django.contrib import messages


class HomePageView(TemplateView):
    template_name = "home.html"


class ContactPageView(CreateView):
    model = ContactSubmission
    form_class = ContactForm
    template_name = "contact.html"
    success_url = reverse_lazy("contact_success")

    def form_valid(self, form):
        messages.success(self.request, "Thank you! Your message has been sent successfully.")
        return super().form_valid(form)


class ContactSuccessView(TemplateView):
    template_name = "contact_success.html"
