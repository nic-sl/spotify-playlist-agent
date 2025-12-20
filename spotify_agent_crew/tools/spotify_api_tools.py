import os
import requests
from typing import List, Dict
from crewai.tools import BaseTool, tool

from spotify_agent_crew.spotify_session.spotify_token_manager import SpotifyTokenManager
from spotify_agent_crew.spotify_session.spotify_app_user import SpotifyAppUser


class SpotifyAPITools:
    name: str = "Spotify API Tools"
    description: str = "Provides access to Spotify API to the agents."

    # Spotify API endpoints
    AUTH_URL: str = "https://accounts.spotify.com/api/token"
    BASE_URL: str = "https://api.spotify.com/v1"

    @staticmethod
    def _get_token() -> str:
        """
        Retrieve a Spotify access token using Client Credentials flow.
        Client ID and Secret should be stored in environment variables.
        """
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError("Spotify client credentials not set in environment variables.")

        response = requests.post(
            SpotifyAPITools.AUTH_URL,
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
        )

        if response.status_code != 200:
            raise Exception(f"Failed to authenticate with Spotify: {response.text}")

        return response.json()["access_token"]

    @tool
    def search_songs(track_names: List[str]) -> Dict[str, str]:
        """
        Search for songs by track names and return a dictionary of {track_name: track_uri}.
        """
        token = SpotifyAPITools._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        uris = {}

        for track in track_names:
            params = {"q": track, "type": "track", "limit": 1}
            response = requests.get(f"{SpotifyAPITools.BASE_URL}/search", headers=headers, params=params)

            if response.status_code == 200:
                items = response.json().get("tracks", {}).get("items", [])
                if items:
                    uris[track] = items[0]["uri"]
                else:
                    uris[track] = None
            else:
                uris[track] = None

        return uris

    @tool
    def create_playlist(playlist_name: str, track_uris: List[str]) -> str:
        """
        Create a playlist for a given user and add tracks to it.
        Uses SpotifyTokenManager to retrieve a valid OAuth token.
        Returns the playlist ID.
        """
        # Get a valid token from the manager
        token = SpotifyTokenManager.get_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Step 1: Create playlist
        payload = {"name": playlist_name, "public": False}
        response = requests.post(
            f"{SpotifyAPITools.BASE_URL}/users/{SpotifyAppUser.get_id()}/playlists",
            headers=headers,
            json=payload
        )

        if response.status_code not in (200, 201):
            raise Exception(f"Failed to create playlist: {response.text}")

        playlist_id = response.json()["id"]

        # Step 2: Add tracks
        add_tracks_url = f"{SpotifyAPITools.BASE_URL}/playlists/{playlist_id}/tracks"
        response = requests.post(add_tracks_url, headers=headers, json={"uris": track_uris})

        if response.status_code not in (200, 201):
            raise Exception(f"Failed to add tracks: {response.text}")

        return

