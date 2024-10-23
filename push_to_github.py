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

        # Add all files
        subprocess.run(['git', 'add', '-A'], check=True)

        # Commit changes with specified message
        subprocess.run(['git', 'commit', '-m', 'Update WiYO application'], check=True)

        # Set remote URL with token in the correct format
        remote_url = f'https://{token}@github.com/zirenk/WiYO.git'
        
        # Update remote URL
        try:
            subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url], check=True)
        except:
            # If remote doesn't exist, add it
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url], check=True)

        # Force push to main branch
        subprocess.run(['git', 'push', '-f', 'origin', 'main'], check=True)
        print("Successfully pushed to GitHub!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error during Git operations: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    push_to_github()
