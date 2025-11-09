import os
from googleapiclient.discovery import build
from typing import Optional, Dict
import re


class YouTubeService:
    """Service for fetching relevant YouTube tutorial videos"""
    
    def __init__(self, api_key: str):
        """Initialize YouTube API client"""
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def search_best_video(self, keywords: str, max_results: int = 10) -> Optional[Dict]:
        """
        Search for the best tutorial video based on keywords
        
        Args:
            keywords: Search keywords (can be comma-separated)
            max_results: Maximum number of results to fetch (default: 10)
            
        Returns:
            Dictionary with video details (url, title, description, views) or None
        """
        try:
            search_query = keywords.split(',')[0].strip()
            
            search_response = self.youtube.search().list(
                q=search_query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                order='relevance',  
                videoDuration='medium',  
                videoDefinition='any',
                relevanceLanguage='en'
            ).execute()
            
            if not search_response.get('items'):
                return None
            
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            videos_response = self.youtube.videos().list(
                part='statistics,snippet,contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            if not videos_response.get('items'):
                return None
            
            best_video = self._select_best_video(videos_response['items'], search_query)
            
            if best_video:
                return {
                    'url': f"https://www.youtube.com/watch?v={best_video['id']}",
                    'title': best_video['snippet']['title'],
                    'description': best_video['snippet']['description'],
                    'thumbnail': best_video['snippet']['thumbnails']['high']['url'],
                    'views': int(best_video['statistics'].get('viewCount', 0)),
                    'likes': int(best_video['statistics'].get('likeCount', 0)),
                    'channel': best_video['snippet']['channelTitle']
                }
            
            return None
            
        except Exception as e:
            print(f"YouTube API Error: {str(e)}")
            return None
    
    def _select_best_video(self, videos: list, search_query: str) -> Optional[Dict]:
        """
        Select the best video from a list based on multiple criteria
        
        Args:
            videos: List of video items from YouTube API
            search_query: Original search query for relevance scoring
            
        Returns:
            Best video item or None
        """
        if not videos:
            return None
        
        scored_videos = []
        
        for video in videos:
            try:
                views = int(video['statistics'].get('viewCount', 0))
                likes = int(video['statistics'].get('likeCount', 0))
                title = video['snippet']['title'].lower()
                description = video['snippet']['description'].lower()
                
                score = 0
                
                if views > 0:
                    score += min(views / 100000, 50) 
                
                if views > 0:
                    like_ratio = likes / views
                    score += like_ratio * 100  
                
                query_words = search_query.lower().split()
                title_matches = sum(1 for word in query_words if word in title)
                score += title_matches * 10
                
                educational_keywords = ['tutorial', 'guide', 'course', 'explained', 
                                        'learn', 'introduction', 'beginner', 'complete']
                title_edu_matches = sum(1 for keyword in educational_keywords if keyword in title)
                score += title_edu_matches * 5
                
                duration = video['contentDetails'].get('duration', '')
                duration_seconds = self._parse_duration(duration)
                if duration_seconds < 120 or duration_seconds > 3600:  
                    score -= 10
                
                scored_videos.append({
                    'video': video,
                    'score': score
                })
                
            except Exception as e:
                continue
        
        if scored_videos:
            scored_videos.sort(key=lambda x: x['score'], reverse=True)
            return scored_videos[0]['video']
        
        return None
    
    def _parse_duration(self, duration: str) -> int:
        """
        Parse ISO 8601 duration format to seconds
        
        Args:
            duration: Duration string (e.g., 'PT15M33S')
            
        Returns:
            Duration in seconds
        """
        try:
            duration = duration.replace('PT', '')
            
            hours = 0
            minutes = 0
            seconds = 0
            
            if 'H' in duration:
                hours = int(duration.split('H')[0])
                duration = duration.split('H')[1]
            
            if 'M' in duration:
                minutes = int(duration.split('M')[0])
                duration = duration.split('M')[1]
            
            if 'S' in duration:
                seconds = int(duration.replace('S', ''))
            
            return hours * 3600 + minutes * 60 + seconds
            
        except Exception:
            return 0
    
    def get_video_embed_url(self, video_url: str) -> str:
        """
        Convert a YouTube watch URL to an embed URL
        
        Args:
            video_url: YouTube watch URL
            
        Returns:
            YouTube embed URL
        """
        video_id = None
        if 'watch?v=' in video_url:
            video_id = video_url.split('watch?v=')[1].split('&')[0]
        elif 'youtu.be/' in video_url:
            video_id = video_url.split('youtu.be/')[1].split('?')[0]
        
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        
        return video_url


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in environment variables")
        exit(1)
    
    youtube_service = YouTubeService(api_key)
    
    print("Searching for best Python tutorial video...")
    keywords = "Python programming tutorial for beginners"
    video = youtube_service.search_best_video(keywords)
    
    if video:
        print(f"\nBest Video Found:")
        print(f"Title: {video['title']}")
        print(f"URL: {video['url']}")
        print(f"Channel: {video['channel']}")
        print(f"Views: {video['views']:,}")
        print(f"Likes: {video['likes']:,}")
    else:
        print("No video found")
