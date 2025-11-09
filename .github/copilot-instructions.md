# News Django Project - AI Coding Agent Instructions

## Project Overview

A Django 5.0 news application with user authentication, article publishing, and comment functionality. Built for Heroku deployment using WhiteNoise for static files and environment-based configuration.

**Stack**: Django 5.0.14 · CustomUser (accounts) · PostgreSQL (via dj-database-url) · Crispy Forms + Bootstrap5 · WhiteNoise · Pillow (image uploads)

## Architecture & Core Patterns

### App Structure

- **accounts**: Custom user model (`CustomUser` extends `AbstractUser`) with rich profiles (bio, social links, profile image); signup/login views + profile management
- **articles**: Core feature - Article CRUD + Comments; includes Categories for article organization; handles media uploads (cover images)
- **pages**: Static pages (currently homepage) with contact form capability
- **config**: Central settings, URL routing, middleware (WhiteNoise, security)

### Key Design Decisions

1. **Custom User Model** (`accounts/models.py`): Extended `AbstractUser` with profile fields (`bio`, `profile_image`, social links). **Always use `settings.AUTH_USER_MODEL` in ForeignKeys** (see `articles/models.py` Article model).
2. **Article-Comment Architecture**: Two-step pattern in `articles/views.py`:
   - `CommentGet`: Handles detail display + form initialization
   - `CommentPost`: Handles comment submission
   - Composed via `ArticleDetailView` (View base class delegates GET/POST to these views)
   - **Author assignment happens in view (`form.instance.author = request.user`)**, not in form
3. **Access Control**: Use `UserPassesTestMixin` + `test_func()` to verify article author (see `ArticleDeleteView.test_func()`, `ArticleUpdateView.test_func()`)
4. **Media Handling**: Images upload to `media/` (articles → `article_covers/`, profiles → `profile_images/`); served in development via `django.conf.urls.static`
5. **Admin Integration**: Uses inline comments in Article admin; filtered list display for easy content management
6. **Static Files**: WhiteNoise configured with `CompressedManifestStaticFilesStorage` for production; runs collectstatic before deploy

### URL Routing

```
/admin/                      → Django admin panel
/accounts/                   → accounts.urls (signup, edit_profile, profile) + django.contrib.auth.urls (login, logout, password reset)
/articles/                   → articles.urls (article_list, article_detail, article_new, article_edit, article_delete)
/                            → pages.urls (homepage, contact)
/media/ (dev only)          → Served by django.conf.urls.static (staticfiles in production)
```

## Critical Developer Workflows

### Development Setup

```powershell
# Install dependencies (requires Python 3.8+)
pip install -r requirements.txt

# Create .env file or set environment variables (optional for dev, required for prod):
# - SECRET_KEY (prod only; has insecure default in dev)
# - DEBUG=True (for development; defaults to False in production)
# - DATABASE_URL (defaults to SQLite 'sqlite:///db.sqlite3' if unset; use for PostgreSQL in prod)
# - ALLOWED_HOSTS (comma-separated; default: localhost,127.0.0.1)

# Initialize database
python manage.py migrate

# Create superuser for admin panel
python manage.py createsuperuser

# Collect static files (needed before production deploy; dev uses STATIC_ROOT collection)
python manage.py collectstatic --noinput

# Start dev server (runs on http://localhost:8000 by default)
python manage.py runserver
```

### Database Migrations

- Migration files: `accounts/migrations/`, `articles/migrations/`, `pages/migrations/`
- After model changes: `python manage.py makemigrations <app_name>` → `python manage.py migrate`
- **Schema relationships**:
  - `Article.author` → FK to `CustomUser` (no explicit related_name, so access via `customuser.article_set.all()`)
  - `Article.category` → FK to `Category` (related_name='articles', so `category.articles.all()`)
  - `Comment.article` → FK to `Article` (related_name='comments', so `article.comments.all()`)
  - `Comment.author` → FK to `CustomUser` (no related_name, so `customuser.comment_set.all()`)

### Testing & Debugging

- Test files exist but are minimal: `accounts/tests.py`, `articles/tests.py`, `pages/tests.py`
- Run all tests: `python manage.py test`
- Run app-specific tests: `python manage.py test accounts` (or `articles`, `pages`)
- Django shell (useful for testing querysets): `python manage.py shell`
- Email backend: Console output (see `settings.EMAIL_BACKEND`) - password resets print to console during development

### Deployment (Heroku)

- **Procfile**: Gunicorn worker already configured (`web: gunicorn config.wsgi`)
- **Static files**: Run `python manage.py collectstatic --noinput` before deploy (WhiteNoise handles compression)
- **Environment setup**: Set on Heroku via `heroku config:set`:
  - `SECRET_KEY=<new-secure-key>`
  - `DEBUG=False`
  - `DATABASE_URL=<PostgreSQL connection string>` (Heroku adds automatically with postgres add-on)
  - `ALLOWED_HOSTS=*.herokuapp.com`
- **CSRF**: `CSRF_TRUSTED_ORIGINS` pre-configured for `*.herokuapp.com` domains
- **Security**: Production (DEBUG=False) auto-enables: HTTPS redirect, secure cookies, HSTS headers

## Project-Specific Conventions

### Model & Admin Patterns

- **Always include `__str__()` methods** for admin list display (see `Article.__str__()`, `Comment.__str__()`)
- **Always define `get_absolute_url()` using `reverse()`** for detail view shortcuts (required for CreateView/UpdateView redirects)
- **Register all models in `admin.py`**:
  - Use `ModelAdmin` subclasses for custom display/filtering (see `ArticleAdmin` with `CommentInline`)
  - Use `admin.TabularInline` for related objects (see `CommentInline` in ArticleAdmin)
  - Set `list_display` to show key fields in list view

### Form Patterns

- **Auth forms** (`CustomUserCreationForm`, `CustomUserChangeForm` in `accounts/forms.py`):
  - Inherit from Django's `UserCreationForm`/`UserChangeForm`
  - Set `Meta.model = CustomUser` and specify `Meta.fields` tuple
- **Comment form** (`CommentForm` in `articles/forms.py`):
  - Inherit from `forms.ModelForm`
  - Set `Meta.model = Comment` and `Meta.fields = ("comment",)` (exclude author/article; assigned in view)
- **Forms use Crispy Bootstrap5** template pack globally (set in `settings.CRISPY_TEMPLATE_PACK = "bootstrap5"`)

### View Patterns

- **CRUD Views**: Use Django Generic Views (`ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`)
  - Always set `model`, `template_name`, `fields` (or use form_class), `success_url`
  - Example: `ArticleCreateView` sets `model = Article` and specifies editable `fields`
- **Authentication**: Add `LoginRequiredMixin` to restrict access (auto-redirects to login)
- **Authorization**: Use `LoginRequiredMixin, UserPassesTestMixin` with `test_func()` to verify ownership:
  ```python
  def test_func(self):
      obj = self.get_object()
      return self.request.user == obj.author
  ```
- **Form submission handling**: Override `form_valid()` to set user/object relationships before save:
  ```python
  def form_valid(self, form):
      form.instance.author = self.request.user  # Set author in view
      return super().form_valid(form)
  ```
- **Composite Views** (see `ArticleDetailView`): Use `View` base class to delegate GET/POST to separate view classes:
  ```python
  class ArticleDetailView(LoginRequiredMixin, View):
      def get(self, request, *args, **kwargs):
          return CommentGet.as_view()(request, *args, **kwargs)
      def post(self, request, *args, **kwargs):
          return CommentPost.as_view()(request, *args, **kwargs)
  ```

### Template Structure

- **Base template**: `templates/base.html` (inherited by all pages)
- **Article templates**:
  - `templates/article_list.html` - list view (public)
  - `templates/article_detail.html` - detail + comment form (login required)
  - `templates/article_new.html` - article creation form
  - `templates/article_edit.html` - article edit form
  - `templates/article_delete.html` - delete confirmation
- **Auth templates** (Django defaults in `templates/registration/`):
  - `login.html`, `signup.html`, password reset templates
- **Pages templates**:
  - `templates/home.html` - homepage
  - `templates/contact.html`, `contact_success.html` - contact form
- All templates use Bootstrap5 via Crispy Forms filters: `{% load crispy_forms_tags %}`

### Settings & Environment

- **Environment Variables** (via `environs` library, read from `.env` file):
  - `SECRET_KEY`: Django secret (has insecure default for dev; change for production)
  - `DEBUG`: Boolean, defaults to False (set True for development)
  - `DATABASE_URL`: Full DB connection string (defaults to SQLite if unset; PostgreSQL on Heroku)
  - `ALLOWED_HOSTS`: Comma-separated list (defaults to localhost,127.0.0.1)
  - `CSRF_TRUSTED_ORIGINS`: Comma-separated list (pre-configured for \*.herokuapp.com in production)
- **Crispy Forms**: `CRISPY_TEMPLATE_PACK = "bootstrap5"` (global config)
- **Timezone**: `TIME_ZONE = "Asia/Karachi"` (affects all DateTimeField behavior)
- **Media/Static**:
  - Static files: `STATIC_URL = "/static/"`, `STATIC_ROOT = BASE_DIR / "staticfiles"`
  - Media uploads: `MEDIA_URL = "/media/"`, `MEDIA_ROOT = BASE_DIR / "media"`
  - WhiteNoise auto-collects static files on production startup

## Cross-Component Communication & Integration Points

### User Authentication Flow

1. **Signup**: `SignUpView` → `CustomUserCreationForm` → creates `CustomUser` → redirects to login
2. **Login**: Django's built-in views via `django.contrib.auth.urls` (included at `/accounts/`)
3. **Profile Management**: `ProfileView` displays user + their articles via reverse relation `customuser.article_set.all()`; `EditProfileView` allows editing all profile fields
4. **Password Reset**: Uses Django's default views; emails print to console (EMAIL_BACKEND set to console)

### Article-Comment Relationship

- **Creating articles**: `ArticleCreateView` sets `form.instance.author = request.user` before save
- **Viewing articles**: `ArticleDetailView` (requires login) delegates to `CommentGet` for GET, `CommentPost` for POST
- **Posting comments**: `CommentPost` creates comment with `comment.author = request.user` and `comment.article = self.object`
- **Accessing comments**: `article.comments.all()` (via `related_name='comments'`); each comment has `.author` and `.article` FK
- **Display in templates**: `article_detail.html` loops through `article.comments.all()` and includes comment form

### Article Lifecycle

- **Create**: POST to `/articles/new/` → `ArticleCreateView` → `article_new.html` form with title, body, category, cover_image
- **List**: GET `/articles/` → `ArticleListView` → `article_list.html` (public view, no login required)
- **Read**: GET `/articles/<id>/` → `ArticleDetailView` (login required) → shows article + comments + comment form
- **Update**: GET/POST `/articles/<id>/update/` → `ArticleUpdateView` (author-only) → `article_edit.html`
- **Delete**: GET/POST `/articles/<id>/delete/` → `ArticleDeleteView` (author-only) → `article_delete.html` confirmation

### Admin Integration

- **Article admin**: Shows `ArticleAdmin` with inline `CommentInline` (edit comments directly in article detail)
- **List display**: Article, Category, Author (filtered for easy scanning)
- **All models registered**: Article, Comment, Category, CustomUser

## Quick Reference: File Locations

- **Settings & Config**: `config/settings.py`, `config/urls.py`, `config/wsgi.py`
- **Custom User Logic**: `accounts/models.py`, `accounts/forms.py`, `accounts/views.py`, `accounts/urls.py`
- **Article/Comment Logic**: `articles/models.py`, `articles/forms.py`, `articles/views.py`, `articles/urls.py`, `articles/admin.py`
- **Pages**: `pages/models.py`, `pages/views.py`, `pages/urls.py`
- **Templates**: `templates/` (shared base + app-specific subdirectories)
- **Static Files**: `static/` (CSS, JS, images) → collected to `staticfiles/` for production

## Common Tasks & Patterns

### Adding a New Article Field

1. Add field to `Article` model in `articles/models.py`
2. Run `python manage.py makemigrations articles` → `python manage.py migrate`
3. Add field to `ArticleCreateView.fields` and `ArticleUpdateView.fields` if user-editable
4. Update `articles/forms.py` if custom validation needed
5. Update templates (`article_list.html`, `article_detail.html`, `article_edit.html`) to display/edit field
6. Optionally add to `ArticleAdmin.list_display` in `articles/admin.py`

### Extending the CustomUser Model

1. Add field to `CustomUser` model in `accounts/models.py`
2. Run `python manage.py makemigrations accounts` → `python manage.py migrate`
3. Update `CustomUserChangeForm.Meta.fields` in `accounts/forms.py` if user-editable
4. Update `edit_profile.html` template to include field
5. Update `profile.html` to display field

### Restricting Views to Authenticated Users

```python
from django.contrib.auth.mixins import LoginRequiredMixin

class YourView(LoginRequiredMixin, ListView):
    model = YourModel
    # Auto-redirects unauthenticated users to login
```

### Adding Author-Only Access

```python
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

class YourView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = YourModel

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.author
```

### Creating a New Admin Inline

```python
# In articles/admin.py
class YourInline(admin.TabularInline):  # or admin.StackedInline
    model = YourRelatedModel
    extra = 1  # Number of empty forms to display

class YourAdmin(admin.ModelAdmin):
    inlines = [YourInline]
    list_display = ('field1', 'field2', 'field3')

admin.site.register(YourModel, YourAdmin)
```

## Known Limitations & Notes

- Email backend set to console (not production-ready for sending emails; override `EMAIL_BACKEND` in production)
- No pagination on article lists (consider adding `paginate_by` to `ArticleListView` if large datasets)
- Comment form is simple text field (no rich text editor; consider adding TinyMCE or similar)
- Static files in production require `collectstatic` step (automated by WhiteNoise + Procfile on Heroku)
- No full-text search implemented (consider adding Django Haystack or Elasticsearch for larger datasets)
