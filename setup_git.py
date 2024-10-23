import subprocess
import os

def setup_git():
    try:
        # Configure git with generic user info since we're using token auth
        subprocess.run(['git', 'config', '--global', 'user.name', 'WiYO App'], check=True)
        subprocess.run(['git', 'config', '--global', 'user.email', 'app@wiyo.example.com'], check=True)
        
        # Set up the token authentication
        token = os.environ.get('GITHUB_TOKEN')
        if not token:
            print("GitHub token not found in environment")
            return False
            
        # Configure the remote URL with the token
        remote_url = f'https://x-access-token:{token}@github.com/zirenk/WiYO.git'
        subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url], check=True)
        
        # Try to push
        subprocess.run(['git', 'push', '-f', 'origin', 'main'], check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during Git setup: {e}")
        return False

if __name__ == "__main__":
    setup_git()
