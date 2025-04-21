import joblib
import streamlit as st
import requests
import pandas as pd
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import urllib.parse
import numpy as np
from functools import lru_cache
import concurrent.futures
from difflib import SequenceMatcher
import os
import stat
import pickle

def check_file_access(file_path):
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return False, "File does not exist"
            
        # Check file permissions
        file_stat = os.stat(file_path)
        if not (file_stat.st_mode & stat.S_IRUSR):
            return False, "File is not readable"
            
        # Check file size
        if os.path.getsize(file_path) == 0:
            return False, "File is empty"
            
        return True, "File is accessible"
    except Exception as e:
        return False, f"Error checking file: {str(e)}"

def safe_load_data(filename):
    try:
        file_path = find_data_file(filename)
        if file_path is None:
            return None
            
        # Try to load the file
        try:
            data = joblib.load(file_path)
            return data
        except Exception as e1:
            try:
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                return data
            except Exception as e2:
                try:
                    data = np.load(file_path, allow_pickle=True)
                    return data
                except Exception as e3:
                    st.error(f"Failed to load {filename}")
                    return None
                    
    except Exception as e:
        st.error(f"Error with {filename}")
        return None

def find_data_file(filename):
    # Possible locations where the file might be
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename),
        os.path.join(os.getcwd(), filename),
        os.path.join('/mount/src/movie-recommendation', filename),
        filename
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

# Load data files with error handling
try:
    # Load the files
    movies = safe_load_data('movies.pkl')
    movie_list = safe_load_data('movie_list.pkl')
    similarity = safe_load_data('similarity.pkl')

    if movies is None or movie_list is None or similarity is None:
        st.error("Failed to load required data files. Please check the data files.")
        st.stop()
except Exception as e:
    st.error("Error loading data files")
    st.stop()

# Initialize session state for loading
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False
if 'recommended_movies' not in st.session_state:
    st.session_state.recommended_movies = None

# Enhanced Custom CSS for modern UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    .main {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        font-family: 'Poppins', sans-serif;
        color: #ffffff;
    }

    .stButton>button {
        background-color: rgba(255, 255, 255, 0.1);
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 12px;
        font-weight: 500;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9em;
        backdrop-filter: blur(5px);
    }

    .stButton>button:hover {
        border-color: cyan;
        box-shadow: 0 0 15px rgba(0, 219, 222, 0.2);
        color: white !important;
    }

    .stButton>button:active {
        border-color: cyan;
        box-shadow: 0 0 15px rgba(0, 219, 222, 0.2);
        color: white !important;
        background-color: rgba(255, 255, 255, 0.1);
        transform: scale(0.98);
    }

    .stButton>button:focus {
        color: white !important;
        border-color: cyan !important;
        box-shadow: 0 0 15px rgba(0, 219, 222, 0.2) !important;
    }

    .stButton>button:focus:not(:focus-visible) {
        color: white !important;
        border-color: cyan !important;
        box-shadow: 0 0 15px rgba(0, 219, 222, 0.2) !important;
    }

    .stSelectbox {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 15px;
        padding: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        backdrop-filter: blur(5px);
    }

    .stSelectbox:hover {
        border-color: cyan;
        box-shadow: 0 0 15px rgba(0, 219, 222, 0.2);
    }

    .movie-title {
        font-size: 1.8em;
        font-weight: 600;
        margin: 15px 0;
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }

    .movie-title:after {
        content: '';
        position: absolute;
        width: 100%;
        height: 2px;
        bottom: -5px;
        left: 0;
        background: linear-gradient(90deg, transparent, #00dbde, transparent);
        transition: all 0.3s ease;
    }

    .movie-title:hover:after {
        height: 3px;
        background: linear-gradient(90deg, transparent, #fc00ff, transparent);
    }

    .header {
        color: #ffffff;
        text-align: center;
        font-size: 3.5em;
        margin-bottom: 40px;
        text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.5);
        animation: fadeInDown 1s ease;
        font-weight: 700;
        letter-spacing: 2px;
        position: relative;
    }

    .header:after {
        content: '';
        position: absolute;
        width: 200px;
        height: 3px;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(90deg, transparent, #00dbde, #fc00ff, transparent);
    }

    .stImage {
        border-radius: 15px;
        transition: all 0.4s ease;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        overflow: hidden;
        position: relative;
        width: 500px;
        height: auto;
        margin: 0 auto;
    }

    .stImage img {
        width: 150% !important;
        height: auto !important;
        object-fit: cover;
        border-radius: 15px;
    }

    .stImage:before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 150%;
        height: 100%;
        background: linear-gradient(45deg, rgba(0,219,222,0.1), rgba(252,0,255,0.1));
        opacity: 0;
        transition: all 0.3s ease;
    }

    .stImage:hover:before {
        opacity: 1;
    }

    .stImage:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 30px rgba(0, 219, 222, 0.4);
    }

    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .recommendations-title {
        color: #ffffff;
        text-align: center;
        font-size: 2.6em;
        margin: 40px 0;
        animation: fadeIn 1s ease;
        font-weight: 600;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        position: relative;
    }

    .recommendations-title:after {
        content: '';
        position: absolute;
        width: 150px;
        height: 2px;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(90deg, transparent, #00dbde, transparent);
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #00dbde, #fc00ff);
        border-radius: 10px;
    }

    .stSpinner > div {
        border-top-color: #00dbde !important;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 30px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        margin: 20px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(5px);
        animation: fadeIn 0.5s ease;
    }

    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 4px solid rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        border-top-color: #00dbde;
        animation: spin 1s linear infinite;
        margin: 20px;
    }

    .loading-text {
        color: #ffffff;
        font-size: 1.1em;
        text-align: center;
        font-weight: 500;
        letter-spacing: 1px;
    }

    .recommendations-container {
        animation: slideUp 0.5s ease;
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .stButton>button:active {
        transform: scale(0.98);
        box-shadow: 0 0 15px rgba(0, 219, 222, 0.3);
        background-color: rgba(0, 219, 222, 0.2);
        transition: all 0.2s ease;
    }

    .movie-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 20px;
        margin: 0 0 30px 0;
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(5px);
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 219, 222, 0.3);
        border-color: rgba(0, 219, 222, 0.3);
    }

    .genre-tag {
        display: inline-block;
        background: rgba(0, 219, 222, 0.2);
        color: #ffffff;
        padding: 5px 12px;
        border-radius: 20px;
        margin: 5px 5px 5px 0;
        font-size: 0.85em;
        border: 1px solid rgba(0, 219, 222, 0.3);
    }

    .movie-info {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1em;
        margin: 8px 0;
    }

    .movie-overview {
        color: rgba(255, 255, 255, 0.8);
        line-height: 1.6;
        margin: 15px 0;
    }

    .action-button {
        background: linear-gradient(45deg, teal, darkcyan);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 25px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 184, 169, 0.3);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.85em;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }

    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 184, 169, 0.4);
    }

    .action-button:after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transition: all 0.3s ease;
    }

    .action-button:hover:after {
        transform: translateX(100%);
    }

    .movie-trivia {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(5px);
    }

    .cast-member {
        text-align: center;
        transition: all 0.3s ease;
    }

    .cast-member:hover {
        transform: translateY(-5px);
    }

    .cast-member img {
        border-radius: 50%;
        box-shadow: 0 4px 15px rgba(0, 219, 222, 0.3);
        transition: all 0.3s ease;
    }

    .cast-member:hover img {
        box-shadow: 0 6px 20px rgba(0, 219, 222, 0.4);
    }

    div[data-testid="stMultiSelect"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }

    div[data-testid="stMultiSelect"]:hover {
        border-color: #00dbde;
        box-shadow: 0 0 15px rgba(0, 219, 222, 0.2);
    }

    div[data-testid="stMultiSelect"] > div {
        color: #ffffff;
    }

    div[data-testid="stMultiSelect"] > div > div {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    div[data-testid="stMultiSelect"] > div > div:hover {
        background-color: black;
        border-color: #00dbde;
    }

    div[data-testid="stMultiSelect"] > div > div > div {
        color: #ffffff;
    }

    div[data-testid="stMultiSelect"] > div > div > div:hover {
        background-color: transparent;
    }

    div[data-testid="stMultiSelect"] > div > div > div[aria-selected="true"]:hover {
        background-color: rgba(0, 219, 222, 0.4);
    }

    div[data-testid="stMultiSelect"] > div > div > div[role="option"] {
        padding: 8px 12px;
        transition: all 0.2s ease;
    }

    div[data-testid="stMultiSelect"] > div > div > div[role="option"]:hover {
        transform: translateX(5px);
    }

    div[data-testid="stMultiSelect"] > div > div > div[role="option"]::before {
        content: '🎬';
        margin-right: 8px;
        opacity: 0.7;
    }

    div[data-testid="stMultiSelect"] > div > div > div[aria-selected="true"]::before {
        content: '✅';
        margin-right: 8px;
    }

    div[data-testid="stMultiSelect"] > div > div > div[aria-selected="true"]:hover::before {
        content: '❌';
    }

    div[data-testid="stMultiSelect"] > div > div > div[aria-selected="true"]:hover {
        background-color: rgba(255, 0, 0, 0.2);
    }

    /* Specific styles for different buttons */
    .action-button[style*="background: linear-gradient(45deg, #ff0000, #cc0000)"] {
        background: linear-gradient(45deg, gold, orange) !important;
        box-shadow: 0 4px 15px rgba(248, 197, 55, 0.3) !important;
    }

    .action-button[style*="background: linear-gradient(45deg, #ff0000, #cc0000)"]:hover {
        box-shadow: 0 6px 20px rgba(248, 197, 55, 0.4) !important;
    }

    .action-button[style*="background: linear-gradient(45deg, #1DA1F2, #0d8bd9)"] {
        background: linear-gradient(45deg, royalblue, mediumblue) !important;
        box-shadow: 0 4px 15px rgba(75, 123, 229, 0.3) !important;
    }

    .action-button[style*="background: linear-gradient(45deg, #1DA1F2, #0d8bd9)"]:hover {
        box-shadow: 0 6px 20px rgba(75, 123, 229, 0.4) !important;
    }

    .stContainer {
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
    }

    .stMarkdown {
        margin: 0 !important;
        padding: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Create a movie index dictionary for faster lookups
movie_index = {}

# Cache for movie details
movie_details_cache = {}

def initialize_movie_index():
    global movie_index
    for idx, title in enumerate(movies['title']):
        movie_index[title.lower()] = idx

def fetch_poster(movie_id):
    max_retries = 3
    retry_delay = 1  # seconds
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=retry_delay,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    # Create a session with retry strategy
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
    
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3d05f117126e1e8778d85a868b27b363&language=en-US"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        return None
    except requests.exceptions.RequestException as e:
        st.warning(f"Warning: Could not fetch poster for movie ID {movie_id}. Error: {str(e)}")
        return None

@lru_cache(maxsize=1000)
def fetch_movie_details(movie_id):
    if movie_id in movie_details_cache:
        return movie_details_cache[movie_id]
        
    max_retries = 3
    retry_delay = 1  # seconds
    
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=retry_delay,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
    
    try:
        # Fetch movie details, credits, and videos in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Create URLs
            movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3d05f117126e1e8778d85a868b27b363&language=en-US"
            credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key=3d05f117126e1e8778d85a868b27b363"
            videos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=3d05f117126e1e8778d85a868b27b363&language=en-US"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Submit all requests
            future_movie = executor.submit(session.get, movie_url, headers=headers, timeout=10)
            future_credits = executor.submit(session.get, credits_url, headers=headers, timeout=10)
            future_videos = executor.submit(session.get, videos_url, headers=headers, timeout=10)
            
            # Get responses
            movie_response = future_movie.result()
            credits_response = future_credits.result()
            videos_response = future_videos.result()
            
            movie_response.raise_for_status()
            credits_response.raise_for_status()
            videos_response.raise_for_status()
            
            data = movie_response.json()
            credits_data = credits_response.json()
            videos_data = videos_response.json()

        # Format budget and revenue
        budget = data.get('budget', 0)
        revenue = data.get('revenue', 0)
        formatted_budget = f"${budget:,}" if budget > 0 else "Not available"
        formatted_revenue = f"${revenue:,}" if revenue > 0 else "Not available"

        # Find the best trailer
        trailer_key = None
        if 'results' in videos_data:
            for video in videos_data['results']:
                if video['type'] == 'Trailer' and video['site'] == 'YouTube' and video.get('official', False):
                    trailer_key = video['key']
                    break
            
            if not trailer_key:
                for video in videos_data['results']:
                    if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                        trailer_key = video['key']
                        break

        # Get main cast (first 3)
        main_cast = []
        if 'cast' in credits_data:
            for actor in credits_data['cast'][:3]:
                main_cast.append({
                    'name': actor['name'],
                    'character': actor['character'],
                    'profile_path': f"https://image.tmdb.org/t/p/w200/{actor['profile_path']}" if actor.get('profile_path') else None
                })

        result = {
            'poster': "https://image.tmdb.org/t/p/w500/" + data['poster_path'] if data.get('poster_path') else None,
            'overview': data.get('overview', 'No description available'),
            'release_date': data.get('release_date', 'N/A'),
            'vote_average': data.get('vote_average', 'N/A'),
            'tmdb_url': f"https://www.themoviedb.org/movie/{movie_id}",
            'trailer_key': trailer_key,
            'budget': formatted_budget,
            'revenue': formatted_revenue,
            'runtime': f"{data.get('runtime', 0)} minutes" if data.get('runtime') else "Not available",
            'genres': [genre['name'] for genre in data.get('genres', [])],
            'main_cast': main_cast
        }
        
        # Cache the result
        movie_details_cache[movie_id] = result
        return result
        
    except requests.exceptions.RequestException as e:
        st.warning(f"Warning: Could not fetch details for movie ID {movie_id}. Error: {str(e)}")
        return None

def find_movie_index(movie_name):
    movie_name = movie_name.lower().strip()
    
    # First try exact match
    if movie_name in movie_index:
        return movie_index[movie_name]
    
    # If no exact match, find similar titles
    best_match = None
    best_score = 0.8  # Minimum similarity threshold
    
    for title in movie_index.keys():
        # Calculate similarity score
        score = SequenceMatcher(None, movie_name, title).ratio()
        
        # If we find a better match, update
        if score > best_score:
            best_score = score
            best_match = title
    
    if best_match:
        st.info(f"Showing results for '{best_match}' (similar to '{movie_name}')")
        return movie_index[best_match]
    
    return None

def recommend(movie):
    try:
        # Find the movie index using fuzzy matching
        index = find_movie_index(movie)
        if index is None:
            st.error(f"Movie '{movie}' not found in database")
            return []
        
        # First get the searched movie details
        searched_movie = {
            'title': movies.iloc[index].title,
            'poster': fetch_poster(movies.iloc[index].movie_id),
            'overview': movies.iloc[index].overview if 'overview' in movies.columns else 'No description available',
            'release_date': movies.iloc[index].release_date if 'release_date' in movies.columns else 'N/A',
            'vote_average': movies.iloc[index].vote_average if 'vote_average' in movies.columns else 'N/A',
            'tmdb_url': f"https://www.themoviedb.org/movie/{movies.iloc[index].movie_id}",
            'trailer_key': None,  # Will be updated with fetch_movie_details
            'budget': 'Not available',
            'revenue': 'Not available',
            'runtime': 'Not available',
            'genres': [],
            'main_cast': []
        }
        
        # Get full details for the searched movie
        details = fetch_movie_details(movies.iloc[index].movie_id)
        if details:
            searched_movie.update(details)
        
        # Use numpy for faster sorting
        distances = np.array(similarity[index])
        top_indices = np.argsort(distances)[::-1][1:11]  # Get top 10 similar movies
        
        # Fetch movie details in parallel
        recommended_movies = [searched_movie]  # Add searched movie as first result
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_movie = {
                executor.submit(fetch_movie_details, movies.iloc[i].movie_id): i 
                for i in top_indices
            }
            
            for future in concurrent.futures.as_completed(future_to_movie):
                i = future_to_movie[future]
                try:
                    details = future.result()
                    if details:
                        recommended_movies.append({
                            'title': movies.iloc[i].title,
                            'poster': details['poster'],
                            'overview': details['overview'],
                            'release_date': details['release_date'],
                            'vote_average': details['vote_average'],
                            'tmdb_url': details['tmdb_url'],
                            'trailer_key': details['trailer_key'],
                            'budget': details['budget'],
                            'revenue': details['revenue'],
                            'runtime': details['runtime'],
                            'genres': details['genres'],
                            'main_cast': details['main_cast']
                        })
                except Exception as e:
                    st.warning(f"Error fetching details for movie {movies.iloc[i].title}: {str(e)}")

        return recommended_movies
    except Exception as e:
        st.error(f"Error in recommendation: {str(e)}")
        return []

def generate_share_text(movie):
    title = movie.get('title', 'Unknown Movie')
    year = movie.get('release_date', 'N/A')[:4] if movie.get('release_date') else 'N/A'
    rating = movie.get('vote_average', 'N/A')
    overview = movie.get('overview', 'No description available')
    # Truncate overview to 100 characters
    short_overview = overview[:100] + '...' if len(overview) > 100 else overview
    return f"🎬 {title} ({year}) | Rating: {rating}/10\n\n{short_overview}\n\n#MovieRecommendation #Film"

# Main UI
st.markdown('<h1 class="header">🎬 Movie Suggestion System</h1>', unsafe_allow_html=True)

# Container for better layout
with st.container():
    try:
        # Initialize the movie index
        initialize_movie_index()
    except Exception as e:
        st.error(f"Error loading data files: {str(e)}")
        st.stop()

    movie_list = movies['title'].values
    selected_movie = st.selectbox(
        "🎥 Type or select a movie from the dropdown",
        movie_list,
        index=None,
        placeholder="Search Movie..."
    )

    # Add genre filter with enhanced styling
    all_genres = [
        'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 
        'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Mystery', 
        'Romance', 'Science Fiction', 'TV Movie', 'Thriller', 'War', 'Western'
    ]
    
    selected_genres = st.multiselect(
        "🎭 Filter by genres",
        all_genres,
        placeholder="Select Genres...",
        key="genre_filter"
    )

    # Create columns for buttons with enhanced styling
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button('Get Recommendations', key='recommend_button'):
            st.session_state.is_loading = True
            st.session_state.recommended_movies = None
            st.experimental_rerun()

    # Show loading animation if in loading state
    if st.session_state.is_loading:
        st.markdown('''
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">Loading</div>
            </div>
        ''', unsafe_allow_html=True)
        
        if not selected_movie and not selected_genres:
            st.warning("Please select a movie or at least one genre!")
            st.session_state.is_loading = False
            st.stop()
        
        if selected_movie:
            recommended_movies = recommend(selected_movie)
            if recommended_movies:
                if selected_genres:
                    filtered_movies = []
                    for movie in recommended_movies:
                        if movie.get('genres') and any(genre in movie['genres'] for genre in selected_genres):
                            filtered_movies.append(movie)
                    recommended_movies = filtered_movies
                    if not recommended_movies:
                        st.warning("No movies found matching the selected genres!")
                        st.session_state.is_loading = False
                        st.stop()
        else:
            recommended_movies = []
            for i in range(len(movies)):
                movie_id = movies.iloc[i].movie_id
                details = fetch_movie_details(movie_id)
                if details and details.get('genres') and any(genre in details['genres'] for genre in selected_genres):
                    recommended_movies.append({
                        'title': movies.iloc[i].title,
                        'poster': details['poster'],
                        'overview': details['overview'],
                        'release_date': details['release_date'],
                        'vote_average': details['vote_average'],
                        'tmdb_url': details['tmdb_url'],
                        'trailer_key': details['trailer_key'],
                        'budget': details['budget'],
                        'revenue': details['revenue'],
                        'runtime': details['runtime'],
                        'genres': details['genres'],
                        'main_cast': details['main_cast']
                    })
                    if len(recommended_movies) >= 10:
                        break
            
            if not recommended_movies:
                st.warning("No movies found matching the selected genres!")
                st.session_state.is_loading = False
                st.stop()

        st.session_state.recommended_movies = recommended_movies
        st.session_state.is_loading = False
        st.experimental_rerun()

    # Show recommendations if they exist
    if st.session_state.recommended_movies:
        st.markdown('<div class="recommendations-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="recommendations-title">Recommended Movies</h2>', unsafe_allow_html=True)
        
        for movie in st.session_state.recommended_movies:
            with st.container():
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f'''
                        <a href="{movie["tmdb_url"]}" target="_blank">
                            <img src="{movie["poster"]}" style="width:100%; border-radius:15px; transition: all 0.3s ease;">
                        </a>
                    ''', unsafe_allow_html=True)
                    
                with col2:
                    st.markdown(f'''
                        <a href="{movie["tmdb_url"]}" target="_blank" style="text-decoration: none;">
                            <h3 class="movie-title">{movie["title"]}</h3>
                        </a>
                        <p class="movie-info">📅 {movie["release_date"]}</p>
                        <p class="movie-info">⭐ {movie["vote_average"]}/10</p>
                    ''', unsafe_allow_html=True)
                    
                    if movie.get('genres'):
                        genres_html = '<div style="margin: 15px 0;">'
                        for genre in movie['genres']:
                            genres_html += f'<span class="genre-tag">{genre}</span>'
                        genres_html += '</div>'
                        st.markdown(genres_html, unsafe_allow_html=True)
                    
                    st.markdown(f'<p class="movie-overview">{movie["overview"]}</p>', unsafe_allow_html=True)
                    
                    # Movie Trivia Section with enhanced styling
                    with st.expander("🎬 Movie Trivia", expanded=False):
                        st.markdown(f'''
                            <div class="movie-trivia">
                                <p class="movie-info"><strong>💰 Budget:</strong> {movie.get('budget', 'Not available')}</p>
                                <p class="movie-info"><strong>💵 Revenue:</strong> {movie.get('revenue', 'Not available')}</p>
                                <p class="movie-info"><strong>⏱️ Runtime:</strong> {movie.get('runtime', 'Not available')}</p>
                            </div>
                        ''', unsafe_allow_html=True)
                        
                        if movie.get('main_cast'):
                            st.markdown('<p class="movie-info"><strong>🎭 Main Cast:</strong></p>', unsafe_allow_html=True)
                            cast_cols = st.columns(3)
                            for i, actor in enumerate(movie['main_cast']):
                                with cast_cols[i]:
                                    st.markdown('<div class="cast-member">', unsafe_allow_html=True)
                                    if actor['profile_path']:
                                        st.image(actor['profile_path'], width=80)
                                    st.markdown(f'''
                                        <p class="movie-info" style="text-align: center; font-weight: 500;">{actor["name"]}</p>
                                        <p class="movie-info" style="text-align: center; font-size: 0.8em;">as {actor["character"]}</p>
                                    ''', unsafe_allow_html=True)
                                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Create a container for the buttons with enhanced styling
                    button_col1, button_col2, button_col3 = st.columns([1, 1, 1])
                    
                    with button_col1:
                        st.markdown(f'''
                            <a href="{movie["tmdb_url"]}" target="_blank">
                                <button class="action-button">
                                    <span style="font-size: 1.2em;">🎬</span> View on TMDB
                                </button>
                            </a>
                        ''', unsafe_allow_html=True)
                    
                    with button_col2:
                        if movie['trailer_key']:
                            st.markdown(f'''
                                <a href="https://www.youtube.com/watch?v={movie['trailer_key']}" target="_blank">
                                    <button class="action-button" style="background: linear-gradient(45deg, #ff0000, #cc0000);">
                                        <span style="font-size: 1.2em;">▶️</span> Watch Trailer
                                    </button>
                                </a>
                            ''', unsafe_allow_html=True)
                    
                    with button_col3:
                        if movie.get('title'):
                            share_text = generate_share_text(movie)
                            share_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(share_text)}&url={urllib.parse.quote(movie['tmdb_url'])}"
                            st.markdown(f'''
                                <a href="{share_url}" target="_blank">
                                    <button class="action-button" style="background: linear-gradient(45deg, #1DA1F2, #0d8bd9);">
                                        <span style="font-size: 1.2em;">𝕏</span> Share
                                    </button>
                                </a>
                            ''', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")