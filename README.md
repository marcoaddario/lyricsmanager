# 🎵 Lyrics Manager

A self-hosted, offline-capable web application for managing song lyrics and set lists — designed for live performance. Works as a Progressive Web App (PWA) on iOS and Android, downloadable to the home screen with full offline support.

---

## Features

| Feature | Details |
|---|---|
| **Libraries** | Create personal or global (admin-managed) song libraries |
| **Songs** | Full lyrics editor with key, tempo and performance notes |
| **Set lists** | Build ordered set lists from any library, with drag-up/down reordering |
| **Perform mode** | Full-screen lyrics viewer with font scaling, keyboard/swipe navigation |
| **Offline** | Download any set list to device IndexedDB — works with zero connectivity |
| **Themes** | Dark, Light, Midnight, Forest, Amber — synced per user |
| **Users** | Admin user management with role-based access |
| **Storage dashboard** | Admin view of usage across all libraries and users |
| **PWA install** | Add to Home Screen on iOS Safari & Android Chrome |

---

## Architecture

```
nginx (reverse proxy, TLS, rate limiting)
  ├── SvelteKit PWA frontend  (port 3000)
  └── FastAPI backend         (port 8000)
        └── PostgreSQL 16     (port 5432, internal)
        └── Redis 7           (port 6379, internal, optional sessions)
```

All services run as Docker Compose containers. Only nginx is exposed to the network.

---

## Quick start

### Prerequisites

- Docker 24+ and Docker Compose v2
- A Linux/macOS host (or WSL2 on Windows)

### 1. Clone and configure

```bash
git clone <your-repo> lyricsmanager
cd lyricsmanager
cp .env.example .env
```

Edit `.env` and set at minimum:

```env
POSTGRES_PASSWORD=a_strong_password_here
SECRET_KEY=a_very_long_random_string_64_chars_minimum
FIRST_ADMIN_EMAIL=you@example.com
FIRST_ADMIN_PASSWORD=your_initial_admin_password
```

### 2. Deploy

```bash
./scripts/deploy.sh
```

This builds the images, starts all containers and runs database migrations automatically.

The app will be available at **http://localhost** (or your server's IP/domain).

### 3. First login

Sign in with the `FIRST_ADMIN_EMAIL` and `FIRST_ADMIN_PASSWORD` you set in `.env`.

> ⚠️ Change the admin password immediately after first login via **Settings → Change password**.

---

## Configuration reference

All configuration is via `.env` variables:

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_PASSWORD` | *(required)* | PostgreSQL password |
| `SECRET_KEY` | *(required)* | JWT signing secret (64+ random chars) |
| `POSTGRES_DB` | `lyricsmanager` | Database name |
| `POSTGRES_USER` | `lyrics` | Database user |
| `FIRST_ADMIN_EMAIL` | `admin@example.com` | Seeded admin email |
| `FIRST_ADMIN_PASSWORD` | `changeme123` | Seeded admin password |
| `HTTP_PORT` | `80` | External HTTP port |
| `HTTPS_PORT` | `443` | External HTTPS port |
| `MAX_STORAGE_MB` | `2048` | Storage usage warning threshold (MB) |
| `PUBLIC_API_URL` | `/api` | API base URL seen by the browser |

---

## HTTPS / TLS setup

For production, place your certificates in `nginx/ssl/` and update `nginx/nginx.conf` to enable the HTTPS server block:

```nginx
server {
    listen 443 ssl;
    ssl_certificate     /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    # ... rest of config
}
```

Then redirect HTTP → HTTPS:

```nginx
server {
    listen 80;
    return 301 https://$host$request_uri;
}
```

For a free certificate with Let's Encrypt, consider adding a `certbot` service to the Compose stack.

---

## PWA installation

### iOS (Safari)
1. Open the app URL in Safari
2. Tap the **Share** button → **Add to Home Screen**
3. The app installs and works fully offline after downloading set lists

### Android (Chrome)
1. Open the app URL in Chrome
2. Tap the **⋮ menu** → **Add to Home Screen** (or banner appears automatically)
3. Same offline capability

### Downloading set lists for offline use

From the **Set Lists** page, tap **⬇ Download** on any set list. All lyrics are cached to device storage (IndexedDB). You can then use **Perform** mode with no internet connection.

Cached set lists are managed from **Settings → Offline storage**.

---

## Development

### Run locally without Docker

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Start a local Postgres, then:
DATABASE_URL=postgresql+asyncpg://lyrics:lyrics@localhost/lyricsmanager \
SECRET_KEY=dev-secret \
alembic upgrade head
python -m app.initial_data
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
PUBLIC_API_URL=http://localhost:8000/api npm run dev
```

### API documentation

FastAPI auto-generates interactive docs at:
- **Swagger UI**: `http://localhost/api/docs`
- **ReDoc**: `http://localhost/api/redoc`

### Database migrations

```bash
# Generate a new migration after model changes
docker compose exec api alembic revision --autogenerate -m "describe change"

# Apply migrations
docker compose exec api alembic upgrade head

# Rollback one step
docker compose exec api alembic downgrade -1
```

---

## Backup and restore

```bash
# Create a backup
./scripts/backup.sh
# Saves to ./backups/db_YYYYMMDD_HHMMSS.sql.gz

# Restore
gunzip -c backups/db_20240101_120000.sql.gz \
  | docker compose exec -T db psql -U lyrics lyricsmanager
```

---

## Project structure

```
lyricsmanager/
├── docker-compose.yml
├── .env.example
├── nginx/
│   └── nginx.conf
├── scripts/
│   ├── deploy.sh
│   └── backup.sh
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── migrations/
│   │   └── versions/
│   └── app/
│       ├── main.py          # FastAPI app entry point
│       ├── initial_data.py  # Seeds admin user
│       ├── core/
│       │   ├── config.py    # Settings (pydantic-settings)
│       │   ├── database.py  # SQLAlchemy async engine
│       │   └── auth.py      # JWT + password utils
│       ├── models/
│       │   └── user.py      # All ORM models
│       ├── schemas/
│       │   └── schemas.py   # All Pydantic schemas
│       └── api/
│           ├── auth.py
│           ├── users.py
│           ├── libraries.py
│           ├── songs.py
│           ├── setlists.py
│           └── admin.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── svelte.config.js
    ├── vite.config.js       # Includes PWA plugin
    └── src/
        ├── app.html
        ├── app.css          # Global styles + 5 themes
        ├── lib/
        │   ├── services/
        │   │   ├── api.ts       # All API calls + token refresh
        │   │   └── offline.ts   # IndexedDB offline storage
        │   ├── stores/
        │   │   └── index.ts     # Auth, theme, network, toasts
        │   └── components/
        │       ├── Sidebar.svelte
        │       └── Toast.svelte
        └── routes/
            ├── +layout.svelte   # Auth guard + app shell
            ├── +page.svelte     # Dashboard
            ├── login/
            ├── libraries/
            │   ├── +page.svelte         # Library list
            │   └── [id]/+page.svelte    # Library + song editor
            ├── setlists/
            │   ├── +page.svelte         # Set list management
            │   └── [id]/+page.svelte    # Set list editor
            ├── perform/
            │   └── [id]/+page.svelte    # Full-screen perform mode
            ├── settings/
            └── admin/
                ├── users/
                ├── libraries/
                └── storage/
```

---

## Security notes

- All API routes require JWT authentication except `/api/auth/login` and `/health`
- Admin-only routes are enforced server-side (not just client-side)
- Rate limiting on login endpoint (5 req/min) prevents brute force
- Passwords are hashed with bcrypt
- JWT tokens expire after 24 hours; refresh tokens after 30 days
- Change `SECRET_KEY` in production — it must never be committed to version control

---

## Licence

MIT
