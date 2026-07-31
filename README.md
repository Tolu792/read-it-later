# Read It Later

A small app for saving articles to read later. Paste in a URL and it fetches the page, pulls out the title, description, main image, and an estimated reading time, then stores it so you can tag it, search it, mark it as read, or archive it.

## Features

- Add an article by URL - title, description, image, and reading time are fetched automatically
- Full article text extraction (via trafilatura) for a clean reading view, stripped of ads and navigation
- Tagging, with filtering and search across your saved articles
- Unread / read / archived status, with one-click actions to change it
- Background fetching via Celery and Redis, so adding an article doesn't block on a slow site
- Per-user accounts, each with their own private list
- A REST API (token-authenticated) covering everything the web UI does, with interactive Swagger docs
- A bookmarklet for saving the page you're currently on from anywhere on the web, not just from inside the app

Some sites block scraping outright (Cloudflare, etc.) or only render their content client-side with JavaScript. When a fetch fails, the article doesn't get stuck in limbo - it's marked as failed and falls back to linking straight to the original source.

## Requirements

- Python 3.14
- Redis (used as the Celery broker)

## Setup

Clone the repo and set up a virtual environment:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
```

Run migrations and create yourself an account:

```
python manage.py migrate
python manage.py createsuperuser
```

The app needs three processes running at the same time, so open three terminals:

```
redis-server
celery -A backend worker -l info
python manage.py runserver
```

Then go to `http://127.0.0.1:8000/`, log in, and start saving articles.

## API

The REST API lives under `/api/`. Get a token with your username and password:

```
curl -X POST http://127.0.0.1:8000/api/token/ -d "username=you&password=yourpassword"
```

Use the token to list, add, update, or delete articles:

```
curl http://127.0.0.1:8000/api/articles/ -H "Authorization: Token YOUR_TOKEN"
```

Interactive docs are at `/api/schema/swagger-ui/`.

## Bookmarklet

Once logged in, visit `/bookmarklet/` and drag the link to your bookmarks bar. Clicking it on any page saves that page to your list.
