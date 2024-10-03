import requests
import os
import time
import git
import shutil

source_token = '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'  # Replace with your actual token, consider using environment variables
source_user = 'navdeep03'
target_token = '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'  # Replace with a secure method to store your token
target_user = 'krishnavagu'

def fetch_repositories():
    """Fetch repositories from the source GitHub user."""
    url = f'https://api.github.com/users/{source_user}/repos'
    headers = {'Authorization': f'token {source_token}'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # Returns a list of repositories
    else:
        print(f"Error fetching repositories: {response.status_code} - {response.json()}")
        return []

def create_repository(repo):
    """Create a repository in the target GitHub user account."""
    url = f'https://api.github.com/user/repos'
    headers = {'Authorization': f'token {target_token}'}
    data = {
        'name': repo['name'],
        'private': repo['private'],
        'description': repo.get('description', ''),
    }

    # Check if the repository already exists in the target
    existing_repos_response = requests.get(f'https://api.github.com/users/{target_user}/repos', headers=headers)

    if existing_repos_response.status_code == 200:
        existing_repo_names = [r['name'] for r in existing_repos_response.json()]
        print(f"Existing repositories in target: {existing_repo_names}")  # Debug statement
    else:
        print(f"Error fetching existing repositories: {existing_repos_response.status_code} - {existing_repos_response.json()}")
        return None  # Exit if there's an error

    if repo['name'] in existing_repo_names:
        print(f"Repository '{repo['name']}' already exists. Skipping.")
        return None

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print(f"Repository created: '{repo['name']}'")
        return response.json()  # Returns the created repository details
    else:
        print(f"Error creating repository '{repo['name']}': {response.status_code} - {response.json()}")
        return None

def clone_and_push(repo):
    """Clone the repository from the source and push it to the target."""
    source_repo_url = f'https://github.com/{source_user}/{repo["name"]}.git'
    target_repo_url = f'https://{target_user}:{target_token}@github.com/{target_user}/{repo["name"]}.git'

    try:
        # Clone the repository
        print(f"Cloning '{source_repo_url}'...")
        local_repo_path = f"./{repo['name']}"

        # Remove existing local repo if it exists
        if os.path.exists(local_repo_path):
            print(f"Removing existing local repository at '{local_repo_path}'...")
            shutil.rmtree(local_repo_path)

        # Clone the source repository
        git.Repo.clone_from(source_repo_url, local_repo_path)
        
        # Push to the target repository
        local_repo = git.Repo(local_repo_path)
        local_repo.git.remote('add', 'target', target_repo_url)

        # Determine default branch
        default_branch = 'master'  # Change this if necessary
        branches = local_repo.git.branch('-r').split()
        if 'origin/main' in branches:
            default_branch = 'main'

        local_repo.git.push('target', default_branch)

        print(f"Successfully pushed '{repo['name']}' to the target.")
    except Exception as e:
        print(f"Failed to clone and push repository '{repo['name']}': {e}")

# Main migration process
def migrate_repositories():
    repos = fetch_repositories()

    for repo in repos:
        created_repo = create_repository(repo)
        if created_repo:
            clone_and_push(repo)  # Call the clone and push function for each created repository
        time.sleep(1)  # Pause to avoid hitting rate limits

if __name__ == "__main__":
    if not source_token or not target_token:
        print("Error: Source or target GitHub token not set.")
    else:
        migrate_repositories()
