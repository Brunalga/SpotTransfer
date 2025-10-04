from flask import Flask, request
from flask_cors import CORS
from ytm import create_ytm_playlist
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spottransfer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={
    r"/*" : {
        "origins": [os.getenv('FRONTEND_URL')],
        "methods" : ["POST", "GET"],
        
    }
})


@app.route('/create', methods=['POST'])
def create_playlist():
    logger.info("=== NEW PLAYLIST CREATION REQUEST ===")
    logger.info(f"Request timestamp: {datetime.now()}")
    
    try:
        data = request.get_json()
        playlist_link = data.get('playlist_link')
        auth_headers = data.get('auth_headers')
        
        logger.info(f"Playlist link: {playlist_link}")
        logger.info(f"Auth headers provided: {'Yes' if auth_headers else 'No'}")
        logger.debug(f"Headers type: {type(auth_headers)}")
        
        if not playlist_link:
            logger.error("No playlist link provided")
            return {"message": "Playlist link is required"}, 400
            
        if not auth_headers:
            logger.error("No auth headers provided")
            return {"message": "Auth headers are required"}, 400
        
        # Handle JSON string headers
        if isinstance(auth_headers, str):
            logger.info("Headers received as string, parsing as JSON...")
            try:
                import json
                auth_headers = json.loads(auth_headers)
                logger.info("Successfully parsed headers from JSON string")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse headers as JSON: {str(e)}")
                return {"message": "Invalid headers format. Headers must be a valid JSON object."}, 400
        
        logger.info("Starting playlist creation process...")
        missed_tracks = create_ytm_playlist(playlist_link, auth_headers)
        
        logger.info(f"Playlist created successfully! Missed tracks: {missed_tracks.get('count', 0)}")
        return {"message": "Playlist created successfully!",
                "missed_tracks": missed_tracks
        }, 200
        
    except Exception as e:
        logger.error(f"Error creating playlist: {str(e)}", exc_info=True)
        return {"message": f"Server timeout while cloning playlist. Please try again or report this issue. Error: {str(e)}"}, 500
    
@app.route('/', methods=['GET'])
def home():
    # Render health check endpoint
    return {"message": "Server Online"}, 200

if __name__ == '__main__':
    app.run(port=8080)