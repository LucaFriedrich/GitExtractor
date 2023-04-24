import requests
import pyperclip
import json
import re
import os
from tqdm import tqdm

def read_api_key_from_file(filename="gitaccesstoken.txt"):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return file.read().strip()
    return None

def extract_username_and_repo(repo_url):
    match = re.match(r'https?://github\.com/([^/]+)/([^/]+)', repo_url)
    if match:
        return match.group(1), match.group(2)
    else:
        return None, None

def get_all_files(repo_url, extension, api_key=None):
    headers = {'Authorization': f'token {api_key}'} if api_key else {}
    api_url = f'https://api.github.com/repos/{repo_url}/git/trees/main?recursive=1'

    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print("Error retrieving the repository - NOT 200")
        return None

    repo_data = json.loads(response.text)
    files = [file for file in repo_data['tree'] if file['path'].endswith(extension)]

    return files

def copy_files_to_clipboard(repo_url, extension, api_key=None):
    files = get_all_files(repo_url, extension, api_key)
    all_content = []

    if files is None:
        return

    for file in tqdm(files, desc="Copy Files", unit="File"):
        file_content = get_file_contents(repo_url, file['path'], api_key)
        if file_content:
            all_content.append(f"{'#' * 80}\n# {file['path']}\n{'#' * 80}\n\n{file_content}\n\n")

    if all_content:
        pyperclip.copy("\n".join(all_content))
        print(f"\n Content of all {extension}-files from this repo has been copied to your clipboard")
    else:
        print(f"\nNo {extension}-Files found")

def get_file_contents(repo_url, file_path, api_key=None):
    headers = {'Authorization': f'token {api_key}'} if api_key else {}
    api_url = f'https://api.github.com/repos/{repo_url}/contents/{file_path}'

    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print("Error retrieving the file")
        return

    file_data = json.loads(response.text)
    content = requests.get(file_data['download_url']).text

    return content

def select_language():
    languages = {
        "1": ".py",
        "2": ".java",
        "3": ".cs"
    }

    print("Choose language:")
    print("1. Python")
    print("2. Java")
    print("3. C#")
    choice = input("Select: ")

    return languages.get(choice, None)

if __name__ == "__main__":
        repo_url = input("Enter Full Repository URL:")
        username, repo = extract_username_and_repo(repo_url)
        if username is None or repo is None:
            print("Invalid Repository URL")
        else:
            repo_url = f"{username}/{repo}"
            api_key = read_api_key_from_file()
            if not api_key:
                api_key = input("Enter your GitHub Personal Access Token or press 'Enter' to continue without: ")
            else:
                print("API-Key has automatically been read from 'gitaccesstoken.txt'")
            extension = select_language()
            if extension:
                copy_files_to_clipboard(repo_url, extension, api_key)

