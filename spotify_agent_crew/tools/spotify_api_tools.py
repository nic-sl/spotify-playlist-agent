"""Utilities that wrap Spotify Web API endpoints as CrewAI tools.

This module now uses the Spotipy library for all Spotify API interactions,
including client credentials and user-scoped actions.
"""

from crewai.tools import tool

import os
from typing import List

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from spotify_agent_crew.spotify_session.spotify_token_manager import SpotifyTokenManager
from spotify_agent_crew.spotify_session.spotify_app_user import SpotifyAppUser

# noinspection PyMethodParameters
class SpotifyAPITools:
    """Static helpers and CrewAI tools for interacting with Spotify APIs.

    Methods prefixed with an underscore are internal helpers. Public methods
    decorated with `@tool` are exposed to agents within CrewAI workflows.
    """
    # Spotify API endpoints
    BASE_URL: str = "https://api.spotify.com/v1"

    @staticmethod
    def _get_app_client() -> spotipy.Spotify:
        """Create a Spotipy client using Client Credentials flow."""
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError("Spotify client credentials not set in environment variables.")

        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        return spotipy.Spotify(auth_manager=auth_manager)

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
        sp = SpotifyAPITools._get_app_client()

        # Step 1: Search for artist ID
        search = sp.search(q=artist_name, type="artist", limit=1)
        items = search.get("artists", {}).get("items", [])
        if not items:
            raise RuntimeError(
                f"[Spotify Search Error] No artist found for name '{artist_name}'.\n"
                f"Full response: {search}"
            )

        artist_id = items[0]["id"]
        country = SpotifyAppUser.get_country()
        # Step 2: Fetch top tracks via Spotipy
        top = sp.artist_top_tracks(artist_id, country=country)
        tracks = top.get("tracks", [])
        if not tracks:
            raise RuntimeError(
                f"[Spotify Top Tracks Error] No top tracks returned.\n"
                f"Artist ID: {artist_id}\n"
                f"Full response: {top}"
            )

        uris = [t.get("uri") for t in tracks if t.get("uri")]
        if not uris:
            raise RuntimeError(
                f"[Spotify Top Tracks Error] Tracks returned but no URIs found.\n"
                f"Artist ID: {artist_id}\n"
                f"Full response: {top}"
            )

        return uris

    @tool
    def get_tracks(artists: List[str]) -> List[str]: #NOSONAR - Tools cannot have self as the first argument
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
    def create_playlist(playlist_name: str, playlist_description: str, track_uris: List[str]): #NOSONAR - Tools cannot have self as the first argument
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
        # Use user-scoped token via our token manager
        token = SpotifyTokenManager.get_token()
        sp = spotipy.Spotify(auth=token)

        # Step 1: Create the playlist
        playlist = sp.user_playlist_create(
            user=SpotifyAppUser.get_id(),
            name=playlist_name,
            public=False,
            description=playlist_description,
        )

        playlist_id = playlist["id"]

        # Step 2: Add tracks (Spotipy can add up to 100 at once)
        added_uris = []
        if track_uris:
            # Add in chunks of 100
            for i in range(0, len(track_uris), 100):
                chunk = track_uris[i:i+100]
                sp.playlist_add_items(playlist_id, chunk)
                added_uris.extend(chunk)

        return {"playlist_id": playlist_id, "added_tracks": added_uris}
