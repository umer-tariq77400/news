from django.contrib import admin
from .models import Article, Comment, Category

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1

class ArticleAdmin(admin.ModelAdmin):
    inlines = [CommentInline]

    list_display = (
        'title',
        'category',
        'author',
    )

admin.site.register(Article, ArticleAdmin)

admin.site.register(Category)

class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'article',
        'comment',
        'author',
    )

admin.site.register(Comment, CommentAdmin)
