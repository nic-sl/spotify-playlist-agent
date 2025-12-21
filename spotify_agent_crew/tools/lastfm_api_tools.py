import os
from typing import Dict, List

import requests
from crewai.tools import tool

# noinspection PyMethodParameters
class LastFmAPITools:
    BASE_URL = "https://ws.audioscrobbler.com/2.0/"
    API_KEY = os.getenv("LAST_FM_API_KEY")

    @tool
    def get_similar_artists(artist_name: str, limit: int = 10) -> Dict[str, List[str]]: #NOSONAR - Tools cannot have self as the first argument
        """
        Fetch similar artists from Last.fm using artist.getSimilar.

        Parameters:
            artist_name: Free-form artist name to search.
            limit: Maximum number of similar artists to return.

        Returns:
            A JSON-serializable dict: {"artists": [list of names]}

        Raises:
            RuntimeError: On HTTP errors or unexpected/empty responses.
        """

        params = {
            "method": "artist.getSimilar",
            "artist": artist_name,
            "api_key": LastFmAPITools.API_KEY,
            "format": "json",
            "limit": limit,
        }

        try:
            resp = requests.get(
                LastFmAPITools.BASE_URL,
                params=params,
                timeout=10
            )
        except Exception as e:
            raise RuntimeError(
                f"[Last.fm Error] Request failed for artist '{artist_name}'.\n"
                f"Exception: {e}"
            )

        if resp.status_code != 200:
            raise RuntimeError(
                f"[Last.fm Error] Status: {resp.status_code}\n"
                f"Artist: {artist_name}\n"
                f"Response: {resp.text}"
            )

        data = resp.json()

        # Last.fm sometimes returns errors inside JSON even with 200 OK
        if "error" in data:
            raise RuntimeError(
                f"[Last.fm API Error] Code {data.get('error')} - {data.get('message')}\n"
                f"Artist: {artist_name}"
            )

        similar = data.get("similarartists", {}).get("artist", [])
        if not similar:
            raise RuntimeError(
                f"[Last.fm Similar Error] No similar artists found.\n"
                f"Artist: {artist_name}\n"
                f"Full response: {data}"
            )

        names = [a.get("name") for a in similar if a.get("name")]
        if not names:
            raise RuntimeError(
                f"[Last.fm Similar Error] Similar artists returned but no names found.\n"
                f"Artist: {artist_name}\n"
                f"Full response: {data}"
            )

        # ✅ Return plain JSON that matches your Pydantic model structure
        return {"artists": names}
