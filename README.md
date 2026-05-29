# 🎵 Lyrics Manager

A self-hosted, offline-capable web application for managing song lyrics and set lists — designed for live performance. Works as a Progressive Web App (PWA) on iOS and Android, downloadable to the home screen.

---

## Features

| Feature | Details |
|---|---|
| **Libraries** | Create personal or global (admin-managed) song libraries |
| **Songs** | Full lyrics editor with key, tempo and performance notes |
| **Set lists** | Build ordered set lists from any library, with drag-up/down reordering |
| **Perform mode** | Full-screen lyrics viewer with font scaling, keyboard/swipe navigation |
| **Offline** | Download any set list to device IndexedDB — works with zero connectivity |
| **Share setlists** | Share with other users with view-only or edit permissions |
| **Mobile-friendly** | Responsive design with smooth scrolling on all devices |
| **Themes** | Dark, Light, Midnight, Forest, Amber — synced per user |
| **Users** | Admin user management with role-based access |
| **Storage dashboard** | Admin view of usage across all libraries and users |
| **PWA install** | Add to Home Screen on iOS Safari & Android Chrome |

---

## Setlist Sharing

Share your setlists with other users with granular permission control:

### Share a setlist
1. Open a setlist from your **Set Lists** page
2. Click the **Share** button in the setlist details
3. Select a user and choose permission level:
   - **View** — User can view and perform the setlist (read-only)
   - **Edit** — User can modify songs and arrangement

### Permission levels
- **Owner**: Full control; can share, delete, and modify
- **Edit**: Can view and modify the setlist
- **View**: Can view and perform only (read-only access)

### Managing shares
- View all active shares from the setlist detail page
- Update permission levels at any time
- Revoke access by removing the share

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

## Mobile Experience

The app is fully optimized for mobile devices:

- **Smooth scrolling** on all pages and devices
- **Touch-friendly** interface with large tap targets
- **Full-screen lyrics** in Perform mode with optional font scaling
- **Responsive layout** that adapts from phone to tablet to desktop
- **Offline support** for complete functionality without internet

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

### API endpoints

#### Setlist Sharing
- `GET /api/setlists/{setlist_id}/shares` — List shares for a setlist (owner only)
- `POST /api/setlists/{setlist_id}/shares` — Share setlist with user
- `PATCH /api/setlists/{setlist_id}/shares/{share_id}` — Update share permission
- `DELETE /api/setlists/{setlist_id}/shares/{share_id}` — Revoke share

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

## License

MIT
