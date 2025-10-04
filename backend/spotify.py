import os
import requests
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)




def get_spotify_access_token(client_id, client_secret):
    logger.info("Requesting Spotify access token...")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        logger.debug(f"Spotify token response status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Failed to get access token: {response.status_code} - {response.text}")
            raise Exception(f"Failed to get access token: {response.json()}")
        
        logger.info("Spotify access token obtained successfully")
        return response.json()["access_token"]
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error getting Spotify token: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error getting Spotify token: {str(e)}")
        raise


def extract_playlist_id(playlist_url):
    return playlist_url.split("/playlist/")[1].split("?")[0]

def get_all_tracks(link, market):
    logger.info(f"Fetching tracks from Spotify playlist: {link}")
    
    try:
        playlist_id = extract_playlist_id(link)
        logger.info(f"Extracted playlist ID: {playlist_id}")
        
        client_id = os.getenv('SPOTIPY_CLIENT_ID')
        client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logger.error("Spotify credentials not found in environment variables")
            raise Exception("Spotify credentials not configured")
        
        access_token = get_spotify_access_token(client_id, client_secret)
        
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?market={market}&limit=100"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        all_tracks = []
        page_count = 0
        
        logger.info("Fetching tracks from Spotify API...")
        while url:
            page_count += 1
            logger.debug(f"Fetching page {page_count} from Spotify API...")
            
            try:
                response = requests.get(url, headers=headers)
                logger.debug(f"Spotify API response status: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"Spotify API error: {response.status_code} - {response.text}")
                    raise Exception(f"Spotify API error: {response.status_code}")
                
                data = response.json()
                page_tracks = 0
                
                for item in data["items"]:
                    track = item["track"]
                    if not track or track.get("is_local") or track.get("restrictions"):
                        logger.debug(f"Skipping track: {track.get('name', 'Unknown')} (local/restricted)")
                        continue
                    
                    all_tracks.append({
                        "name": track["name"],
                        "artists": [artist["name"] for artist in track["artists"]],
                        "album": track["album"]["name"],
                    })
                    page_tracks += 1
                
                logger.debug(f"Page {page_count}: Found {page_tracks} valid tracks")
                url = data.get("next")
                if url == 'null':
                    break
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error fetching tracks from Spotify: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Error processing Spotify API response: {str(e)}")
                raise
        
        logger.info(f"Successfully fetched {len(all_tracks)} tracks from {page_count} pages")
        return all_tracks
        
    except Exception as e:
        logger.error(f"Error in get_all_tracks: {str(e)}", exc_info=True)
        raise

def get_playlist_name(link):
    logger.info(f"Fetching playlist name for: {link}")
    
    try:
        playlist_id = extract_playlist_id(link)
        logger.info(f"Extracted playlist ID: {playlist_id}")
        
        client_id = os.getenv('SPOTIPY_CLIENT_ID')
        client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        access_token = get_spotify_access_token(client_id, client_secret)
        
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        logger.debug("Requesting playlist metadata from Spotify...")
        response = requests.get(url, headers=headers)
        logger.debug(f"Spotify playlist API response status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Spotify playlist API error: {response.status_code} - {response.text}")
            raise Exception(f"Spotify playlist API error: {response.status_code}")
        
        data = response.json()
        playlist_name = data["name"]
        logger.info(f"Playlist name retrieved: {playlist_name}")
        return playlist_name
        
    except Exception as e:
        logger.error(f"Error getting playlist name: {str(e)}", exc_info=True)
        raise
    
    
    


