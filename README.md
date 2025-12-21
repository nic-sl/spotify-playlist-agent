# Spotify Playlist Agent

An AI-assisted web app that builds Spotify playlists from a natural-language prompt.

The app uses:
- FastAPI + Jinja2 for a minimal web UI and OAuth callback handling
- CrewAI to orchestrate a small crew of agents and tasks
- Last.fm API to discover similar artists
- Spotify Web API to fetch tracks and publish playlists to your account

## Contents
- Features
- Requirements
- Quickstart (uv or pip)
- Environment variables (.env)
- Run the app

## Features
- “Login with Spotify” via OAuth Authorization Code flow
- Analyze a prompt (e.g., “upbeat indie rock like The Strokes”) into artists
- Get top tracks for each artist and create a private playlist for you
- Best‑effort track addition (skips tracks that fail to add)

## Requirements
- Python 3.12+
- A Spotify Developer application (Client ID and Client Secret)
- A Last.fm API key
- Recommended: uv (fast Python package manager) or plain pip/venv

## Quickstart

### Using uv (recommended)
1. Install uv if needed:  
   `pip install uv`
2. From the project root, create a virtual environment and install deps:  
   `uv sync`
3. Copy the example env and edit values:  
   `cp .env .env.local`
4. Run the dev server:  
   `uv run uvicorn main:app --reload`
---

## Environment variables (.env)

This app reads configuration from a `.env` file via python-dotenv.

### Example `.env`
```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/callback
SESSION_SECRET=change-me-in-production
LAST_FM_API_KEY=your_lastfm_api_key
```

### Notes
- `SPOTIFY_REDIRECT_URI` must match your Spotify dashboard settings.
- `SESSION_SECRET` secures browser sessions; use a strong value.
- `LAST_FM_API_KEY` is required for similar‑artist lookup.
- CrewAI provider defaults to `crewai[bedrock]`. Configure AWS credentials or switch providers as needed.

---

## Run the app
1. Start the dev server:
   ```
   uv run uvicorn main:app --reload
   # or
   uvicorn main:app --reload
   ```
2. Open: `http://127.0.0.1:8000/`
3. Click **Login with Spotify**.
4. On the chat page, enter a playlist prompt. The app will:
   - Run the CrewAI pipeline  
   - Find similar artists via Last.fm  
   - Fetch top tracks via Spotify  
   - Create a private playlist and add tracks