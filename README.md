# Spotify Playlist Agent

Build a Spotify playlist from a short, natural‑language prompt.

Uses FastAPI (web + OAuth), CrewAI (agent orchestration), Last.fm (similar artists), and Spotify Web API (tracks + playlist publish).

## Features
- Sign in with Spotify (OAuth Authorization Code flow)
- Interprets your prompt to pick seed artists (CrewAI)
- Fetches top tracks per artist (for your Spotify profile country)
- Creates a playlist and adds the tracks

## Requirements
- Python 3.12+
- Spotify Developer app (Client ID, Client Secret)
- Last.fm API key
- Access to LLM models (default configuration: AWS Bedrock)
- uv (recommended) for dependency management

## Quickstart

Using uv (recommended)
1) Install deps: `uv sync`
2) Create `.env` (see below)
3) Run: `uv run uvicorn main:app --reload`

## Environment (.env)
The app reads configuration from a `.env` in the project root.

Required
- `SPOTIFY_CLIENT_ID=<your client id>`
- `SPOTIFY_CLIENT_SECRET=<your client secret>`
- `LAST_FM_API_KEY=<your last.fm api key>`
- `MODEL=<LLM model>` (+ appropriate credentials – e.g., `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`)

## Run
1) Start the server:
```
uv run uvicorn main:app --reload
# or
uvicorn main:app --reload
```
2) Open http://127.0.0.1:8000/
3) Click “Login with Spotify”, then on the chat page enter your playlist prompt.
4) The app will: analyze your prompt, find similar artists (Last.fm), fetch tracks (Spotify), and publish a playlist to your account.