from django.views.generic import ListView, DetailView
from django.views.generic.edit import DeleteView, UpdateView, CreateView
from django.urls import reverse_lazy
from .models import Article

class ArticleListView(ListView):
    model = Article
    template_name = "article_list.html"

class ArticleDetailView(DetailView):
    model = Article
    template_name = "article_detail.html"

class ArticleDeleteView(DeleteView):
    model = Article
    template_name = "article_delete.html"
    success_url = reverse_lazy("article_list")

class ArticleUpdateView(UpdateView):
    model = Article
    template_name = "article_edit.html"
    fields = ['title', 'body']
    success_url = "/articles/"

class ArticleCreateView(CreateView):
    model = Article
    template_name = "article_new.html"
    fields = ["title", "author", "body"]