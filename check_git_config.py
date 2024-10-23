import subprocess
import os

def check_git_config():
    try:
        # Check git config
        print("Checking Git configuration...")
        subprocess.run(['git', 'config', '--list'], check=True)
        
        # Check remote URL
        print("\nChecking remote URL...")
        subprocess.run(['git', 'remote', '-v'], check=True)
        
        # Check repository status
        print("\nChecking repository status...")
        subprocess.run(['git', 'status'], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error during Git check: {e}")
        return False

if __name__ == "__main__":
    check_git_config()
