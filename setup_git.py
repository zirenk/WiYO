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
            
        # Configure the remote URL with the token directly in URL
        remote_url = f'https://{token}@github.com/zirenk/WiYO.git'
        
        # Try to remove existing remote if it exists
        try:
            subprocess.run(['git', 'remote', 'remove', 'origin'], check=True)
        except:
            pass
            
        # Add new remote and push
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url], check=True)
        subprocess.run(['git', 'push', '-f', 'origin', 'main'], check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during Git setup: {e}")
        return False

if __name__ == "__main__":
    setup_git()
