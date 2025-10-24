# News Django Project - AI Coding Agent Instructions

## Project Overview
A Django 5.0 news application with user authentication, article publishing, and comment functionality. Built for Heroku deployment using WhiteNoise for static files and environment-based configuration.

**Stack**: Django 5.0.14 · CustomUser (accounts) · PostgreSQL (via dj-database-url) · Crispy Forms + Bootstrap5 · WhiteNoise

## Architecture & Core Patterns

### App Structure
- **accounts**: Custom user model (`CustomUser` extends `AbstractUser`) with signup/login views
- **articles**: Core feature - Article CRUD + Comment creation on articles
- **pages**: Static pages (currently just homepage)
- **config**: Project settings, URL routing

### Key Design Decisions
- **Custom User Model** (`accounts/models.py`): Extended `AbstractUser` with `age` field. Always use `settings.AUTH_USER_MODEL` in ForeignKeys (see `articles/models.py`)
- **Comment Pattern** (`articles/views.py`): Two-view GET/POST pattern (`CommentGet`/`CommentPost`) composed in `ArticleDetailView` for handling detail display + comment form
- **Access Control**: Use `UserPassesTestMixin` with `test_func()` to verify article author (see `ArticleDeleteView`, `ArticleUpdateView`)
- **Static Files**: WhiteNoise configured with `CompressedManifestStaticFilesStorage` for production

### URL Routing
```
/admin/ → Django admin
/accounts/ → include(accounts.urls) + include(django.contrib.auth.urls) [both paths share prefix]
/articles/ → include(articles.urls)
/ → include(pages.urls)
```

## Critical Developer Workflows

### Development Setup
```powershell
# Install dependencies (requires Python 3.8+)
pip install -r requirements.txt

# Configure environment (copy defaults from settings.py)
# Create .env file or set environment variables:
# - SECRET_KEY (required for production)
# - DEBUG=True (for development)
# - DATABASE_URL (defaults to SQLite if unset)

# Run migrations
python manage.py migrate

# Start dev server
python manage.py runserver
```

### Database Migrations
- Located in `accounts/migrations/`, `articles/migrations/`, `pages/migrations/`
- After model changes: `python manage.py makemigrations <app_name>` → `python manage.py migrate`
- Schema: `Article` has ForeignKey to `CustomUser` with `related_name='articles'` (implicit); `Comment` has FK to both with `related_name='comments'` for articles

### Testing & Debugging
- Test files: `accounts/tests.py`, `articles/tests.py`, `pages/tests.py` (currently minimal)
- Run tests: `python manage.py test`
- Django shell: `python manage.py shell` (useful for testing querysets)
- Email backend: Console output (see `settings.py` EMAIL_BACKEND) - password resets print to console

### Deployment
- **Procfile**: Gunicorn worker configured (for Heroku)
- Static files: Run `python manage.py collectstatic` before deploy
- Environment: `CSRF_TRUSTED_ORIGINS` set for `*.herokuapp.com`
- Database: Uses `dj-database-url` to parse `DATABASE_URL` env var for PostgreSQL

## Project-Specific Conventions

### Model & Admin Patterns
- Always include `__str__()` methods (see `Article`, `Comment`)
- Always define `get_absolute_url()` using `reverse()` for detail views
- Register models in `admin.py` for backend access

### Form Patterns
- Forms inherit from `UserCreationForm`/`UserChangeForm` for auth (see `accounts/forms.py`)
- Comment form via `CommentForm` in `articles/forms.py` (validates comment text)
- Forms use Crispy Bootstrap5 template pack in templates

### View Patterns
- **CRUD Views**: Use Generic Views (`ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`)
- **Authentication**: `LoginRequiredMixin` required for article views
- **Authorization**: `UserPassesTestMixin` + `test_func()` for owner-only access
- **Composite Views**: See `ArticleDetailView` - uses `View` base class to delegate GET/POST to separate view classes

### Template Structure
- Base template: `templates/base.html` (inherited by all)
- App templates: `templates/article_list.html`, `article_detail.html`, `article_new.html`, `article_edit.html`, `article_delete.html`
- Auth templates: `templates/registration/login.html`, `signup.html`, password reset templates
- Homepage: `templates/home.html`

### Settings & Environment
- **Environment Variables** (via `environs` library):
  - `SECRET_KEY`: Production key (has default, change in production)
  - `DEBUG`: Boolean, default False
  - `DATABASE_URL`: Full connection string (uses PostgreSQL on Heroku)
- **Crispy Forms**: Bootstrap5 configured globally (`CRISPY_TEMPLATE_PACK = "bootstrap5"`)
- **Timezone**: Asia/Karachi (affects all DateTimeField behavior)

## Cross-Component Communication & Integration Points

### User Authentication Flow
1. Signup: `SignUpView` → `CustomUserCreationForm` → creates `CustomUser` → redirects to login
2. Login: Django's built-in auth views (included via `django.contrib.auth.urls`)
3. User metadata: Custom `age` field available on authenticated user (`request.user`)

### Article-Comment Relationship
- `Article.comments.all()` returns comments (inverse relation via `Comment.related_name='comments'`)
- `Comment.author` and `Comment.article` both FK to user/article
- Posting comment updates `comment.author = self.request.user` in view (not form)

### Admin Integration
- Register all models to allow CMS-style content management
- `CustomUser` should be registered with custom admin form (`CustomUserChangeForm`)

## Quick Reference: File Locations
- **Settings & Config**: `config/settings.py`, `config/urls.py`, `config/wsgi.py`
- **Custom User Logic**: `accounts/models.py`, `accounts/forms.py`, `accounts/views.py`
- **Article/Comment Logic**: `articles/models.py`, `articles/forms.py`, `articles/views.py`
- **Templates**: `templates/` (shared base + app-specific)
- **Static Files**: `static/` (CSS, JS, images) → collected to `staticfiles/` for production

## Common Tasks & Patterns

### Adding a New Article Field
1. Update `Article` model in `articles/models.py`
2. Run `python manage.py makemigrations articles`
3. Add field to `ArticleCreateView.fields` and `ArticleUpdateView.fields` if user-editable
4. Update form in `articles/forms.py` if custom validation needed
5. Update templates (`article_list.html`, `article_detail.html`)

### Restricting Views to Authenticated Users
```python
from django.contrib.auth.mixins import LoginRequiredMixin

class YourView(LoginRequiredMixin, View):
    # Auto-redirects unauthenticated users to login
```

### Adding Author-Only Access
```python
from django.contrib.auth.mixins import UserPassesTestMixin

class YourView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.author  # Common pattern
```

## Known Limitations & Notes
- Email backend set to console (not production-ready for sending emails)
- No pagination on article lists (consider adding if large datasets)
- Comment form is simple text field (no rich text editor)
- Static files in production require `collectstatic` step (handled by WhiteNoise)
