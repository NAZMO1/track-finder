"""Standalone demo data: no external recognition or database writes."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/demo/track")
def demo_track():
    """Return clearly labeled sample data so visitors can explore the UI."""
    return {
        "status": "success",
        "demo": True,
        "track": {
            "title": "Demo Track",
            "subtitle": "Sample Artist",
            "cover": "",
            "spotify_url": "https://open.spotify.com/search/Demo%20Track%20Sample%20Artist",
            "youtube_url": "https://www.youtube.com/results?search_query=Demo%20Track%20Sample%20Artist",
            "apple_url": ""
        }
    }
