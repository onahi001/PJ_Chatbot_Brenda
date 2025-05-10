from youtube_transcript_api import YouTubeTranscriptApi as yt
from youtube_transcript_api.formatters import JSONFormatter as jft
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptAvailable,
    VideoUnavailable,
    TooManyRequests,
    CouldNotRetrieveTranscript,
)
import re


# --- verifying it is a youtube link ---
def check_link(url):
    youtube_domains = [
        "youtube.com",
        "youtu.be"
    ]
    return any(domain in url for domain in youtube_domains)

# --- extracts the video id from a youtube url ---
def extract_video_id(url):
    if not check_link(url):
        return None, " This is not a valid YouTube URL"
    
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    
    match = re.search(pattern, url)
    if match:
        return match.group(1), None
    return None, "Could not extract the video information"

def message_processor(url):
    link = url.strip()
    video_id = ""
    
    video_id, error = extract_video_id(link)
    if error:
        return None, error
    
    try:
        vid_trans = yt.get_transcript(video_id)
        vid_json = jft().format_transcript(vid_trans)
        if not vid_json:
            return None, "Could not obtain information of video"
        
    except VideoUnavailable:
        return None, "This video is unavailable."
    except TranscriptsDisabled:
        return None, "Could not obtain information for this video."
    except NoTranscriptAvailable:
        return None, "Could not obtain information for this video."
    except TooManyRequests:
        return None, "Too many requests. Please wait and try again."
    except CouldNotRetrieveTranscript:
        return None, "Could not obtain information for this video. Unknown error."
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"
    
    # storing the file in a JSON format
    with open (f'data/User_Downloaded/video_{video_id}.json', 'w', encoding='utf-8') as json_file:
        json_file.write(vid_json)
        
    return f'data/User_Downloaded/video_{video_id}.json', None



