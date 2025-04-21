import os
import sys

def check_deployment():
    print("=== Deployment Environment Check ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")
    
    # Check deployment-specific directory
    deployment_dir = '/mount/src/movie-recommendation'
    print(f"\nChecking deployment directory: {deployment_dir}")
    if os.path.exists(deployment_dir):
        print("Deployment directory exists")
        print("Contents of deployment directory:")
        for item in os.listdir(deployment_dir):
            print(f"- {item}")
    else:
        print("Deployment directory does not exist")
    
    # Check data files
    print("\nChecking data files:")
    files_to_check = ['movies.pkl', 'movie_list.pkl', 'similarity.pkl', 'app.py']
    for file in files_to_check:
        paths = [
            os.path.join(os.getcwd(), file),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), file),
            os.path.join(deployment_dir, file)
        ]
        found = False
        for path in paths:
            if os.path.exists(path):
                print(f"Found {file} at: {path}")
                print(f"Size: {os.path.getsize(path)} bytes")
                print(f"Permissions: {oct(os.stat(path).st_mode)[-3:]}")
                found = True
                break
        if not found:
            print(f"{file} not found in any location")

if __name__ == "__main__":
    check_deployment() 