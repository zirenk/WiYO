import subprocess
import os

def check_repo():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("No Github token found in environment")
        return
        
    try:
        # Configure git with token
        subprocess.run(['git', 'config', '--global', 'url."https://x-access-token:' + token + '@github.com/".insteadOf', 'https://github.com/'], check=True)
        
        # Try pushing
        result = subprocess.run(['git', 'push', '-f', 'origin', 'main'], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_repo()
