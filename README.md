# Footwear E-commerce

Django storefront for footwear: home page with featured destinations, catalog by gender (women / men / kids), shopping bag, checkout, and order history. Uses PostgreSQL and Django’s built-in user authentication.

## Stack

| Piece | Notes |
|--------|--------|
| **Python / Django** | Django **5.1.x** (see `config/settings.py` header) |
| **Database** | **PostgreSQL** (`django.db.backends.postgresql`) |
| **Media** | Product and banner images via `ImageField` → `media/` (gitignored) |

There is no `requirements.txt` in the repo yet. Install at minimum:

- `Django~=5.1`
- `psycopg2-binary` (or `psycopg`) for PostgreSQL
- `Pillow` (required for `ImageField`)

Example:

```bash
pip install "Django~=5.1" psycopg2-binary Pillow
```

Consider adding a `requirements.txt` or `pyproject.toml` and pinning versions for reproducible installs.

## Project layout

| Path | Role |
|------|------|
| `config/` | Django project settings, root `urls.py`, `wsgi.py` |
| `store/` | Home page (`Destination` model, hero/landing content) |
| `categories/` | Catalog (`WFM` / `MFM` / `KFM` products, bag, purchases, orders) |
| `accounts/` | Register, login, logout |
| `templates/` | Shared HTML templates |
| `static/` | CSS, JS, images served in development via `STATICFILES_DIRS` |
| `calc/` | Empty placeholder app; **not** listed in `INSTALLED_APPS` |

## URL map

| URL prefix | App | Purpose |
|------------|-----|---------|
| `/` | `store` | Home |
| `/admin/` | Django | Admin site |
| `/accounts/` | `accounts` | `register`, `login`, `logout` (no trailing slash in paths as configured) |
| `/catalog/` | `categories` | `women/`, `men/`, `kids/`, bag, checkout, order history |

Media files are exposed under `MEDIA_URL` (`/media/`) when using `runserver` with the default `urls.py` setup.

## Local setup

### 1. Clone and virtual environment

```bash
cd footwear-ecommerce
python -m venv .venv
```

On Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies (see **Stack** above).

### 2. Database

Create a PostgreSQL database and user, then point Django at them.

**Security:** `config/settings.py` currently contains a concrete database configuration. For any shared or production repo you should **move credentials to environment variables** (or `local_settings.py`, which is gitignored) and never commit secrets. Use a `.env` file (gitignored) and load it in settings if you adopt `django-environ` or similar.

After the database is reachable:

```bash
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
```

### 3. Run the dev server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

### 4. Static and media

- **Static:** `collectstatic` writes to `static_collected/` (gitignored) for production-style serving.
- **Media:** Uploaded files go under `media/` (gitignored). Ensure the process can write to `MEDIA_ROOT`.

## Domain model (high level)

- **`store.Destination`** — Landing tiles (category text, title, image, discount, optional offer flag).
- **`categories.WFM` / `MFM` / `KFM`** — Women’s, men’s, and kids’ footwear; each has related per-size stock (`WFMSizeAvailability`, etc.).
- **`categories.BagItem`** — Line items in the bag (user, product id, category code, size, quantity).
- **`categories.Purchase`** — Placed orders (shipping fields + product description).

## Configuration notes for developers

- **Time zone:** `Asia/Kolkata` (`USE_TZ = True`).
- **Sessions:** Stored in the database (`SESSION_ENGINE = ...db`). `SESSION_COOKIE_SECURE = True` expects **HTTPS**. For plain `http://127.0.0.1` during local dev you may need to set `SESSION_COOKIE_SECURE = False` in local settings or you can lose session cookies.
- **`ALLOWED_HOSTS`:** Empty in default settings; set appropriately before deploying (e.g. `ALLOWED_HOSTS = ["localhost", "127.0.0.1"]` for local tests).

## Common commands

```bash
python manage.py migrate
python manage.py runserver
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## License

Add a license file if this project is open source or distributed.
