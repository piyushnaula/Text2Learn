import os
from typing import Optional, Tuple

import requests
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEO_RELEVANCE_THRESHOLD = float(os.getenv("VIDEO_RELEVANCE_THRESHOLD", "0.75"))

_embed_model: Optional[SentenceTransformer] = None


def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embed_model


def _compute_relevance(subtopic,video_title,video_description):
    model = _get_embed_model()
    query_text = subtopic
    video_text = f"{video_title}. {video_description}"

    emb_query = model.encode(query_text, normalize_embeddings=True)
    emb_video = model.encode(video_text, normalize_embeddings=True)

    score = float(util.cos_sim(emb_query, emb_video)[0][0])
    return score


def find_youtube_video(subtopic, topic):
    if not YOUTUBE_API_KEY:
        return None, None, 0.0

    search_query = f"{subtopic} {topic} tutorial explanation"

    params = {
        "part": "snippet",
        "q": search_query,
        "type": "video",
        "maxResults": 5,
        "relevanceLanguage": "en",
        "key": YOUTUBE_API_KEY,
    }

    try:
        resp = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("items", [])
        if not items:
            return None, None, 0.0

        best_url = None
        best_title = None
        best_score = 0.0

        for item in items:
            video_id = item["id"].get("videoId", "")
            snippet = item.get("snippet", {})
            title = snippet.get("title", "")
            description = snippet.get("description", "")

            score = _compute_relevance(subtopic, title, description)

            if score > best_score:
                best_score = score
                best_title = title
                best_url = f"https://www.youtube.com/watch?v={video_id}"

        if best_score >= VIDEO_RELEVANCE_THRESHOLD:
            return best_url, best_title, best_score
        else:
            return None, None, best_score

    except requests.exceptions.RequestException:
        return None, None, 0.0
