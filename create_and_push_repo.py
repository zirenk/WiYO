import os
import subprocess
import requests
import json

def create_and_push_repo():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("GitHub token not found")
        return False
        
    # Create repository using GitHub API
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # First check if repo exists
    repo_url = 'https://api.github.com/repos/zirenk/WiYO'
    response = requests.get(repo_url, headers=headers)
    
    if response.status_code == 404:
        # Create new repository
        data = {
            'name': 'WiYO',
            'description': 'Anonymous polling application',
            'private': False
        }
        response = requests.post('https://api.github.com/user/repos', 
                               headers=headers, 
                               data=json.dumps(data))
        
        if response.status_code not in [201, 200]:
            print(f"Failed to create repository: {response.json()}")
            return False
    
    try:
        # Configure git
        subprocess.run(['git', 'config', '--global', 'user.name', 'WiYO App'], check=True)
        subprocess.run(['git', 'config', '--global', 'user.email', 'app@wiyo.example.com'], check=True)
        
        # Initialize if needed
        if not os.path.exists('.git'):
            subprocess.run(['git', 'init'], check=True)
        
        # Add files
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit
        subprocess.run(['git', 'commit', '-m', 'Initial commit of WiYO application'], check=True)
        
        # Set remote with token in URL
        remote_url = f'https://{token}@github.com/zirenk/WiYO.git'
        
        # Remove existing remote if it exists
        try:
            subprocess.run(['git', 'remote', 'remove', 'origin'], check=True)
        except:
            pass
            
        # Add new remote and push
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url], check=True)
        subprocess.run(['git', 'push', '-u', 'origin', 'main', '--force'], check=True)
        
        print("Successfully pushed to GitHub!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operations: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    create_and_push_repo()
