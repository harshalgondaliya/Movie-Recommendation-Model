# Movie-Recommendation

# 🎬 Movie Recommender System

A modern, interactive movie recommendation system built with Streamlit and powered by TMDB dataset. This application helps users discover new movies based on their preferences and selected genres.

## ⚠️ Important: Essential Project File
The similarity matrix file (`similarity.pkl`, ~176MB) is **ESSENTIAL** for this project to function properly. Without this file, the movie recommendation system will not work. Please follow these steps to set up the model:

1. Download `similarity.pkl` from [Google Drive](https://drive.google.com/file/d/1x5BKOKwmlP1Ysh10vl8oIHXqx0msO8p4/view?usp=drive_link)
2. Place the downloaded file in the root directory of the project
3. Make sure the file is named exactly as `similarity.pkl`

![Movie Recommender System](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![TMDB](https://img.shields.io/badge/TMDB-01D277?style=for-the-badge&logo=themoviedatabase&logoColor=white)

## ✨ Features

- **Smart Movie Recommendations**: Get personalized movie suggestions based on your selected movie or preferred genres
- **Modern UI**: Beautiful, responsive interface with smooth animations and transitions
- **Detailed Movie Information**: View comprehensive details including:
  - Movie posters and trailers
  - Release dates and ratings
  - Budget and revenue information
  - Cast and crew details
  - Genre tags
  - Movie overviews
- **Genre Filtering**: Filter recommendations by specific genres
- **Social Sharing**: Share movie recommendations on social media
- **Interactive Elements**: 
  - Smooth loading animations
  - Hover effects on movie cards
  - Dynamic genre tags
  - Responsive design

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Download the project files
2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## 🎥 How to Use

1. **Select a Movie**:
   - Choose a movie from the dropdown menu or type to search
   - The system will find similar movies based on your selection

2. **Filter by Genre** (Optional):
   - Select one or more genres to refine your recommendations
   - The system will show movies matching your selected genres

3. **Get Recommendations**:
   - Click the "Get Recommendations" button
   - Wait for the system to process and display your personalized recommendations

4. **Explore Movie Details**:
   - View movie posters and information
   - Click on movie titles to visit their TMDB pages
   - Watch trailers directly from the app
   - Share your favorite recommendations on social media

## 🛠️ Technical Details

### Data Source
- Movie data from The Movie Database (TMDB)
- Pre-processed similarity matrix for efficient recommendations

### Key Components
- **Recommendation Engine**: Uses content-based filtering with cosine similarity
- **API Integration**: Fetches real-time movie data from TMDB API
- **Caching System**: Implements caching for better performance
- **Error Handling**: Robust error handling and retry mechanisms

### Technologies Used
- Streamlit for the web interface
- Python for backend processing
- TMDB API for movie data
- CSS for custom styling and animations
- Concurrent processing for efficient data fetching

## 📊 Performance Optimizations

- Implemented caching for movie details
- Parallel processing for API requests
- Efficient similarity calculations
- Lazy loading of movie data
- Optimized image loading

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- The Movie Database (TMDB) for providing the movie data
- Streamlit team for the amazing framework
- All contributors who have helped improve this project

## 📞 Support

If you encounter any issues or have suggestions, please contact the project maintainer.

## Data Files
This project uses several pickle files for storing movie data and similarity matrices:

1. `movie_list.pkl`: Contains the list of movies
2. `movies.pkl`: Contains movie details and metadata
3. `similarity.pkl`: Contains the similarity matrix for movie recommendations

To generate these files, run:
```python
python data_preprocessing.py
```

Note: Make sure you have the required movie dataset before running the preprocessing script.

---

Made with ❤️ by [Your Name]
