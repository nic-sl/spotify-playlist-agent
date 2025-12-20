"""Utilities that wrap Spotify Web API endpoints as CrewAI tools.

The tools here assume that authentication is already handled elsewhere. For
client-credential flows, `_get_token()` is provided internally. For user-
scoped actions like creating playlists, the `SpotifyTokenManager` provides a
valid user token and `SpotifyAppUser` supplies the active user context.
"""

from crewai.tools import tool

import os
import requests

from spotify_agent_crew.spotify_session.spotify_token_manager import SpotifyTokenManager
from spotify_agent_crew.spotify_session.spotify_app_user import SpotifyAppUser

from typing import List

# noinspection PyMethodParameters
class SpotifyAPITools:
    """Static helpers and CrewAI tools for interacting with Spotify APIs.

    Methods prefixed with an underscore are internal helpers. Public methods
    decorated with `@tool` are exposed to agents within CrewAI workflows.
    """
    # Spotify API endpoints
    AUTH_URL: str = "https://accounts.spotify.com/api/token"
    BASE_URL: str = "https://api.spotify.com/v1"

    @staticmethod
    def _get_token() -> str:
        """Fetch an app access token via the Client Credentials flow.

        Environment variables `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`
        must be set.

        Returns:
            A bearer token string to call app-scoped endpoints.
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
            raise RuntimeError(f"Failed to authenticate with Spotify: {response.text}")

        return response.json()["access_token"]

    @staticmethod
    def _get_top_tracks(artist_name: str) -> List[str]:
        """Resolve an artist name to top track URIs.

        Parameters:
            artist_name: Free-form artist name to search.

        Returns:
            List of Spotify track URIs for the artist's top tracks in the
            current user market.

        Raises:
            RuntimeError: On HTTP errors or unexpected/empty responses.
        """
        token = SpotifyAPITools._get_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Step 1: Search for artist ID
        search_params = {"q": artist_name, "type": "artist", "limit": 1}
        search_resp = requests.get(
            f"{SpotifyAPITools.BASE_URL}/search",
            headers=headers,
            params=search_params,
            timeout=10,
        )

        if search_resp.status_code != 200:
            raise RuntimeError(
                f"[Spotify Search Error] Status: {search_resp.status_code}\n"
                f"Artist: {artist_name}\n"
                f"Response: {search_resp.text}"
            )

        items = search_resp.json().get("artists", {}).get("items", [])
        if not items:
            raise RuntimeError(
                f"[Spotify Search Error] No artist found for name '{artist_name}'.\n"
                f"Full response: {search_resp.json()}"
            )

        artist_id = items[0]["id"]
        params = {"market": SpotifyAppUser.get_country()}

        # Step 2: Fetch top tracks
        url = f"{SpotifyAPITools.BASE_URL}/artists/{artist_id}/top-tracks"
        top_resp = requests.get(url, headers=headers, params=params, timeout=10)

        if top_resp.status_code != 200:
            raise RuntimeError(
                f"[Spotify Top Tracks Error] Status: {top_resp.status_code}\n"
                f"Artist ID: {artist_id}\n"
                f"Response: {top_resp.text}"
            )

        tracks = top_resp.json().get("tracks", [])
        if not tracks:
            raise RuntimeError(
                f"[Spotify Top Tracks Error] No top tracks returned.\n"
                f"Artist ID: {artist_id}\n"
                f"Full response: {top_resp.json()}"
            )

        uris = [t.get("uri") for t in tracks if t.get("uri")]
        if not uris:
            raise RuntimeError(
                f"[Spotify Top Tracks Error] Tracks returned but no URIs found.\n"
                f"Artist ID: {artist_id}\n"
                f"Full response: {top_resp.json()}"
            )

        return uris

    @tool
    def get_tracks(artists: List[str]) -> List[str]: #NOSONAR - Tools cannot have self as first argument
        """Return up to 3 top track URIs for each provided artist name.

        Parameters:
            artists: List of artist names to look up.

        Returns:
            Combined list of track URIs (max three per artist).

        Raises:
            RuntimeError: If an artist lookup or top track retrieval fails.
        """
        all_tracks: List[str] = []

        for artist in artists:
            # Call your existing function
            top_uris = SpotifyAPITools._get_top_tracks(artist)

            # Take only the first 3
            top_3 = top_uris[:3]

            if not top_3:
                raise RuntimeError(
                    f"[Spotify Error] Artist '{artist}' returned no usable tracks."
                )

            all_tracks.extend(top_3)

        return all_tracks

    @tool
    def create_playlist(playlist_name: str, playlist_description: str, track_uris: List[str]): #NOSONAR - Tools cannot have self as first argument
        """Create a private playlist for the current user and add tracks.

        Adds tracks one by one; failures are skipped so the operation is
        best-effort.

        Parameters:
            playlist_name: Name of the new playlist.
            playlist_description: Description for the playlist.
            track_uris: URIs of tracks to add.

        Returns:
            Dict containing the created `playlist_id` and the list of
            successfully `added_tracks` URIs.

        Raises:
            RuntimeError: If playlist creation fails.
        """
        token = SpotifyTokenManager.get_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Step 1: Create the playlist
        payload = {
            "name": playlist_name,
            "description": playlist_description,
            "public": False
        }

        response = requests.post(
            f"{SpotifyAPITools.BASE_URL}/users/{SpotifyAppUser.get_id()}/playlists",
            headers=headers,
            json=payload
        )

        if response.status_code not in (200, 201):
            raise RuntimeError(f"Failed to create playlist: {response.text}")

        playlist_id = response.json()["id"]

        # Step 2: Add tracks individually
        add_tracks_url = f"{SpotifyAPITools.BASE_URL}/playlists/{playlist_id}/tracks"

        added_uris = []

        for uri in track_uris:
            r = requests.post(add_tracks_url, headers=headers, json={"uris": [uri]})

            if r.status_code in (200, 201):
                added_uris.append(uri)

        return {
            "playlist_id": playlist_id,
            "added_tracks": added_uris,
        }
