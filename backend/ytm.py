from ytmusicapi import YTMusic
import ytmusicapi
from spotify import get_all_tracks, get_playlist_name
import logging
import time

logger = logging.getLogger(__name__)


def get_video_ids(ytmusic,tracks):
    logger.info(f"Starting search for {len(tracks)} tracks on YouTube Music")
    video_ids = []
    missed_tracks = {
        "count": 0,
        "tracks": []
    }
    start_time = time.time()
    
    for i, track in enumerate(tracks, 1):
        try:
            search_string = f"{track['name']} {track['artists'][0]}"
            
            # Log progress every 50 tracks or for first/last tracks
            if i % 50 == 0 or i <= 5 or i > len(tracks) - 5:
                logger.info(f"Progress: {i}/{len(tracks)} tracks processed ({i/len(tracks)*100:.1f}%)")
                logger.info(f"Found so far: {len(video_ids)} tracks, Missed: {missed_tracks['count']} tracks")
            
            logger.debug(f"Searching for track {i}/{len(tracks)}: {search_string}")
            
            # Add timeout to prevent hanging
            try:
                search_results = ytmusic.search(search_string, filter="songs")
                if not search_results:
                    logger.warning(f"No search results for: {search_string}")
                    raise Exception("No search results")
                    
                video_id = search_results[0]["videoId"]
                video_ids.append(video_id)
                logger.debug(f"Found video ID: {video_id}")
                
            except Exception as search_error:
                logger.warning(f"Search failed for '{search_string}': {str(search_error)}")
                raise search_error
            
        except Exception as e:
            logger.warning(f"Track not found on YouTube Music: {track['name']} by {track['artists'][0]} - Error: {str(e)}")
            missed_tracks["count"] += 1
            missed_tracks["tracks"].append(f"{track['name']} {track['artists'][0]}")
    
    search_time = time.time() - start_time
    logger.info(f"Search completed in {search_time:.2f} seconds")
    logger.info(f"Found {len(video_ids)}/{len(tracks)} songs on YouTube Music")
    logger.info(f"Missed tracks: {missed_tracks['count']}")
    
    if len(video_ids) == 0:
        logger.error("No songs found on YouTube Music")
        raise Exception("No songs found on YouTube Music")
    
    return video_ids, missed_tracks


def create_ytm_playlist(playlist_link, headers):
    logger.info("=== STARTING PLAYLIST CREATION ===")
    logger.info(f"Playlist link: {playlist_link}")
    
    try:
        # Convert JSON headers to raw format for ytmusicapi
        logger.info("Converting headers to ytmusicapi format...")
        if isinstance(headers, dict):
            logger.info("Headers received as dictionary, converting to raw format...")
            # Convert dictionary to raw headers string
            raw_headers_lines = []
            for key, value in headers.items():
                if value:  # Only include non-empty values
                    raw_headers_lines.append(f"{key}: {value}")
            raw_headers_string = "\n".join(raw_headers_lines)
            logger.info(f"Converted {len(raw_headers_lines)} headers to raw format")
        else:
            # Headers are already in string format
            logger.info("Headers already in string format")
            raw_headers_string = headers
        
        logger.info("Setting up YouTube Music authentication...")
        ytmusicapi.setup(filepath="header_auth.json", headers_raw=raw_headers_string)
        ytmusic = YTMusic("header_auth.json")
        logger.info("YouTube Music authentication successful")
        
        logger.info("Fetching tracks from Spotify...")
        tracks = get_all_tracks(playlist_link, "IN")
        logger.info(f"Retrieved {len(tracks)} tracks from Spotify")
        
        logger.info("Getting playlist name...")
        name = get_playlist_name(playlist_link)
        logger.info(f"Playlist name: {name}")
        
        logger.info("Searching for tracks on YouTube Music...")
        video_ids, missed_tracks = get_video_ids(ytmusic, tracks)
        
        logger.info(f"Creating playlist '{name}' with {len(video_ids)} tracks...")
        playlist_result = ytmusic.create_playlist(name, "", "PRIVATE", video_ids)
        logger.info(f"Playlist created successfully! Playlist ID: {playlist_result}")
        
        return missed_tracks
        
    except Exception as e:
        logger.error(f"Error in create_ytm_playlist: {str(e)}", exc_info=True)
        raise

