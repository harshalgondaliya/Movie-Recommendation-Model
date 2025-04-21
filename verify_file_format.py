import os
import pickle
import joblib
import numpy as np
import pandas as pd

def verify_file(file_path):
    print(f"\nVerifying {file_path}")
    if not os.path.exists(file_path):
        print("File does not exist")
        return False
        
    # Get file size
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size} bytes")
    
    # Try to read as binary first
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        print("Successfully read as binary")
    except Exception as e:
        print(f"Error reading as binary: {str(e)}")
        return False
        
    # Try different loading methods
    methods = {
        'joblib': lambda: joblib.load(file_path),
        'pickle': lambda: pickle.load(open(file_path, 'rb')),
        'numpy': lambda: np.load(file_path, allow_pickle=True)
    }
    
    for method_name, load_func in methods.items():
        try:
            data = load_func()
            print(f"Successfully loaded with {method_name}")
            print(f"Data type: {type(data)}")
            if isinstance(data, (pd.DataFrame, np.ndarray)):
                print(f"Shape: {data.shape}")
            return True
        except Exception as e:
            print(f"Failed to load with {method_name}: {str(e)}")
            
    return False

def fix_file_format(file_path):
    try:
        # First try to load with pickle
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
            
        # Save with joblib
        joblib.dump(data, file_path)
        print(f"Successfully converted {file_path} to joblib format")
        return True
    except Exception as e:
        print(f"Error converting {file_path}: {str(e)}")
        return False

def main():
    files_to_check = ['movies.pkl', 'movie_list.pkl', 'similarity.pkl']
    base_dir = '/mount/src/movie-recommendation'
    
    for file in files_to_check:
        file_path = os.path.join(base_dir, file)
        if not verify_file(file_path):
            print(f"\nAttempting to fix {file_path}")
            if fix_file_format(file_path):
                print("Successfully fixed file format")
            else:
                print("Failed to fix file format")

if __name__ == "__main__":
    main() 