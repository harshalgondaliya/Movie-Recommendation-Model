import pickle
import joblib
import os

def convert_file(file_path):
    try:
        # Load the pickle file
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        # Save as joblib
        joblib.dump(data, file_path)
        print(f"Successfully converted {file_path}")
    except Exception as e:
        print(f"Error converting {file_path}: {str(e)}")

# Convert all pickle files
files_to_convert = ['movies.pkl', 'movie_list.pkl', 'similarity.pkl']

for file in files_to_convert:
    if os.path.exists(file):
        convert_file(file)
    else:
        print(f"File {file} not found") 