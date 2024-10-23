import subprocess
import os
import sys

def push_to_github():
    try:
        # Ensure we have the token
        token = os.environ.get('GITHUB_TOKEN')
        if not token:
            print("GitHub token not found")
            return False

        # Configure git with specified user info
        subprocess.run(['git', 'config', '--global', 'user.name', 'WiYO App'], check=True)
        subprocess.run(['git', 'config', '--global', 'user.email', 'app@wiyo.example.com'], check=True)
        
        # Initialize repository if it doesn't exist
        if not os.path.exists('.git'):
            subprocess.run(['git', 'init'], check=True)

        # Add all files
        subprocess.run(['git', 'add', '-A'], check=True)

        # Commit changes with specified message
        try:
            subprocess.run(['git', 'commit', '-m', 'Update WiYO application'], check=True)
        except subprocess.CalledProcessError:
            print("No changes to commit")
            pass

        # Set remote URL with token using the oauth2 format
        remote_url = f'https://oauth2:{token}@github.com/zirenk/WiYO.git'
        
        # Try to remove existing remote if it exists
        try:
            subprocess.run(['git', 'remote', 'remove', 'origin'], check=True)
        except subprocess.CalledProcessError:
            pass

        # Add new remote
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url], check=True)

        # Set main branch if not exists
        try:
            subprocess.run(['git', 'checkout', '-b', 'main'], check=True)
        except subprocess.CalledProcessError:
            # Branch already exists, just switch to it
            subprocess.run(['git', 'checkout', 'main'], check=True)

        # Force push to main branch with verbose output
        result = subprocess.run(['git', 'push', '-v', '-f', 'origin', 'main'], 
                              capture_output=True, 
                              text=True)
        if result.returncode != 0:
            print(f"Push failed with error: {result.stderr}")
            return False
            
        print("Successfully pushed to GitHub!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error during Git operations: {e}")
        if hasattr(e, 'stderr'):
            print(f"Error details: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    push_to_github()
