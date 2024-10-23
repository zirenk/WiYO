import subprocess
import os
import time

def init_and_push():
    try:
        # Configure git
        subprocess.run(['git', 'config', '--global', 'user.name', 'WiYO App'], check=True)
        subprocess.run(['git', 'config', '--global', 'user.email', 'app@wiyo.example.com'], check=True)
        
        # Initialize repository if needed
        if not os.path.exists('.git'):
            subprocess.run(['git', 'init'], check=True)
        
        # Add all files
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', 'Initial commit of WiYO application'], check=True)
        
        # Configure the remote with token directly in URL
        token = os.environ.get('GITHUB_TOKEN')
        if not token:
            print("GitHub token not found")
            return False
            
        remote_url = f'https://{token}@github.com/zirenk/WiYO.git'
        
        # Remove existing remote if it exists
        try:
            subprocess.run(['git', 'remote', 'remove', 'origin'], check=True)
        except:
            pass
            
        # Add new remote
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url], check=True)
        
        # Push to GitHub
        subprocess.run(['git', 'push', '-u', 'origin', 'main', '--force'], check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operations: {e}")
        return False

if __name__ == "__main__":
    init_and_push()
