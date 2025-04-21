import os
import sys

def verify_files():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Current directory: {current_dir}")
    
    # List of required files
    required_files = ['movies.pkl', 'movie_list.pkl', 'similarity.pkl', 'app.py']
    
    # Check each file
    for file in required_files:
        file_path = os.path.join(current_dir, file)
        exists = os.path.exists(file_path)
        size = os.path.getsize(file_path) if exists else 0
        print(f"{file}: {'Exists' if exists else 'Missing'}, Size: {size} bytes")

if __name__ == "__main__":
    verify_files() 