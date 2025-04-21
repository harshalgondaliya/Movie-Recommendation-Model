import os
import stat

def fix_file_permissions(file_path):
    try:
        # Set read permissions for all users
        os.chmod(file_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        print(f"Fixed permissions for {file_path}")
        return True
    except Exception as e:
        print(f"Error fixing permissions for {file_path}: {str(e)}")
        return False

def main():
    # Files to fix
    files_to_fix = ['movies.pkl', 'movie_list.pkl', 'similarity.pkl']
    
    # Try different possible locations
    possible_dirs = [
        os.path.dirname(os.path.abspath(__file__)),
        os.getcwd(),
        '/mount/src/movie-recommendation'
    ]
    
    for dir_path in possible_dirs:
        print(f"\nChecking directory: {dir_path}")
        if not os.path.exists(dir_path):
            print("Directory does not exist")
            continue
            
        for file in files_to_fix:
            file_path = os.path.join(dir_path, file)
            if os.path.exists(file_path):
                print(f"\nFound {file} at {file_path}")
                print(f"Current permissions: {oct(os.stat(file_path).st_mode)[-3:]}")
                if fix_file_permissions(file_path):
                    print(f"New permissions: {oct(os.stat(file_path).st_mode)[-3:]}")
                else:
                    print("Failed to fix permissions")

if __name__ == "__main__":
    main() 