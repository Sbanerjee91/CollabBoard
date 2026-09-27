# CollabBoard

A real-time collaborative whiteboard. Open a room link, start drawing — everyone else in the room sees your strokes, text, and images appear as you make them.

Built with Django, Django Channels (WebSockets), and a single dependency-free HTML/JS frontend — no frontend build step, no framework.

## Features

- **Drawing tools** — pen, highlighter, eraser (true erase, not white paint-over), line, arrow, rectangle, ellipse
- **Text** — click anywhere with the text tool and type; wraps automatically
- **Images** — upload a photo or screenshot to discuss; it's resized and compressed client-side before syncing
- **Live cursors & presence** — see who's in the room and where everyone's pointer is, in real time
- **Custom identity** — first-time visitors are asked for a name and colour, remembered on that device afterwards
- **Resilient by design** — reconnects automatically if the connection drops; falls back to a local-only "Solo" mode if no server is reachable; canvas resizing never loses your drawing
- **Undo/redo**, PNG export, light/dark theme, paper styles (dot grid / lined / blank), shareable room links
- **Keyboard shortcuts** — `P` `H` `E` `L` `A` `R` `O` `T` for tools, `[` `]` for stroke width, `Ctrl/Cmd+Z` / `Ctrl/Cmd+Shift+Z` for undo/redo

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Django 6 |
| Real-time transport | Django Channels 4 (WebSockets) |
| ASGI server | Daphne |
| Channel layer | `InMemoryChannelLayer` (see [Limitations](#limitations)) |
| Frontend | Single HTML file — vanilla JS, Canvas 2D API, no build step |
| Database | SQLite (used only for Django's built-in admin/auth/session tables — the whiteboard itself stores nothing there) |

## Getting started

### Prerequisites
- Python 3.10+

### Setup

```bash
git clone <your-repo-url>
cd collab_board

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install django channels daphne

python manage.py migrate
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in a browser. Open it again in a second tab (or a second browser) to see live sync in action.

> **Tested with:** Django 6.1, Channels 4.3, Daphne 4.2.

### Confirming it's running correctly

When the server starts, the very first line after the system-check output should say:

```
Starting ASGI/Daphne version ... development server at http://127.0.0.1:8000/
```

If it instead says `Starting development server at http://...` with no mention of ASGI/Daphne, WebSockets will not work — see [Troubleshooting](#troubleshooting).

## Project structure

```
collab_board/
├── manage.py
├── core/                     # Project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py                # Routes HTTP → Django, WebSocket → Channels
│   └── wsgi.py
└── canvas/                   # The whiteboard app
    ├── views.py               # Serves the whiteboard page
    ├── urls.py
    ├── routing.py              # WebSocket URL: /ws/canvas/<room_name>/
    ├── consumers.py            # Relays messages to everyone in a room
    ├── models.py               # (empty — nothing is persisted; see Limitations)
    └── templates/canvas/index.html   # The entire frontend
```

## How it works

1. A browser opens `/`, which serves `index.html` — the whole UI, in one file.
2. That page opens a WebSocket to `/ws/canvas/<room_name>/`. Everyone connected to the same room name joins the same "group" in Django Channels.
3. Every drawing action (a stroke point, a text box, an image, a cursor move) is sent as a small JSON message over that socket.
4. The server (`consumers.py`) does no interpretation of the message — it just relays whatever it receives to everyone else in the group.
5. Each browser repaints its own canvas based on what it receives. There's no "server-side" drawing state; the board exists only in the browsers currently connected to it.

## Limitations

- **No persistence.** If everyone leaves a room, the board is gone. There's no database storage of drawings by design in this version.
- **Single-process only.** `InMemoryChannelLayer` only relays messages within one server process. Running multiple workers or instances (common in production deployments) will silently split users into separate, isolated rooms. Switch to [`channels-redis`](https://github.com/django/channels_redis) before deploying beyond a single process.
- **No authentication.** Anyone with a room's link can draw, clear the board, or upload images.
- **Room names** are limited to letters, numbers, underscores, and hyphens.

## Troubleshooting

**WebSocket fails immediately, drawing doesn't sync between tabs:**
Run `python manage.py migrate` if you haven't already — Channels' middleware can throw if the database tables it needs (even just for sessions) don't exist yet.

**Server won't start / import errors:**
Confirm `daphne` is installed and listed first in `INSTALLED_APPS` in `core/settings.py` — its position there is what makes `runserver` use the ASGI development server instead of the plain HTTP one.

**Nothing appears in the terminal when you open a tab:**
The request likely isn't reaching the server at all — check the browser's DevTools → Network tab, filter by "WS", and confirm the WebSocket connection's status is `101 Switching Protocols`.

## License

Add a license of your choice (MIT is a common default for a project like this) before publishing.
