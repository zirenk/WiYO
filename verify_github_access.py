import os
import requests

def verify_github_access():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("GitHub token not found")
        return False
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Test API access
    response = requests.get('https://api.github.com/user', headers=headers)
    if response.status_code != 200:
        print(f"Failed to authenticate with GitHub API: {response.status_code}")
        print("Please ensure the token has the correct permissions")
        return False
        
    # Test repository access
    repo_url = 'https://api.github.com/repos/zirenk/WiYO'
    response = requests.get(repo_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to access repository: {response.status_code}")
        print("Please ensure the token has access to the repository")
        return False
        
    print("GitHub access verification successful!")
    return True

if __name__ == "__main__":
    verify_github_access()
