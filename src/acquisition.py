import os
import re
import json
from pathlib import Path
from googleapiclient.discovery import build

def get_video_id(url):
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:be\/)([0-9A-Za-z_-]{11}).*'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def fetch_metrics(video_urls, output_file=None):
    metrics = {}
    api_key = os.getenv("YOUTUBE_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    video_ids = []
    url_map = {}
    for url in video_urls:
        vid = get_video_id(url)
        if vid:
            video_ids.append(vid)
            url_map[vid] = url
            
    if api_key and video_ids:
        try:
            youtube = build("youtube", "v3", developerKey=api_key)
            for i in range(0, len(video_ids), 50):
                batch = video_ids[i:i+50]
                resp = youtube.videos().list(part="snippet,statistics", id=",".join(batch)).execute()
                for item in resp.get("items", []):
                    v_id = item["id"]
                    snippet = item.get("snippet", {})
                    stats = item.get("statistics", {})
                    metrics[v_id] = {
                        "title": snippet.get("title", "Unknown"),
                        "url": url_map.get(v_id, f"https://www.youtube.com/watch?v={v_id}"),
                        "view_count": int(stats.get("viewCount", 0)),
                        "like_count": int(stats.get("likeCount", 0)),
                        "comment_count": int(stats.get("commentCount", 0))
                    }
        except Exception as e:
            print(f"YouTube Data API metrics fetch warning: {e}")

    # Fallback for any video_ids not populated by API
    for vid in video_ids:
        if vid not in metrics:
            metrics[vid] = {
                "title": f"YouTube Video ({vid})",
                "url": url_map.get(vid, f"https://www.youtube.com/watch?v={vid}"),
                "view_count": 0,
                "like_count": 0,
                "comment_count": 0
            }

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=4)
            
    return metrics
